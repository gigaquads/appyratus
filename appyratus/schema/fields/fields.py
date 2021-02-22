import operator
import random
import re
import time
import typing
import uuid

from decimal import Decimal, getcontext as get_decimal_context
from copy import deepcopy
from datetime import date, datetime, timedelta
from functools import reduce
from os.path import abspath, expanduser
from typing import Callable, Dict, Text, Type
from uuid import UUID

import bcrypt
import dateutil.parser
import pytz

from faker import Faker

from appyratus.utils.time_utils import TimeUtils
from appyratus.utils.string_utils import StringUtils
from appyratus.utils.dict_utils import DictUtils
from appyratus.enum import Enum as EnumObject

from .field_adapter import FieldAdapter
from .value_generator import ValueGenerator, Bounds

RE_BCRYPT_HASH = re.compile(r'^\$2[ayb]\$.{56}$')
RE_FLOAT = re.compile(r'^-?\d*(\.\d*)?$')
RE_EMAIL = re.compile(r'^[a-z][\w\-\.]*@[\w\.\-]*\w\.\w+$', re.I)
RE_UUID = re.compile(r'^[a-f0-9]{32}$')

UNRECOGNIZED_VALUE = 'unrecognized'
INVALID_VALUE = 'invalid'


class Field(object):

    # convenient references to friend classes
    Adapter = FieldAdapter
    Generator = ValueGenerator
    Bounds = Bounds

    faker = Faker()
    generator = ValueGenerator()
    np_dtype = 'O'

    def __init__(
        self,
        source: Text = None,
        name: Text = None,
        required: bool = False,
        nullable: bool = None,
        default: object = None,
        meta: typing.Dict = None,
        scalar: bool = True,
        np_dtype = 'object',
        on_create: object = None,
        before: object = None,
        after: object = None,
        on_generate: Callable = None,
        **kwargs,
    ):
        """
        # Kwargs
        - `source`: key in source data if different from declared field name.
        - `name`: name of the field as declared on the host Schema class.
        - `required`: key must exist in source data if set.
        - `np_dtype`: numpy dtype name
        - `nullable`: if key exists, it can be None/null if this is set.
        - `default`: a constant or callable the returns a default value.
        - `on_create`: generic method to run upon init of host schema class.
        - `after`: generic method to run after fields are processed.
        - `meta`: additional data storage
        """
        self.name = name
        self.source = source or name
        self.required = required
        self.nullable = nullable
        self.default = default
        self.scalar = scalar
        self.on_create = on_create
        self.before = before or self.before
        self.after = after or self.after
        self.on_generate = on_generate or self.on_generate
        self.meta = meta or {}
        self.meta.update(kwargs)
        self.schema = None
        self._has_constant_default = (
            default is not None and not callable(default)
        )

        if np_dtype:
            self.np_dtype = np_dtype
        # otherwise, default to np_dtype class attr

    def __repr__(self):
        info_str = ''
        if self.source or not self.name:
            info_str = self.source
        elif self.source != self.name:
            info_str += ' -> ' + self.name
        return f'{self.__class__.__name__}({info_str})'

    def copy(self):
        field_type = type(self)
        return field_type(
            name=self.name,
            source=self.source,
            required=self.required,
            default=self.default,
            scalar=self.scalar,
            on_create=self.on_create,
            before=self.before,
            after=self.after,
            meta=self.meta,
        )

    def process(self, value):
        return (value, None)

    def generate(self, *args, **kwargs):
        return self.generator.generate(self, *args, **kwargs)

    @property
    def has_constant_default(self):
        return self._has_constant_default

    @classmethod
    def adapt(cls, on_adapt, **kwargs) -> FieldAdapter:
        return cls.Adapter(cls, on_adapt, **kwargs)

    @staticmethod
    def before(field, value, context: dict = None):
        """
        This method is *intentionally* shadowed by the ctor keyword argument
        with the same name. This stub is just for declaring the expected
        interface.
        """
        return (value, None)

    @staticmethod
    def after(field, value, dest: dict, context=None):
        """
        This method is *intentionally* shadowed by the ctor keyword argument
        with the same name. This stub is just for declaring the expected
        interface.
        """
        return (value, None)

    def on_generate(self, **kwargs):
        p = random.randint(0, 10)

        if p < 1:
            delegate = Bool()
        elif p < 4:
            delegate = String()
        elif p < 6:
            delegate = Int()
        elif p < 7:
            delegate = Float()
        else:
            delegate = Dict()

        return delegate.on_generate()

    def on_generate_range(self, bounds: 'Bounds' = None, **kwargs):
        raise NotImplementedError('override in subclass')


class Enum(Field):
    def __init__(self, nested: Field, values, **kwargs):
        self.nested = nested
        self.values = set(values)

        if 'default' not in kwargs and isinstance(values, EnumObject):
            kwargs['default'] = values.default

        super().__init__(**kwargs)

        self.np_dtype = nested.np_dtype

    def process(self, value):
        if value is None and self.nullable:
            return (value, None)
        nested_value, error = self.nested.process(value)
        if error:
            return (None, error)
        elif nested_value not in self.values:
            return (None, UNRECOGNIZED_VALUE)
        else:
            return (nested_value, None)

    def on_generate(self, **kwargs):
        return random.choice(list(self.values))


class String(Field):
    np_dtype = '<U1'

    generator = Field.Generator(
        callbacks={
            '_id': lambda f, **kwargs: UuidString.next_id(),
            'id': lambda f, **kwargs: str(f.faker.random_number(digits=16)),
            'public_id': lambda f, **kwargs: UuidString.next_id(),
            'first_name': lambda f, **kwargs: f.faker.first_name(),
            'last_name': lambda f, **kwargs: f.faker.last_name(),
            'full_name': lambda f, **kwargs: f.faker.name(),
            'name': lambda f, **kwargs: f.faker.catch_phrase().title(),
            'description': lambda f, **kwargs: f.faker.paragraph(nb_sentences=10),
            'descr': lambda f, **kwargs: f.faker.paragraph(nb_sentences=10),
            'summary': lambda f, **kwargs: f.faker.paragraph(nb_sentences=6),
            'comment': lambda f, **kwargs: f.faker.paragraph(nb_sentences=4),
            'city': lambda f, **kwargs: f.faker.city(),
            'address': lambda f, **kwargs: f.faker.address(),
            'phone': lambda f, **kwargs: f.faker.phone_number(),
            'phone_number': lambda f, **kwargs: f.faker.phone_number(),
            'mobile': lambda f, **kwargs: f.faker.phone_number(),
            'zip': lambda f, **kwargs: f.faker.zipcode(),
            'zip_code': lambda f, **kwargs: f.faker.zipcode(),
            'zipcode': lambda f, **kwargs: f.faker.zipcode(),
            'postal_code': lambda f, **kwargs: f.faker.zipcode(),
            'postalcode': lambda f, **kwargs: f.faker.zipcode(),
            'year': lambda f, **kwargs: f.faker.year(),
            'user_name': lambda f, **kwargs: f.faker.user_name(),
            'username': lambda f, **kwargs: f.faker.user_name(),
            'nick': lambda f, **kwargs: f.faker.user_name(),
            'handle': lambda f, **kwargs: f.faker.user_name(),
            'screen_name': lambda f, **kwargs: f.faker.user_name(),
            'screenname': lambda f, **kwargs: f.faker.user_name(),
            'state_code': lambda f, **kwargs: f.faker.state_abbr(),
            'state': lambda f, **kwargs: f.faker.state(),
            'country_code': lambda f, **kwargs: f.faker.country_code(),
            'country': lambda f, **kwargs: f.faker.country(),
            'card_number': lambda f, **kwargs: f.faker.credit_card_number(),
            'credit_card_number': lambda f, **kwargs: f.faker.credit_card_number(),
            'security_code': lambda f, **kwargs: f.faker.credit_card_security_code(),
            'credit_card_security_code': lambda f, **kwargs: f.faker.credit_card_security_code(),
            'label': lambda f, **kwargs: StringUtils.snake(f.faker.color_name()).lower(),
            'color': lambda f, **kwargs: StringUtils.snake(f.faker.color_name()).lower(),
            'currency_code': lambda f, **kwargs: f.faker.currency_code(),
            'currency_name': lambda f, **kwargs: f.faker.currency_name(),
            'ein': lambda f, **kwargs: f.faker.ein(),
            'filename': lambda f, **kwargs: f.faker.ein(),
            'file_name': lambda f, **kwargs: f.faker.ein(),
            'fname': lambda f, **kwargs: f.faker.ein(),
            'filepath': lambda f, **kwargs: f.faker.file_path(),
            'file_path': lambda f, **kwargs: f.faker.file_path(),
            'fpath': lambda f, **kwargs: f.faker.file_path(),
            'file_extension': lambda f, **kwargs: f.faker.file_extension(),
            'extension': lambda f, **kwargs: f.faker.file_extension(),
            'ext': lambda f, **kwargs: f.faker.file_extension(),
            'image_url': lambda f, **kwargs: f.faker.image_url(),
            'url': lambda f, **kwargs: f.faker.url(),
            'host': lambda f, **kwargs: f.faker.hostname(),
            'hostname': lambda f, **kwargs: f.faker.hostname(),
            'host_name': lambda f, **kwargs: f.faker.hostname(),
            'port': lambda f, **kwargs: str(random.randrange(1001, 10000)),
            'ssn': lambda f, **kwargs: f.faker.ssn(),
            'ip_addr': lambda f, **kwargs: f.faker.ipv4(),
            'ip_address': lambda f, **kwargs: f.faker.ipv4(),
            'ip': lambda f, **kwargs: f.faker.ipv4(),
            'ipv4': lambda f, **kwargs: f.faker.ipv4(),
            'ipv6': lambda f, **kwargs: f.faker.ipv6(),
            'langauge_code': lambda f, **kwargs: f.faker.langauge_code(),
            'license_plate': lambda f, **kwargs: f.faker.license_plate(),
            'locale': lambda f, **kwargs: f.faker.locale(),
            'mac_addr': lambda f, **kwargs: f.faker.mac_address(),
            'mac_address': lambda f, **kwargs: f.faker.mac_address(),
            'md5': lambda f, **kwargs: str(f.faker.md5()),
            'mime': lambda f, **kwargs: f.faker.mime_type(),
            'mime_type': lambda f, **kwargs: f.faker.mime_type(),
            'mimetype': lambda f, **kwargs: f.faker.mime_type(),
            'month': lambda f, **kwargs: f.faker.month(),
            'isbn': lambda f, **kwargs: f.faker.isbn(),
            'slug': lambda f, **kwargs: f.faker.slug(),
            'street': lambda f, **kwargs: f.faker.street_name(),
            'street_name': lambda f, **kwargs: f.faker.street_name(),
            'suffix': lambda f, **kwargs: f.faker.suffix(),
            'timezone': lambda f, **kwargs: f.faker.timezone(),
            'time_zone': lambda f, **kwargs: f.faker.timezone(),
            'tz': lambda f, **kwargs: f.faker.timezone(),
            'user_agent': lambda f, **kwargs: f.faker.user_agent(),
            'useragent': lambda f, **kwargs: f.faker.user_agent(),
            'ua': lambda f, **kwargs: f.faker.user_agent(),
            'text': lambda f, **kwargs: f.faker.text(),
            'event': lambda f, **kwargs: f.faker.word(),
            'event_name': lambda f, **kwargs: f.faker.word(),
            'email': lambda f, **kwargs: f.faker.email(),
            'email_addr': lambda f, **kwargs: f.faker.email(),
            'email_address': lambda f, **kwargs: f.faker.email(),
            'message': lambda f, **kwargs: f.faker.text(max_nb_chars=140),
            'keyword': lambda f, **kwargs: f.faker.word().lower(),
            'tag': lambda f, **kwargs: f.faker.word().lower(),
            'headline': lambda f, **kwargs: f.faker.catch_phrase().title(),
            'amount': lambda f, **kwargs: str(random.randrange(0, 51)),
            'count': lambda f, **kwargs: str(random.randrange(0, 51)),
            'angle': lambda f, **kwargs: str(random.randrange(-360, 361)),
            'password': lambda f, **kwargs: f.faker.password(),
        },
    )

    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        elif value is not None:
            return (str(value), None)
        else:
            return (value, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return self.faker.text(max_nb_chars=64)

    def on_generate_range(self, bounds: 'Bounds', **kwargs):
        def vec(text, n):
            padding = n - len(text)
            vec = [ord(c) for c in text]
            if padding:
                vec += [ord('a')] * padding
            return vec

        def midpoint(s1, s2):
            n = max(len(s1), len(s2))
            v1 = vec(s1, n)
            v2 = vec(s2, n)
            return ''.join(
                chr(c) for c in
                    (abs(i1+i2)//2 for i1, i2 in zip(v1, v2))
            )

        def increment(text, incr):
            return text[:-1] + chr(ord(text[-1]) + incr)

        lower = None
        upper = None

        if bounds.lower:
            lower = bounds.lower[:]
            if not bounds.lower_inclusive:
                lower = increment(lower, 1)

        if bounds.upper:
            upper = bounds.upper[:]
            if not bounds.upper_inclusive:
                upper = increment(upper, -1)

        if lower is not None and upper is not None:
            return midpoint(lower, upper)
        elif lower is not None:
            return lower

        assert upper is not None
        return upper


class Bytes(Field):
    np_dtype = 'S1'

    def __init__(self, encoding='utf-8', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoding = encoding

    def process(self, value):
        if isinstance(value, bytes):
            return (value, None)
        if isinstance(value, str):
            return (value.encode(self.encoding), None)
        return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return self.faker.binary(1 << random.randint(5, 8))


class FormatString(String):

    @staticmethod
    def after(field, fstr, data, context=None):
        value = fstr.format(**data)
        return (value, None)


class Int(Field):
    np_dtype = 'int64'

    generator = ValueGenerator(
        callbacks={
            '_id': lambda f, **kwargs: f.faker.random_number(digits=16),
            '_rev': lambda f, **kwargs: f.faker.random_number(digits=3),
            'id': lambda f, **kwargs: f.faker.random_number(digits=16),
            'public_id': lambda f, **kwargs: f.faker.random_number(digits=16),
            'age': lambda f, **kwargs: random.randint(10, 100),
            'rating': lambda f, **kwargs: random.randint(1, 10),
            'width': lambda f, **kwargs: random.randint(0, 100),
            'height': lambda f, **kwargs: random.randint(0, 100),
            'size': lambda f, **kwargs: random.randint(0, 100),
            'depth': lambda f, **kwargs: random.randint(0, 100),
            'angle': lambda f, **kwargs: random.randint(-360, 360),
            'year': lambda f, **kwargs: int(f.faker.year()),
            'month': lambda f, **kwargs: int(f.faker.month()),
            'day': lambda f, **kwargs: int(f.faker.day_of_month()),
            'code': lambda f, **kwargs: random.randint(0, 20),
            'seq': lambda f, **kwargs: random.randint(0, 100),
            'no': lambda f, **kwargs: random.randint(0, 100),
            'num': lambda f, **kwargs: random.randint(0, 100),
            'count': lambda f, **kwargs: random.randint(0, 100),
            'sequence': lambda f, **kwargs: random.randint(0, 1000),
            'index': lambda f, **kwargs: random.randint(0, 1000),
            'idx': lambda f, **kwargs: random.randint(0, 1000),
        },
    )

    def __init__(self, signed=False, **kwargs):
        super().__init__(**kwargs)
        self.signed = signed

    def process(self, value):
        if isinstance(value, str):
            if not value.isdigit():
                return (None, INVALID_VALUE)
            else:
                value = int(value)
        if isinstance(value, int):
            if self.signed and value < 0:
                return (None, INVALID_VALUE)
            else:
                return (value, None)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return random.randint(-10, 100)

    def on_generate_range(self, bounds: 'Bounds' = None, **kwargs):
        while True:
            lower = bounds.lower
            if not bounds.lower_inclusive:
                lower += 1
            upper = bounds.upper
            if not bounds.upper_inclusive:
                upper -= 1
            value = random.randint(lower, upper)
            if (not bounds.exclude) or (value not in bounds.exclude):
                return value


class Uint(Int):
    np_dtype = 'uint64'

    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)

    def on_generate(self, **kwargs):
        return random.randint(0, 100)


class Uint32(Uint):
    np_dtype = 'uint32'

    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)


class Int32(Int):
    np_dtype = 'int32'

    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)


class Uint64(Int):
    np_dtype = 'int64'

    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)


class Float(Field):
    np_dtype = 'float64'

    generator = ValueGenerator(
        callbacks={
            '_id': lambda f, **kwargs: f.faker.random_number(digits=16),
            'public_id': lambda f, **kwargs: f.faker.random_number(digits=16),
            'size': lambda f, **kwargs: 100 * random.random(),
            'price': lambda f, **kwargs: 100 * random.random(),
            'age': lambda f, **kwargs: random.randint(12, 80),
            'width': lambda f, **kwargs: random.randint(0, 100),
            'height': lambda f, **kwargs: random.randint(0, 100),
            'depth': lambda f, **kwargs: random.randint(0, 100),
            'angle': lambda f, **kwargs: random.randint(-360, 360),
            'year': lambda f, **kwargs: int(f.faker.year()),
            'month': lambda f, **kwargs: int(f.faker.month()),
            'day': lambda f, **kwargs: int(f.faker.day_of_month()),
            'code': lambda f, **kwargs: random.randint(0, 20),
            'seq': lambda f, **kwargs: random.randint(0, 100),
            'no': lambda f, **kwargs: random.randint(0, 100),
            'num': lambda f, **kwargs: random.randint(0, 100),
        },
    )

    def process(self, value):
        if isinstance(value, float):
            return (value, None)
        elif isinstance(value, int):
            return (float(value), None)
        elif isinstance(value, str):
            if not RE_FLOAT.match(value):
                return (None, INVALID_VALUE)
            else:
                return (float(value), None)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return random.random() * random.randint(-100, 100)


class Email(String):
    def process(self, value):
        dest, error = super().process(value)
        if error:
            return (dest, error)
        elif not RE_EMAIL.match(value):
            return (None, 'not a valid e-mail address')
        else:
            return (value.lower(), None)

    def on_generate(self, **kwargs):
        return self.faker.email()


class Uuid(Field):
    def process(self, value):
        if isinstance(value, UUID):
            return (value, None)
        elif isinstance(value, str):
            value = value.replace('-', '').lower()
            if not RE_UUID.match(value):
                return (None, INVALID_VALUE)
            else:
                return (UUID(value), None)
        elif isinstance(value, int):
            hex_str = hex(value)[2:]
            uuid_hex = ('0' * (32 - len(hex_str))) + hex_str
            return (UUID(uuid_hex), None)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return self.next_id()

    @classmethod
    def next_id(cls):
        return uuid.uuid4()


class UuidString(String):
    def process(self, value):
        if isinstance(value, UUID):
            return (value.hex, None)
        elif isinstance(value, str):
            value = value.replace('-', '').lower()
            if RE_UUID.match(value):
                return (value, None)
            else:
                return (None, INVALID_VALUE)
        elif isinstance(value, int):
            hex_str = hex(value)[2:]
            uuid_hex = ('0' * (32 - len(hex_str))) + hex_str
            return (uuid_hex, None)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return self.next_id()

    @classmethod
    def next_id(cls):
        return UUID(int=random.getrandbits(128)).hex


class Bool(Field):
    np_dtype = 'bool'
    truthy = {True, 'T', 't', 'TRUE', 'True', 'true', 1, '1'}
    falsey = {False, 'F', 'f', 'FALSE', 'False', 'false', 0, '0'}

    def process(self, value):
        if isinstance(value, bool):
            return (value, None)
        elif isinstance(value, (int, str)):
            strvalue = str(value).lower()
            if strvalue in self.truthy:
                return (True, None)
            elif strvalue in self.falsey:
                return (False, None)
            else:
                return (None, INVALID_VALUE)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return self.faker.boolean()


class Numeric(Float):
    def __init__(self, precision=None, **kwargs):
        super().__init__(**kwargs)
        self.precision = precision

    def process(self, value):
        result, error = super().process(value)
        if error is None and result is not None:
            if self.precision is not None:
                get_decimal_context().prec = self.precision
            return (Decimal(result), error)
        else:
            return (result, error)


class TimeDelta(Field):

    RE_PATTERN_1 = re.compile(
        r'(?P<days>[-\d]+) day[s]*, (?P<hours>\d+):'
        r'(?P<minutes>\d+):(?P<seconds>\d[\.\d+]*)'
    )

    RE_PATTERN_2 = re.compile(
        r'(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d[\.\d+]*)'
    )

    def parse(self, text):
        if 'day' in text:
            match = self.RE_PATTERN_1.match(text)
        else:
            match = self.RE_PATTERN_2.match(text)
        if match: 
            return timedelta(**{
                key: float(val) for key, val in match.groupdict().items()
            })
        return

    def __init__(self, unit='seconds', **kwargs):
        super().__init__(**kwargs)
        self.unit = unit

    def process(self, value):
        if isinstance(value, timedelta):
            return (value, None)
        if isinstance(value, (int, float)):
            return (timedelta(**{self.unit: value}), None)
        if isinstance(value, str):
            td = self.parse(value) 
            if td is not None:
                return (td, None)
            else:
                return (None, 'unrecognized timedelta format')
        if isinstance(value, dict):
            kwargs = value
            try:
                return (timedelta(**kwargs), None)
            except:
                pass
        return (None, 'invalid timedelta')


class DateTime(Field):
    def __init__(self, tz=None, default=None, **kwargs):
        self.tz = tz or pytz.utc
        if default is True:
            default = TimeUtils.utc_now

        super().__init__(default=default, **kwargs)

    def process(self, value):
        if isinstance(value, datetime):
            return (value.replace(tzinfo=self.tz), None)
        elif isinstance(value, (int, float)):
            try:
                return (
                    TimeUtils.from_timestamp(value).replace(tzinfo=self.tz), None
                )
            except ValueError:
                return (None, INVALID_VALUE)
        elif isinstance(value, date):
            new_value = datetime.combine(value, datetime.min.time())
            new_value = new_value.replace(tzinfo=self.tz)
            return (new_value, None)
        elif isinstance(value, str):
            try:
                return (
                    dateutil.parser.parse(value).replace(tzinfo=self.tz), None
                )
            except:
                return (None, INVALID_VALUE)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return self.faker.date_time_this_year(tzinfo=self.tz)


class DateTimeString(String):
    def __init__(self, format_spec=None, timezone=None, **kwargs):
        super().__init__(**kwargs)
        self.format_spec = format_spec
        if timezone is None:
            timezone = pytz.utc
        self.timezone = timezone

    def process(self, value):
        if isinstance(value, str):
            try:
                dt = dateutil.parser.parse(value)
            except:
                return (None, INVALID_VALUE)
        elif isinstance(value, (int, float)):
            dt = TimeUtils.from_timestamp(value)
        elif isinstance(value, datetime):
            dt = value.replace(tzinfo=self.timezone)
        elif isinstance(value, date):
            dt = datetime.combine(value, datetime.min.time())
        else:
            return (None, UNRECOGNIZED_VALUE)

        if self.format_spec:
            dt_str = datetime.strftime(dt, self.format_spec)
        else:
            dt_str = dt.isoformat()

        return (dt_str, None)

    def on_generate(self, **kwargs):
        if self.format_spec:
            return datetime.strftime(
                self.faker.date_time_this_year(tzinfo=pytz.utc),
                self.format_spec
            )
        return self.faker.date_time_this_year(tzinfo=pytz.utc).isoformat()


class Timestamp(Field):
    np_dtype = 'int64'

    def process(self, value):
        if isinstance(value, (int, float)):
            return (value, None)
        elif isinstance(value, datetime):
            return (TimeUtils.to_timestamp(value), None)
        elif isinstance(value, date):
            return (time.mktime(value.timetuple()), None)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return TimeUtils.to_timestamp(
            self.faker.date_time_this_year(tzinfo=pytz.utc)
        )


class List(Field):
    def __init__(self, nested: Field = None, **kwargs):

        def on_create():
            singular_name = StringUtils.singular(self.name)
            self.nested.name = singular_name
            self.nested.source = singular_name
            self.np_dtype = self.nested.np_dtype
            on_create_custom = kwargs.pop('on_create', None)
            if on_create_custom:
                on_create_custom()

        super().__init__(on_create=on_create, **kwargs)

        self.scalar = False
        self.nested = None

        from appyratus.schema import Schema

        if isinstance(nested, Nested):
            self.nested = nested.schema
        elif isinstance(nested, dict):
            self.nested = Schema.factory('NestedSchema', nested)()
        elif isinstance(nested, Field):
            self.nested = deepcopy(nested)
        elif callable(nested):
            # expects that a Schema instance is returned
            self.nested = nested()
        else:
            self.nested = Schema()

    def __repr__(self):
        if self.name and self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{}, {})'.format(
            self.__class__.__name__,
            getattr(self, 'source') or '?',
            load_to,
            self.nested.__class__.__name__,
        )

    def process(self, sequence):
        dest_sequence = []
        idx2error = {}
        if sequence is None:
            if self.nullable:
                return (None, None)
            else:
                return (None, INVALID_VALUE)

        if isinstance(sequence, set):
            sequence = sorted(sequence)
        for idx, value in enumerate(sequence):
            dest_val, err = self.nested.process(value)
            if not err:
                dest_sequence.append(dest_val)
            else:
                idx2error[idx] = err

        if not idx2error:
            return (dest_sequence, None)
        else:
            return (None, idx2error)

    def on_generate(self, **kwargs):
        return [
            self.nested.generate() for _ in range(random.randint(1, 10))
        ]


class Set(List):

    def __repr__(self):
        if self.name and self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{}, {})'.format(
            self.__class__.__name__,
            self.source,
            load_to,
            self.nested.__class__.__name__,
        )

    def process(self, sequence):
        result, error = super().process(list(sequence))
        return ((set(result) if not error and result else result), error)


class Nested(Field):
    """
    # Example:
    ```python
        my_fields = Nested({
            'field_1': Str(),
            'field_2': Int(),
        })
    ```
    """
    def __init__(self, obj, **kwargs):
        super().__init__(**kwargs)

        from appyratus.schema import Schema

        self.scalar = False
        self.schema_type = None
        self.schema = None

        if isinstance(obj, dict):
            if self.name is not None:
                name = self.name.replace('_', ' ').title().replace(' ', '')
                class_name = f'{name}Schema'
            else:
                class_name = 'Schema'
            self.schema_type = Schema.factory(class_name, obj)
            self.schema = self.schema_type()
        elif isinstance(obj, Schema):
            self.schema = obj
            self.schema_type = type(obj)
        elif isinstance(obj, type) and issubclass(obj, Schema):
            self.schema_type = obj
            self.schema = self.schema_type()
        elif callable(obj):
            self.schema = obj()
            self.schema_type = type(self.schema)

    def __repr__(self):
        if self.name and self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{})'.format(self.schema.__class__.__name__, self.source, load_to)

    def process(self, value):
        return self.schema.process(value)

    def on_generate(self, **kwargs):
        return self.schema.generate()


class Dict(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scalar = False

    def process(self, value):
        if isinstance(value, dict):
            return (value, None)
        elif isinstance(value, str):
            # assume is JSON end decode it
            from appyratus.json import JsonEncoder

            json = JsonEncoder()
            try:
                value = json.decode(value)
                if not isinstance(value, dict):
                    return (None, UNRECOGNIZED_VALUE)
                return (value, None)
            except Exception:
                return (None, UNRECOGNIZED_VALUE)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return self.faker.pydict()


class FilePath(String):
    """
    # FilePath
    Coerce a filepath into it's absolutized form.  This includes expanding the
    userpath if specified.
    """
    def process(self, value):
        if isinstance(value, str):
            value = abspath(expanduser(value))
            return (value, None)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, **kwargs):
        return self.faker.file_path()


class IpAddress(String):
    """
    # IPv4/6
    """
    def on_generate(self, **kwargs):
        if random.randint(1, 10) < 3:
            return self.faker.ipv6()
        else:
            return self.faker.ipv4()


class DomainName(String):
    """
    # Domain Name
    """
    def on_generate(self, **kwargs):
        return self.faker.domain_name()


class Url(String):
    """
    # Web URL
    """
    def on_generate(self, **kwargs):
        return self.faker.url()


class BcryptString(String):
    encoding = 'utf8'

    class hash_str(str):
        def __eq__(self, other: str):
            return bcrypt.checkpw(
                other.encode(BcryptString.encoding), self.encode(BcryptString.encoding)
            )

    def __init__(self, rounds=14, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rounds = rounds

    def process(self, value):
        value, error = super().process(value)
        if error:
            return (None, error)
        elif RE_BCRYPT_HASH.match(value):
            return (self.hash_str(value), None)

        salt = bcrypt.gensalt(self.rounds)
        raw_hash_enc = bcrypt.hashpw(value.encode(self.encoding), salt)
        raw_hash = raw_hash_enc.decode(self.encoding)

        return (self.hash_str(raw_hash), None)

    def on_generate(self, **kwargs):
        # hash for password: "password"
        return '$2b$05$OkUuDW0uEXLLbYWZBKtLCO4amuuY7AjBOfUSe6I3dizBHXxVnppA2'


class ItemGetter(Field):
    """
    # Item Getter
    Get items from a nested data structure

    In example, All of the Voyager's systems are down and B'Elana needs to
    access the `ships` data node.  She only has her trusty PADD and   She would specify:

    ```py
    data = {'ships': {'voyager': {'status': 'Bad Ass'}}}
    class 
    primary_status = ItemGetter(fields.String(), source="ships.voyager.status")
    ```

    and bearing the , then `primary_status` would return "Bad Ass" rightfully

    """

    def __init__(self, obj, source: Text, separator: Text = None, **kwargs):
        """
        # Args
        - `obj` the object expected to be found at the provided source
        - `source`, the path to the key you want to tap into
        - `separator', the separator used to identify segments of the source path
        - `**kwargs`, to be passed to super
        """
        if not separator:
            separator = '.'

        path = source.split(separator)
        self.path = path[1:]

        super().__init__(source=path[0], **kwargs)

    def after(self, field, fstr, data, context=None):
        """
        # Do Format
        The heavy lifting callable of the Item Getter, passed into pre-process
        """
        if not data:
            return (data, None)
        mydata = reduce(operator.getitem, self.path, data)
        return (mydata, None)
