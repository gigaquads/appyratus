import inflect
import random
import uuid
import re
import time
import typing
import sys

from copy import deepcopy
from datetime import date, datetime
from os.path import abspath, expanduser
from typing import Type, Callable, Text, Dict
from uuid import UUID, uuid4

import pytz
import bcrypt
import dateutil.parser

from faker import Faker
from appyratus.utils import TimeUtils, DictUtils, StringUtils

from .value_generator import ValueGenerator
from .field_adapter import FieldAdapter

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

    generator = ValueGenerator()
    faker = Faker()

    def __init__(
        self,
        source: Text = None,
        name: Text = None,
        required: bool = False,
        nullable: bool = True,
        default: object = None,
        meta: typing.Dict = None,
        on_create: object = None,
        post_process: object = None,
        on_generate: Callable = None,
        **kwargs,
    ):
        """
        # Kwargs
        - `source`: key in source data if different from declared field name.
        - `name`: name of the field as declared on the host Schema class.
        - `required`: key must exist in source data if set.
        - `nullable`: if key exists, it can be None/null if this is set.
        - `default`: a constant or callable the returns a default value.
        - `on_create`: generic method to run upon init of host schema class.
        - `post_process`: generic method to run after fields are processed.
        - `meta`: additional data storage
        """
        self.name = name
        self.source = source or name
        self.required = required
        self.nullable = nullable
        self.default = default
        self.on_create = on_create
        self.post_process = post_process
        self.meta = meta or {}
        self.meta.update(kwargs)

        # if not None, this callable will shadow the base on_generate method
        # declared on this Field class.
        if on_generate is not None:
            self.on_generate = on_generate

    def __repr__(self):
        if self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return f'<{self.__class__.__name__}({self.source}{load_to})>'

    @classmethod
    def adapt(cls, on_adapt, **kwargs) -> FieldAdapter:
        return cls.Adapter(cls, on_adapt, **kwargs)

    def process(self, value):
        return (value, None)

    def generate(self, constraint=None, *args, **kwargs):
        return self.on_generate(constraint=constraint, *args, **kwargs)

    def pre_process(self, value, source: dict, context: dict = None):
        """
        This method is *intentionally* shadowed by the ctor keyword argument
        with the same name. This stub is just for declaring the expected
        interface.
        """
        return (value, None)

    def post_process(self, dest: dict, value, context=None):
        """
        This method is *intentionally* shadowed by the ctor keyword argument
        with the same name. This stub is just for declaring the expected
        interface.
        """
        return (value, None)

    def on_generate(self, constraint=None, *args, **kwargs):
        return self.generator.generate(
            self, constraint=constraint, *args, **kwargs
        )


class Enum(Field):

    generator = Field.Generator(
        default=lambda f, cield, *args, **kwargs: (
            random.choice(list(field.values()))
        )
    )

    def __init__(self, nested: Field, values, **kwargs):
        self.nested = nested
        self.values = set(values)
        super().__init__(**kwargs)

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


class String(Field):

    generator = Field.Generator(
        callbacks={
            '_id': lambda f: UuidString.next_id(),
            'id': lambda f: str(f.faker.random_number(digits=16)),
            'public_id': lambda f, c: UuidString.next_id(),
            'first_name': lambda f, c: f.faker.first_name(),
            'last_name': lambda f, c: f.faker.last_name(),
            'full_name': lambda f, c: f.faker.name(),
            'name': lambda f, c: f.faker.catch_phrase().title(),
            'description': lambda f, c: f.faker.paragraph(nb_sentences=10),
            'descr': lambda f, c: f.faker.paragraph(nb_sentences=10),
            'summary': lambda f, c: f.faker.paragraph(nb_sentences=6),
            'city': lambda f, c: f.faker.city(),
            'address': lambda f, c: f.faker.address(),
            'phone': lambda f, c: f.faker.phone_number(),
            'phone_number': lambda f, c: f.faker.phone_number(),
            'mobile': lambda f, c: f.faker.phone_number(),
            'zip': lambda f, c: f.faker.zipcode(),
            'zip_code': lambda f, c: f.faker.zipcode(),
            'zipcode': lambda f, c: f.faker.zipcode(),
            'postal_code': lambda f, c: f.faker.zipcode(),
            'postalcode': lambda f, c: f.faker.zipcode(),
            'year': lambda f, c: f.faker.year(),
            'user_name': lambda f, c: f.faker.user_name(),
            'username': lambda f, c: f.faker.user_name(),
            'nick': lambda f, c: f.faker.user_name(),
            'handle': lambda f, c: f.faker.user_name(),
            'screen_name': lambda f, c: f.faker.user_name(),
            'screenname': lambda f, c: f.faker.user_name(),
            'state_code': lambda f, c: f.faker.state_abbr(),
            'state': lambda f, c: f.faker.state(),
            'country_code': lambda f, c: f.faker.country_code(),
            'country': lambda f, c: f.faker.country(),
            'card_number': lambda f, c: f.faker.credit_card_number(),
            'credit_card_number': lambda f, c: f.faker.credit_card_number(),
            'security_code': lambda f, c: f.faker.credit_card_security_code(),
            'credit_card_security_code': lambda f, c: f.faker.credit_card_security_code(),
            'color': lambda f, c: StringUtils.snake(f.faker.color_name()),
            'currency_code': lambda f, c: f.faker.currency_code(),
            'currency_name': lambda f, c: f.faker.currency_name(),
            'ein': lambda f, c: f.faker.ein(),
            'filename': lambda f, c: f.faker.ein(),
            'file_name': lambda f, c: f.faker.ein(),
            'fname': lambda f, c: f.faker.ein(),
            'filepath': lambda f, c: f.faker.file_path(),
            'file_path': lambda f, c: f.faker.file_path(),
            'fpath': lambda f, c: f.faker.file_path(),
            'file_extension': lambda f, c: f.faker.file_extension(),
            'extension': lambda f, c: f.faker.file_extension(),
            'ext': lambda f, c: f.faker.file_extension(),
            'image_url': lambda f, c: f.faker.image_url(),
            'url': lambda f, c: f.faker.url(),
            'host': lambda f, c: f.faker.hostname(),
            'hostname': lambda f, c: f.faker.hostname(),
            'host_name': lambda f, c: f.faker.hostname(),
            'port': lambda f, c: str(random.randrange(1001, 10000)),
            'ssn': lambda f, c: f.faker.ssn(),
            'ip_addr': lambda f, c: f.faker.ipv4(),
            'ip_address': lambda f, c: f.faker.ipv4(),
            'ip': lambda f, c: f.faker.ipv4(),
            'ipv4': lambda f, c: f.faker.ipv4(),
            'ipv6': lambda f, c: f.faker.ipv6(),
            'langauge_code': lambda f, c: f.faker.langauge_code(),
            'license_plate': lambda f, c: f.faker.license_plate(),
            'locale': lambda f, c: f.faker.locale(),
            'mac_addr': lambda f, c: f.faker.mac_address(),
            'mac_address': lambda f, c: f.faker.mac_address(),
            'md5': lambda f, c: str(f.faker.md5()),
            'mime': lambda f, c: f.faker.mime_type(),
            'mime_type': lambda f, c: f.faker.mime_type(),
            'mimetype': lambda f, c: f.faker.mime_type(),
            'month': lambda f, c: f.faker.month(),
            'isbn': lambda f, c: f.faker.isbn(),
            'slug': lambda f, c: f.faker.slug(),
            'street': lambda f, c: f.faker.street_name(),
            'street_name': lambda f, c: f.faker.street_name(),
            'suffix': lambda f, c: f.faker.suffix(),
            'timezone': lambda f, c: f.faker.timezone(),
            'time_zone': lambda f, c: f.faker.timezone(),
            'tz': lambda f, c: f.faker.timezone(),
            'user_agent': lambda f, c: f.faker.user_agent(),
            'useragent': lambda f, c: f.faker.user_agent(),
            'ua': lambda f, c: f.faker.user_agent(),
            'text': lambda f, c: f.faker.text(),
            'event': lambda f, c: f.faker.word(),
            'event_name': lambda f, c: f.faker.word(),
            'email': lambda f, c: f.faker.email(),
            'email_addr': lambda f, c: f.faker.email(),
            'email_address': lambda f, c: f.faker.email(),
            'message': lambda f, c: f.faker.text(max_nb_chars=140),
            'keyword': lambda f, c: f.faker.word().lower(),
            'tag': lambda f, c: f.faker.word().lower(),
            'headline': lambda f, c: f.faker.catch_phrase().title(),
            'amount': lambda f, c: str(random.randrange(0, 51)),
            'count': lambda f, c: str(random.randrange(0, 51)),
            'angle': lambda f, c: str(random.randrange(-360, 361)),
            'password': lambda f, c: f.faker.password(),
        },
        default=lambda f, c: f.faker.text(max_nb_chars=100)
    )

    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        elif value is not None:
            return (str(value), None)
        else:
            return (value, UNRECOGNIZED_VALUE)

    def on_generate(self, constraint=None):
        value = super().on_generate(constraint=constraint)
        if constraint is not None:
            if constraint.is_equality_constraint:
                if not constraint.is_negative:
                    value = constraint.value
                else:
                    new_value = constraint.value[::-1]
                    if new_value == value:
                        new_value += 'x'
                    value = new_value
            else:
                if constraint.is_range_constraint:
                    if constraint.upper_value is not None:
                        if value >= constraint.upper_value:
                            value = constraint.upper_value
                            if value:
                                value = value[:-1]
                    if constraint.lower_value is not None:
                        if value <= constraint.lower_value:
                            value = constraint.lower_value
                            if value:
                                value += value[-1]
        return value

class Bytes(Field):

    def __init__(self, encoding='utf-8', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoding = encoding

    def process(self, value):
        if isinstance(value, bytes):
            return (value, None)
        if isinstance(value, str):
            return (value.encode(self.encoding), None)
        return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, constraint=None):
        value = super().on_generate(constraint=constraint)
        if value is not None:
            return value
        else:
            return self.faker.binary(length=1024)


class FormatString(String):

    def __init__(self, **kwargs):
        super().__init__(post_process=self.do_format, **kwargs)

    def do_format(self, fstr, data, context=None):
        value = fstr.format(**data)
        return (value, None)

    def on_generate(self, constraint=None):
        return super().on_generate(constraint=constraint)


class Int(Field):

    generator = ValueGenerator(
        callbacks={
            '_id': lambda f, c: f.faker.random_number(digits=16),
            '_rev': lambda f, c: f.faker.random_number(digits=3),
            'public_id': lambda f, c: f.faker.random_number(digits=16),
            'age': lambda f, c: random.randint(10, 100),
            'width': lambda f, c: random.randint(0, 100),
            'height': lambda f, c: random.randint(0, 100),
            'size': lambda f, c: random.randint(0, 100),
            'depth': lambda f, c: random.randint(0, 100),
            'angle': lambda f, c: random.randint(-360, 360),
            'year': lambda f, c: int(f.faker.year()),
            'month': lambda f, c: int(f.faker.month()),
            'day': lambda f, c: int(f.faker.day_of_month()),
            'code': lambda f, c: random.randint(0, 20),
            'seq': lambda f, c: random.randint(0, 100),
            'no': lambda f, c: random.randint(0, 100),
            'num': lambda f, c: random.randint(0, 100),
        },
        default=lambda f, c: random.randint(-100, 100)
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

    def on_generate(self, constraint=None):
        # TODO: Move this constraint logic into ValueGenerator
        # and pass in as ctor callback kwarg
        if constraint is not None:
            if constraint.is_equality_constraint:
                if not constraint.is_negative:
                    value = constraint.value
                else:
                    value = constraint.value + random.randint(-100, 100)
            elif constraint.is_range_constraint:
                value = super().on_generate(constraint=constraint)
                lower = constraint.lower_value
                upper = constraint.upper_value
                if lower is not None:
                    if constraint.is_lower_inclusive and value < lower:
                        value = lower
                    elif (not constraint.is_lower_inclusive) and value <= lower:
                        value = lower + 1
                if upper is not None:
                    if constraint.is_upper_inclusive and value > upper:
                        value = upper
                    elif (not constraint.is_upper_inclusive) and value >= upper:
                        value = upper - 1
        else:
            value = super().on_generate(constraint=constraint)
        return value


class Uint(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)

    def on_generate(self, constraint=None):
        if constraint is not None and constraint.is_range_constraint:
            if constraint.lower_value is None:
                constraint.lower_value = 0
        return abs(super().on_generate(constraint=constraint))


class Uint32(Uint):
    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)


class Uint64(Uint):
    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)

    def on_generate(self, constraint=None):
        return abs(super().on_generate(constraint=constraint))


class Sint32(Int):

    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)


class Sint64(Int):

    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)


class Float(Field):

    generator = ValueGenerator(
        callbacks={
            '_id': lambda f, c: f.faker.random_number(digits=16),
            'public_id': lambda f, c: f.faker.random_number(digits=16),
            'age': lambda f, c: random.randint(12, 80),
            'width': lambda f, c: random.randint(0, 100),
            'height': lambda f, c: random.randint(0, 100),
            'depth': lambda f, c: random.randint(0, 100),
            'angle': lambda f, c: random.randint(-360, 360),
            'year': lambda f, c: int(f.faker.year()),
            'month': lambda f, c: int(f.faker.month()),
            'day': lambda f, c: int(f.faker.day_of_month()),
            'code': lambda f, c: random.randint(0, 20),
            'seq': lambda f, c: random.randint(0, 100),
            'no': lambda f, c: random.randint(0, 100),
            'num': lambda f, c: random.randint(0, 100),
        },
        default=lambda f, c: random.randint(-100, 100)
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

    def on_generate(self, constraint=None):
        value = super().on_generate(constraint=constraint)
        if value is not None:
            return value
        return random.random() * sys.maxsize


class Email(String):

    generator = ValueGenerator(
        default=lambda f, c: f.faker.email()
    )

    def process(self, value):
        dest, error = super().process(value)
        if error:
            return (dest, error)
        elif not RE_EMAIL.match(value):
            return (None, 'not a valid e-mail address')
        else:
            return (value.lower(), None)


class Uuid(Field):

    generator = ValueGenerator(default=lambda f: Uuid.next_id())

    @classmethod
    def next_id(cls):
        return uuid.uuid4()

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


class UuidString(String):

    generator = ValueGenerator(default=lambda f: UuidString.next_id())

    @classmethod
    def next_id(cls):
        return Uuid.next_id().hex

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

    def on_generate(self, constraint=None):
        value = super().on_generate(constraint=constraint)
        if value is not None:
            return value
        return Uuid.next_id().hex


class Bool(Field):

    truthy = {True, 'T', 't', 'TRUE', 'True', 'true', 1, '1'}
    falsey = {False, 'F', 'f', 'FALSE', 'False', 'false', 0, '0'}

    generator = ValueGenerator(
        default=lambda f, c: f.faker.boolean()
    )

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


class DateTime(Field):

    generator = ValueGenerator(
        default=lambda f, c: f.faker.date_time_this_year(tzinfo=pytz.utc)
    )

    def __init__(self, timezone=None, **kwargs):
        super().__init__(**kwargs)
        if timezone is None:
            timezone = pytz.utc
        self.timezone = timezone

    def process(self, value):
        if isinstance(value, datetime):
            return (value.replace(tzinfo=self.timezone), None)
        elif isinstance(value, (int, float)):
            try:
                return (TimeUtils.from_timestamp(value), None)
            except ValueError:
                return (None, INVALID_VALUE)
        elif isinstance(value, date):
            new_value = datetime.combine(value, datetime.min.time())
            new_value = new_value.replace(tzinfo=self.timezone)
            return (new_value, None)
        elif isinstance(value, str):
            try:
                return (dateutil.parser.parse(value), None)
            except:
                return (None, INVALID_VALUE)
        else:
            return (None, UNRECOGNIZED_VALUE)


class DateTimeString(String):

    generator = ValueGenerator(
        default=lambda f, c: (
            datetime.strftime(
                f.faker.date_time_this_year(tzinfo=pytz.utc), f.format_spec
            ) if f.format_spec
            else f.faker.date_time_this_year(tzinfo=pytz.utc).isoformat()
        )
    )

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

    def on_generate(self, constraint=None):
        value = super().on_generate(constraint=constraint)
        if value is not None:
            return value
        return datetime.strftime(self.faker.date_time_this_year(), self.format_spec)


class Timestamp(Field):

    generator = ValueGenerator(
        default=lambda f, c: TimeUtils.to_timestamp(
            f.faker.date_time_this_year(tzinfo=pytz.utc)
        )
    )

    def process(self, value):
        if isinstance(value, (int, float)):
            return (value, None)
        elif isinstance(value, datetime):
            return (TimeUtils.to_timestamp(value), None)
        elif isinstance(value, date):
            return (time.mktime(value.timetuple()), None)
        else:
            return (None, UNRECOGNIZED_VALUE)

    def on_generate(self, constraint=None):
        value = super().on_generate(constraint=constraint)
        if value is not None:
            return value
        return TimeUtils.to_timestamp(self.faker.date_time_this_year())


class List(Field):

    generator = ValueGenerator(
        default=lambda f, c: [
            f.nested.generate() for i in range(random.randint(1, 10))
        ]
    )

    _inflect = inflect.engine()

    def __init__(self, nested: Field = None, **kwargs):
        on_create_kwarg = kwargs.pop('on_create', None)

        def on_create(schema_type: Type['Schema']):
            if on_create_kwarg:
                on_create_kwarg(schema_type)

            from appyratus.schema import Schema

            if isinstance(nested, Nested):
                # XXX nested.on_create has not been called yet, so it has not
                # been setup with nested.schema, and subsequently the name
                # cannot be set.. nested is NoneType and nested.schema is None
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

            singular_name = self._inflect.singular_noun(self.name)
            self.nested.name = singular_name
            self.nested.source = singular_name

            if self.nested.on_create:
                self.nested.on_create(schema_type)

        super().__init__(on_create=on_create, **kwargs)
        self.nested = None

    def __repr__(self):
        if self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{}, {})'.format(
            self.__class__.__name__,
            getattr(self, 'source') or 'NoSource',
            load_to,
            self.nested.__class__.__name__,
        )

    def process(self, sequence):
        dest_sequence = []
        idx2error = {}
        if not sequence:
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


class Set(List):

    def __repr__(self):
        if self.source != self.name:
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

    def on_generate(self, constraint=None):
        return set(super().on_generate(constraint=constraint))


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

    generator = ValueGenerator(
        default=lambda f, c: f.nested.generate()
    )

    def __init__(self, obj, **kwargs):

        def on_create(schema_type: Type['Schema']):
            from appyratus.schema import Schema

            if isinstance(obj, dict):
                name = self.name.replace('_', ' ').title().replace(' ', '')
                class_name = f'{name}Schema'
                self.schema_type = Schema.factory(class_name, obj)
                self.schema = self.schema_type()
            elif isinstance(obj, Schema):
                self.schema_type = obj
                self.schema = self.schema_type()
            elif callable(obj):
                self.schema = obj()
                self.schema_type = obj.__class__

        super().__init__(on_create=on_create, **kwargs)
        self.schema_type = None
        self.schema = None

    def __repr__(self):
        if self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{})'.format(self.schema.__class__.__name__, self.source, load_to)

    def process(self, value):
        return self.schema.process(value)


class Dict(Field):

    generator = ValueGenerator(
        default=lambda f, c: f.faker.pydict()
    )

    def process(self, value):
        if isinstance(value, dict):
            return (value, None)
        else:
            return (None, UNRECOGNIZED_VALUE)


class FilePath(String):
    """
    # FilePath
    Coerce a filepath into it's absolutized form.  This includes expanding the
    userpath if specified.
    """

    generator = ValueGenerator(
        default=lambda f, c: f.faker.file_path()
    )

    def process(self, value):
        if isinstance(value, str):
            value = abspath(expanduser(value))
            return (value, None)
        else:
            return (None, UNRECOGNIZED_VALUE)


class IpAddress(String):
    """
    # IPv4
    """

    generator = ValueGenerator(
        default=lambda f, c: (
            f.faker.ipv4() if random.randint(0, 1) else f.faker.ipv6()
        )
    )


class DomainName(String):
    """
    # Domain Name
    """

    generator = ValueGenerator(
        default=lambda f, c: f.faker.domain_name()
    )


class Url(String):
    """
    # Web URL
    """

    generator = ValueGenerator(
        default=lambda f, c: f.faker.url()
    )


class BcryptString(String):

    class hash_str(str):

        def __eq__(self, other: str):
            return bcrypt.checkpw(
                other.encode(BcryptString.encoding), self.encode(BcryptString.encoding)
            )

    encoding = 'utf8'
    generator = ValueGenerator(
        default=lambda f, c: (  # hash for password: "password"
            '$2b$05$OkUuDW0uEXLLbYWZBKtLCO4amuuY7AjBOfUSe6I3dizBHXxVnppA2'
        )
    )

    def __init__(self, rounds=14, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rounds = rounds

    def process(self, value):
        value, error = super().process(value)
        if error:
            return (None, error)
        elif RE_BCRYPT_HASH.match(value):
            return (value, None)

        salt = bcrypt.gensalt(self.rounds)
        raw_hash_enc = bcrypt.hashpw(value.encode(self.encoding), salt)
        raw_hash = raw_hash_enc.decode(self.encoding)

        return (self.hash_str(raw_hash), None)
