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
        self.default = default or lambda field, *args, **kwargs: None
        self.callbacks = callbacks or {}

    def generate(self, field: 'Field', *args, **kwargs):
        if field.name is not None:
            func = self.default
        else:
            func = self.callbacks.get(field.name, self.default)
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

    generator = FieldValueGenerator()
    # `faker_presetes` is a mapping from common field names, like "first_name",
    # to a dict containing the name of a Faker method an an arguments dict,
    # like: {"first_name": {"method": "first_name", "args": {}}}
    faker_presets = {}

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
        self.faker = Faker()

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

    def fake(self, *args, **kwargs):
        return self.generator.generate(*args, **kwargs)
        if self.name is not None:
            options = self.faker_presets.get(self.name)
            if options is None:
                match = RE_FIELD_NAME_SUFFIX.match(self.name)
                if match:
                    name = match.groups()[0]
                    options = self.faker_presets.get(name)
            if options is not None:
                func = getattr(self.faker, options['method'])
                return func(**options.get('args', {}))
        return None


class Enum(Field):
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

    def fake(self):
        return random.choice(list(self.values()))


class String(Field):

    faker_presets = {
        'first_name': {'method': 'first_name'},
        'last_name': {'method': 'first_name'},
        'full_name': {'method': 'name'},
        'name': {'method': 'catch_phrase'},
        'description': {'method': 'paragraph', 'args': {'nb_sentences': 10}},
        'summary': {'method': 'paragraph', 'args': {'nb_sentences': 5}},
        'city': {'method': 'city'},
        'address': {'method': 'address'},
        'phone': {'method': 'phone_number'},
        'phone_number': {'method': 'phone_number'},
        'mobile': {'method': 'phone_number'},
        'zip': {'method': 'zipcode'},
        'zip_code': {'method': 'zipcode'},
        'postal_code': {'method': 'zipcode'},
        'year': {'method': 'year'},
        'user_name': {'method': 'user_name'},
        'username': {'method': 'user_name'},
        'nick': {'method': 'user_name'},
        'nick_name': {'method': 'user_name'},
        'handle': {'method': 'user_name'},
        'screen_name': {'method': 'user_name'},
        'state_code': {'method': 'state_abbr'},
        'state': {'method': 'state'},
        'country_code': {'method': 'country_code'},
        'card_number': {'method': 'credit_card_number'},
        'credit_card_number': {'method': 'credit_card_number'},
        'credit_card_security_code': {'method': 'credit_card_security_code'},
        'security_code': {'method': 'credit_card_security_code'},
        'color': {'method': 'color_name'},
        'currency_code': {'method': 'currency_code'},
        'currency_name': {'method': 'currency_name'},
        'ein': {'method': 'ein'},
        'filename': {'method': 'file_name'},
        'file_name': {'method': 'file_name'},
        'fname': {'method': 'file_name'},
        'file_path': {'method': 'file_path'},
        'filepath': {'method': 'file_path'},
        'fpath': {'method': 'file_path'},
        'file_extension': {'method': 'file_extension'},
        'image_url': {'method': 'image_url'},
        'host': {'method': 'hostname'},
        'hostname': {'method': 'hostname'},
        'host_name': {'method': 'hostname'},
        'ssn': {'method': 'ssn'},
        'ip_addr': {'method': 'ipv4'},
        'ip_address': {'method': 'ipv4'},
        'ip': {'method': 'ipv4'},
        'language_code': {'method': 'language_code'},
        'license_plate': {'method': 'license_plate'},
        'locale': {'method': 'locale'},
        'mac_addr': {'method': 'mac_address'},
        'mac_address': {'method': 'mac_address'},
        'md5': {'method': 'md5'},
        'mime_type': {'method': 'mime_type'},
        'mimetype': {'method': 'mime_type'},
        'mime': {'method': 'mime_type'},
        'month': {'method': 'month'},
        'isbn': {'method': 'isbn10'},
        'slug': {'method': 'slug'},
        'street': {'method': 'street_name'},
        'street_name': {'method': 'street_name'},
        'suffix': {'method': 'suffix'},
        'timezone': {'method': 'timezone'},
        'tz': {'method': 'timezone'},
        'time_zone': {'method': 'timezone'},
        'user_agent': {'method': 'user_agent'},
        'useragent': {'method': 'user_agent'},
        'ua': {'method': 'user_agent'},
        'id': {'method': 'random_number', 'args': {'digits': 16}},
        '_id': {'method': 'random_number', 'args': {'digits': 16}},
        'text': {'method': 'text'},
        'event': {'method': 'word'},
        'event_name': {'method': 'word'},
        'email': {'method': 'email'},
        'email_addr': {'method': 'email'},
        'email_address': {'method': 'email'},
        'message': {'method': 'text', 'args': {'max_nb_chars': 140}},
        'keyword': {'method': 'word'},
        'headline': {'method': 'catch_phrase'},
        'tag': {'method': 'word'},
        'amount': {'method': 'random_number', 'args': {'digits': 3}},
    }

    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        elif value is not None:
            return (str(value), None)
        else:
            return (value, 'unrecognized')

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        else:
            return self.faker.text(max_nb_chars=100)


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

    def fake(self):
        value = super().fake()
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

    def fake(self):
        return super().fake()


class Int(Field):

    faker_presets = {
        '_id': {'method': 'random_number', 'args': {'digits': 16}},
        '_rev': {'method': 'random_number', 'args': {'digits': 5}},
        'id': {'method': 'random_number', 'args': {'digits': 16}},
        'age': {'method': 'random_number', 'args': {'digits': 2}},
        'width': {'method': 'random_number', 'args': {'digits': 4}},
        'height': {'method': 'random_number', 'args': {'digits': 4}},
        'angle': {'method': 'random_number', 'args': {'digits': 3}},
        'scale': {'method': 'random_number', 'args': {'digits': 3}},
        'count': {'method': 'random_number', 'args': {'digits': 5}},
        'year': {'method': 'year', 'args': {}},
        'month': {'method': 'month', 'args': {}},
        'day': {'method': 'day_of_month', 'args': {}},
        'code': {'method': 'random_number', 'args': {'digits': 5}},
    }

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

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        return random.randint(-sys.maxsize, sys.maxsize)


class Uint32(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        return random.randint(0, 4294967295)

class Uint64(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        return random.randint(0, 18446744073709551615)


class Sint32(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        return random.randint(-2147483648, 2147483647)


class Sint64(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        return random.randint(-9223372036854775808, 9223372036854775807)


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

    def fake(self):
        value = super().fake()
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

    def fake(self):
        value = super().fake()
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

    def fake(self):
        value = super().fake()
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

    def fake(self):
        value = super().fake()
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

    def fake(self):
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

    def fake(self):
        value = super().fake()
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

    def fake(self):
        value = super().fake()
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

    def fake(self):
        value = super().fake()
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

    def fake(self):
        return [self.nested.fake() for i in range(random.randint(1, 10))]


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

    def fake(self):
        return set(super().fake())


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

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        return self.nested.fake()


class Dict(Field):
    def process(self, value):
        if isinstance(value, dict):
            return (value, None)
        else:
            return (None, 'unrecognized')

    def fake(self):
        value = super().fake()
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

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        return self.faker.file_path()


class IpAddress(String):
    """
    # IPv4
    """

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        return self.faker.ipv4()


class DomainName(String):
    """
    # Domain Name
    """

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        return self.faker.domain_name()


class Url(String):
    """
    # Web URL
    """

    def fake(self):
        value = super().fake()
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

    def fake(self):
        value = super().fake()
        if value is not None:
            return value
        salt = bcrypt.gensalt(self.rounds)
        return bcrypt.hashpw('password'.encode('utf8'), salt).decode('utf8')
