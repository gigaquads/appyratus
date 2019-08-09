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
from appyratus.utils import TimeUtils, DictUtils

RE_FIELD_NAME_SUFFIX = re.compile(r'^.+_([^_]+)$')


class FieldValueGenerator(object):
    def __init__(self, callbacks: Dict[Text, Callable] = None, default: Callable = None):
        self.default = default or (lambda field, *args, **kwargs: None)
        self.callbacks = callbacks or {}
        self.inflect = inflect.engine()

    def generate(self, field: 'Field', *args, **kwargs):
        if field.name is None:
            func = self.default
        else:
            func = self.callbacks.get(field.name, self.default)
            if func is self.default:
                singular_name = self.inflect.singular_noun(field.name)
                func = self.callbacks.get(singular_name, self.default)
            if func is self.default:
                match = RE_FIELD_NAME_SUFFIX.match(field.name)
                if match:
                    name = match.groups()[0]
                    func = self.callbacks.get(name, self.default)
        return func(field, *args, **kwargs)


class FieldTypeAdapter(object):
    """
    FieldTypeAdapter is used by anything that needs to be able to convert an
    appyratus Field type to a corresponding field type used by some other
    library. See the SqlalchemyDao in the `pybiz` project for an example.
    """

    def __init__(
        self,
        field_type: Type['Field'],
        on_adapt: Callable = None,
        on_encode: Callable = None,
        on_decode: Callable = None,
    ):
        self.field_type = field_type
        self.on_adapt = on_adapt
        self.on_encode = on_encode
        self.on_decode = on_decode


class Field(object):

    TypeAdapter = FieldTypeAdapter
    ValueGenerator = FieldValueGenerator

    faker = Faker()
    generator = FieldValueGenerator()

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

    def __repr__(self):
        if self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return f'<{self.__class__.__name__}({self.source}{load_to})>'

    @classmethod
    def adapt(cls, on_adapt, **kwargs) -> TypeAdapter:
        return cls.TypeAdapter(cls, on_adapt, **kwargs)

    def process(self, value):
        return (value, None)

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

    def generate(self, *args, **kwargs):
        return self.generator.generate(self, *args, **kwargs)


class Enum(Field):

    generator = Field.ValueGenerator(
        default=lambda field, *args, **kwargs: (
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
            return (None, 'unrecognized')
        else:
            return (nested_value, None)


class String(Field):

    generator = Field.ValueGenerator(
        callbacks={
            '_id': lambda f, *a, **k: uuid.uuid4().hex,
            'public_id': lambda f, *a, **k: uuid.uuid4().hex,
            'first_name': lambda f, *a, **k: f.faker.first_name(),
            'last_name': lambda f, *a, **k: f.faker.last_name(),
            'full_name': lambda f, *a, **k: f.faker.name(),
            'name': lambda f, *a, **k: f.faker.catch_phrase().title(),
            'description': lambda f, *a, **k: f.faker.paragraph(nb_sentences=10),
            'descr': lambda f, *a, **k: f.faker.paragraph(nb_sentences=10),
            'summary': lambda f, *a, **k: f.faker.paragraph(nb_sentences=6),
            'city': lambda f, *a, **k: f.faker.city(),
            'address': lambda f, *a, **k: f.faker.address(),
            'phone': lambda f, *a, **k: f.faker.phone_number(),
            'phone_number': lambda f, *a, **k: f.faker.phone_number(),
            'mobile': lambda f, *a, **k: f.faker.phone_number(),
            'zip': lambda f, *a, **k: f.faker.zipcode(),
            'zip_code': lambda f, *a, **k: f.faker.zipcode(),
            'zipcode': lambda f, *a, **k: f.faker.zipcode(),
            'postal_code': lambda f, *a, **k: f.faker.zipcode(),
            'postalcode': lambda f, *a, **k: f.faker.zipcode(),
            'year': lambda f, *a, **k: f.faker.year(),
            'user_name': lambda f, *a, **k: f.faker.user_name(),
            'username': lambda f, *a, **k: f.faker.user_name(),
            'nick': lambda f, *a, **k: f.faker.user_name(),
            'handle': lambda f, *a, **k: f.faker.user_name(),
            'screen_name': lambda f, *a, **k: f.faker.user_name(),
            'screenname': lambda f, *a, **k: f.faker.user_name(),
            'state_code': lambda f, *a, **k: f.faker.state_abbr(),
            'state': lambda f, *a, **k: f.faker.state(),
            'country_code': lambda f, *a, **k: f.faker.country_code(),
            'country': lambda f, *a, **k: f.faker.country(),
            'card_number': lambda f, *a, **k: f.faker.credit_card_number(),
            'credit_card_number': lambda f, *a, **k: f.faker.credit_card_number(),
            'security_code': lambda f, *a, **k: f.faker.credit_card_security_code(),
            'credit_card_security_code': lambda f, *a, **k: f.faker.credit_card_security_code(),
            'color': lambda f, *a, **k: f.faker.color(),
            'currency_code': lambda f, *a, **k: f.faker.currency_code(),
            'currency_name': lambda f, *a, **k: f.faker.currency_name(),
            'ein': lambda f, *a, **k: f.faker.ein(),
            'filename': lambda f, *a, **k: f.faker.ein(),
            'file_name': lambda f, *a, **k: f.faker.ein(),
            'fname': lambda f, *a, **k: f.faker.ein(),
            'filepath': lambda f, *a, **k: f.faker.file_path(),
            'file_path': lambda f, *a, **k: f.faker.file_path(),
            'fpath': lambda f, *a, **k: f.faker.file_path(),
            'file_extension': lambda f, *a, **k: f.faker.file_extension(),
            'extension': lambda f, *a, **k: f.faker.file_extension(),
            'ext': lambda f, *a, **k: f.faker.file_extension(),
            'image_url': lambda f, *a, **k: f.faker.image_url(),
            'url': lambda f, *a, **k: f.faker.url(),
            'host': lambda f, *a, **k: f.faker.hostname(),
            'hostname': lambda f, *a, **k: f.faker.hostname(),
            'host_name': lambda f, *a, **k: f.faker.hostname(),
            'port': lambda f, *a, **k: str(random.randrange(1001, 10000)),
            'ssn': lambda f, *a, **k: f.faker.ssn(),
            'ip_addr': lambda f, *a, **k: f.faker.ipv4(),
            'ip_address': lambda f, *a, **k: f.faker.ipv4(),
            'ip': lambda f, *a, **k: f.faker.ipv4(),
            'ipv4': lambda f, *a, **k: f.faker.ipv4(),
            'ipv6': lambda f, *a, **k: f.faker.ipv6(),
            'langauge_code': lambda f, *a, **k: f.faker.langauge_code(),
            'license_plate': lambda f, *a, **k: f.faker.license_plate(),
            'locale': lambda f, *a, **k: f.faker.locale(),
            'mac_addr': lambda f, *a, **k: f.faker.mac_address(),
            'mac_address': lambda f, *a, **k: f.faker.mac_address(),
            'md5': lambda f, *a, **k: str(f.faker.md5()),
            'mime': lambda f, *a, **k: f.faker.mime_type(),
            'mime_type': lambda f, *a, **k: f.faker.mime_type(),
            'mimetype': lambda f, *a, **k: f.faker.mime_type(),
            'month': lambda f, *a, **k: f.faker.month(),
            'isbn': lambda f, *a, **k: f.faker.isbn(),
            'slug': lambda f, *a, **k: f.faker.slug(),
            'street': lambda f, *a, **k: f.faker.street_name(),
            'street_name': lambda f, *a, **k: f.faker.street_name(),
            'suffix': lambda f, *a, **k: f.faker.suffix(),
            'timezone': lambda f, *a, **k: f.faker.timezone(),
            'time_zone': lambda f, *a, **k: f.faker.timezone(),
            'tz': lambda f, *a, **k: f.faker.timezone(),
            'user_agent': lambda f, *a, **k: f.faker.user_agent(),
            'useragent': lambda f, *a, **k: f.faker.user_agent(),
            'ua': lambda f, *a, **k: f.faker.user_agent(),
            'id': lambda f, *a, **k: f.faker.random_number(digits=16),
            '_id': lambda f, *a, **k: uuid.uuid4().hex,
            'text': lambda f, *a, **k: f.faker.text(),
            'event': lambda f, *a, **k: f.faker.word(),
            'event_name': lambda f, *a, **k: f.faker.word(),
            'email': lambda f, *a, **k: f.faker.email(),
            'email_addr': lambda f, *a, **k: f.faker.email(),
            'email_address': lambda f, *a, **k: f.faker.email(),
            'message': lambda f, *a, **k: f.faker.text(max_nb_chars=140),
            'keyword': lambda f, *a, **k: f.faker.word().lower(),
            'tag': lambda f, *a, **k: f.faker.word().lower(),
            'headline': lambda f, *a, **k: f.faker.catch_phrase().title(),
            'amount': lambda f, *a, **k: str(random.randrange(0, 51)),
            'count': lambda f, *a, **k: str(random.randrange(0, 51)),
            'angle': lambda f, *a, **k: str(random.randrange(-360, 361)),
        },
        default=lambda f, *a, **k: f.faker.text(max_nb_chars=100)
    )

    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        elif value is not None:
            return (str(value), None)
        else:
            return (value, 'unrecognized')


class Bytes(Field):
    def __init__(self, encoding='utf-8', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoding = encoding

    def process(self, value):
        if isinstance(value, bytes):
            return (value, None)
        if isinstance(value, str):
            return (value.encode(self.encoding), None)
        return (None, 'unrecognized')

    def generate(self):
        value = super().generate()
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

    def generate(self):
        return super().generate()


class Int(Field):

    generator = Field.ValueGenerator(
        callbacks={
            '_id': lambda f, *a, **k: f.faker.random_number(digits=16),
            'public_id': lambda f, *a, **k: f.faker.random_number(digits=16),
            'age': lambda f, *a, **k: random.randint(12, 80),
            'width': lambda f, *a, **k: random.randint(0, 100),
            'height': lambda f, *a, **k: random.randint(0, 100),
            'depth': lambda f, *a, **k: random.randint(0, 100),
            'angle': lambda f, *a, **k: random.randint(-360, 360),
            'year': lambda f, *a, **k: int(f.faker.year()),
            'month': lambda f, *a, **k: int(f.faker.month()),
            'day': lambda f, *a, **k: int(f.faker.day_of_month()),
            'code': lambda f, *a, **k: random.randint(0, 20),
            'seq': lambda f, *a, **k: random.randint(0, 100),
            'no': lambda f, *a, **k: random.randint(0, 100),
            'num': lambda f, *a, **k: random.randint(0, 100),
        },
        default=lambda f, *a, **k: random.randint(-100, 100)
    )

    def __init__(self, signed=False, **kwargs):
        super().__init__(**kwargs)
        self.signed = signed

    def process(self, value):
        if isinstance(value, str):
            if not value.isdigit():
                return (None, 'invalid')
            else:
                value = int(value)
        if isinstance(value, int):
            if self.signed and value < 0:
                return (None, 'invalid')
            else:
                return (value, None)
        else:
            return (None, 'unrecognized')


class Uint32(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)

    def generate(self):
        return abs(super().generate())

class Uint64(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)

    def generate(self):
        return abs(super().generate())


class Sint32(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)


class Sint64(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)


class Float(Field):
    re_float = re.compile(r'^\d*(\.\d*)?$')

    def process(self, value):
        if isinstance(value, float):
            return (value, None)
        elif isinstance(value, int):
            return (float(value), None)
        elif isinstance(value, str):
            if not self.re_float.match(value):
                return (None, 'expected a float')
            else:
                return (float(value), None)
        else:
            return (None, 'expected a float')

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return random.random() * sys.maxsize


class Email(String):
    re_email = re.compile(r'^[a-z][\w\-\.]*@[\w\.\-]*\w\.\w+$', re.I)

    def process(self, value):
        dest, error = super().process(value)
        if error:
            return (dest, error)
        elif not self.re_email.match(value):
            return (None, 'not a valid e-mail address')
        else:
            return (value.lower(), None)

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return self.faker.email()


class Uuid(Field):
    re_uuid = re.compile(r'^[a-f0-9]{32}$')

    def process(self, value):
        if isinstance(value, UUID):
            return (value, None)
        elif isinstance(value, str):
            value = value.replace('-', '').lower()
            if not self.re_uuid.match(value):
                return (None, 'invalid')
            else:
                return (UUID(value), None)
        elif isinstance(value, int):
            hex_str = hex(value)[2:]
            uuid_hex = ('0' * (32 - len(hex_str))) + hex_str
            return (UUID(uuid_hex), None)
        else:
            return (None, 'unrecognized')

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return uuid.uuid4()


class UuidString(String):
    re_uuid = re.compile(r'^[a-f0-9]{32}$')

    def process(self, value):
        if isinstance(value, UUID):
            return (value.hex, None)
        elif isinstance(value, str):
            value = value.replace('-', '').lower()
            if self.re_uuid.match(value):
                return (value, None)
            else:
                return (None, 'invalid')
        elif isinstance(value, int):
            hex_str = hex(value)[2:]
            uuid_hex = ('0' * (32 - len(hex_str))) + hex_str
            return (uuid_hex, None)
        else:
            return (None, 'unrecognized')

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return uuid.uuid4().hex


class Bool(Field):
    truthy = {'T', 't', 'True', 'true', 1, '1'}
    falsey = {'F', 'f', 'False', 'false', 0, '0'}

    def process(self, value):
        if isinstance(value, bool):
            return (value, None)
        elif value in self.truthy:
            return (True, None)
        elif value in self.falsey:
            return (False, None)
        else:
            return (None, 'unrecognized')

    def generate(self):
        return self.faker.boolean()


class DateTime(Field):
    def process(self, value):
        if isinstance(value, datetime):
            return (value.replace(tzinfo=pytz.utc), None)
        elif isinstance(value, (int, float)):
            try:
                return (TimeUtils.from_timestamp(value), None)
            except ValueError:
                return (None, 'invalid')
        elif isinstance(value, date):
            return (datetime.combine(value, datetime.min.time()), None)
        elif isinstance(value, str):
            try:
                return (dateutil.parser.parse(value), None)
            except:
                return (None, 'invalid')
        else:
            return (None, 'unrecognized')

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return self.faker.date_time_this_year()


class DateTimeString(String):
    def __init__(self, format_spec=None, **kwargs):
        super().__init__(**kwargs)
        self.format_spec = format_spec

    def process(self, value):
        if isinstance(value, str):
            try:
                dt = dateutil.parser.parse(value)
            except:
                return (None, 'invalid')
        elif isinstance(value, (int, float)):
            dt = TimeUtils.from_timestamp(value)
        elif isinstance(value, datetime):
            dt = value.replace(tzinfo=pytz.utc)
        elif isinstance(value, date):
            dt = datetime.combine(value, datetime.min.time())
        else:
            return (None, 'unrecognized')

        if self.format_spec:
            dt_str = datetime.strftime(dt, self.format_spec)
        else:
            dt_str = dt.isoformat()

        return (dt_str, None)

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return datetime.strftime(
            self.faker.date_time_this_year(),
            self.format_spec
        )


class Timestamp(Field):
    def process(self, value):
        if isinstance(value, (int, float)):
            return (value, None)
        elif isinstance(value, datetime):
            return (TimeUtils.to_timestamp(value), None)
        elif isinstance(value, date):
            return (time.mktime(value.timetuple()), None)
        else:
            return (None, 'unrecognized')

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return TimeUtils.to_timestamp(self.faker.date_time_this_year())


class List(Field):

    _inflect = inflect.engine()

    def __init__(self, nested: Field = None, **kwargs):
        on_create_kwarg = kwargs.pop('on_create', None)

        def on_create(schema_type: Type['Schema']):
            if on_create_kwarg:
                on_create_kwarg(schema_type)

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

            singular_name = self._inflect.singular_noun(self.name)
            self.nested.name = singular_name
            self.nested.source = singular_name

            if self.nested.on_create:
                self.nested.on_create(schema_type)

        super().__init__(on_create=on_create, **kwargs)

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
        dest_sequence = []
        idx2error = {}
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

    def generate(self):
        return [self.nested.generate() for i in range(random.randint(1, 10))]


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
        return ((set(result) if not error else result), error)

    def generate(self):
        return set(super().generate())


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
        return '{}({}{})'.format(
            self.schema.__class__.__name__, self.source, load_to
        )

    def process(self, value):
        return self.schema.process(value)

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return self.nested.generate()


class Dict(Field):
    def process(self, value):
        if isinstance(value, dict):
            return (value, None)
        else:
            return (None, 'unrecognized')

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
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
            return (None, 'unrecognized')

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return self.faker.file_path()


class IpAddress(String):
    """
    # IPv4
    """

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return self.faker.ipv4()


class DomainName(String):
    """
    # Domain Name
    """

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return self.faker.domain_name()


class Url(String):
    """
    # Web URL
    """

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        return self.faker.url()


class BcryptString(String):

    class hash_str(str):
        def __eq__(self, other: str):
            return bcrypt.checkpw(other.encode('utf8'), self.encode('utf8'))


    re_bcrypt_hash = re.compile(r'^\$2[ayb]\$.{56}$')

    def __init__(self, rounds=14, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rounds = rounds

    def process(self, value):
        value, error = super().process(value)
        if error:
            return (None, error)
        elif self.re_bcrypt_hash.match(value):
            return (value, None)
        else:
            salt = bcrypt.gensalt(self.rounds)
            raw_hash = bcrypt.hashpw(value.encode('utf8'), salt).decode('utf8')
            return (self.hash_str(raw_hash), None)

    def generate(self):
        value = super().generate()
        if value is not None:
            return value
        salt = bcrypt.gensalt(self.rounds)
        return bcrypt.hashpw('password'.encode('utf8'), salt).decode('utf8')
