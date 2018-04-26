import copy

import pytz
import dateutil.parser

from uuid import UUID, uuid4
from datetime import datetime, date
from abc import ABCMeta, abstractmethod

from Crypto import Random

from appyratus.time import to_timestamp

from .results import FieldResult
from .consts import (
    OP_LOAD,
    OP_DUMP,
    RE_EMAIL,
    RE_FLOAT,
    RE_UUID,
)


class Field(object, metaclass=ABCMeta):
    def __init__(
        self,
        allow_none=False,
        load_only=False,
        load_from=None,
        dump_to=None,
        required=False,
        load_required=False,
        dump_required=False,
        default=None,
    ):
        """
        Kwargs:
            - allow_none: the field may have a value of None.
            - required: the field must be present when loaded and dumped.
            - load_only: do not dump this field.
            - load_from: the name of the field in the pre-loaded data.
            - load_required: the field must be present when loaded
            - dump_to: the name of the field in the dumped data
            - dump_required: the field must be present when dumped
        """
        self.load_only = load_only
        self.load_from = load_from
        self.dump_to = dump_to
        self.allow_none = allow_none
        self.required = required
        self.dump_required = dump_required
        self.load_required = load_required
        self.name = None
        self.default = default

    def __repr__(self):
        return '<Field({}{})>'.format(
            self.__class__.__name__, ', name="{}"'.format(self.name)
            if self.name else ''
        )

    @property
    def default_value(self):
        if self.default is not None:
            if callable(self.default):
                return self.default()
            else:
                return copy.deepcopy(self.default)
        return None

    @property
    def has_default_value(self):
        return self.default is not None

    @abstractmethod
    def load(self, data):
        pass

    @abstractmethod
    def dump(self, data):
        pass


class Anything(Field):
    def load(self, value):
        return FieldResult(value=value)

    def dump(self, data):
        return FieldResult(value=data)


class Object(Field):
    def __init__(self, nested, *args, **kwargs):
        super(Object, self).__init__(*args, **kwargs)
        self.nested = nested    # expect to by type Schema

    def load(self, value):
        schema_result = self.nested.load(value)
        if schema_result.errors:
            return FieldResult(error=schema_result.errors)
        else:
            return FieldResult(value=self.nested.load(value).data)

    def dump(self, value):
        schema_result = self.nested.dump(value)
        if schema_result.errors:
            return FieldResult(error=schema_result.errors)
        else:
            return FieldResult(value=self.nested.dump(value).data)


class List(Field):
    def __init__(self, nested, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.nested = nested

    def load(self, value):
        if not isinstance(value, (list, tuple, set)):
            return FieldResult(error='expected a valid sequence')

        result_list = []
        if isinstance(self.nested, Field):
            for i, x in enumerate(value):
                result = self.nested.load(x)
                if result.error:
                    return FieldResult(error={i: result.error})
                result_list.append(result.value)
        else:
            for i, x in enumerate(value):
                result = self.nested.load(x)
                if result.errors:
                    return FieldResult(error={i: result.errors})
                result_list.append(result.data)

        return FieldResult(value=result_list)

    def dump(self, data):
        return self.load(data)


class Regexp(Field):
    def __init__(self, pattern, re_flags=None, *args, **kwargs):
        super(Regexp, self).__init__(*args, **kwargs)
        self.pattern = pattern
        self.flags = flags or ()
        self.regexp = re.compile(self.pattern, *self.flags)

    def load(self, value):
        if not isinstance(value, str):
            return FieldResult(error='expected a string')
        if not self.regexp.match(value):
            return FieldResult(error='illegal string format')

        return FieldResult(value=value)

    def dump(self, data):
        return self.load(data)


class Str(Field):
    def load(self, value):
        if isinstance(value, UUID):
            return FieldResult(value.hex)
        elif isinstance(value, str):
            return FieldResult(value)
        else:
            return FieldResult(
                error='expected a string but got {}'.
                format(type(value).__name__)
            )

    def dump(self, data):
        return self.load(data)


class Dict(Field):
    def load(self, value):
        if isinstance(value, dict):
            return FieldResult(value)
        else:
            return FieldResult(error='expected a dict')

    def dump(self, data):
        return self.load(data)


class Enum(Field):
    def __init__(self, nested, allowed_values, *args, **kwargs):
        super(Enum, self).__init__(*args, **kwargs)
        self.is_nested_field = isinstance(nested, Field)
        self.allowed_values = set(allowed_values)
        self.nested = nested

    def load(self, value):
        if value not in self.allowed_values:
            return FieldResult(error='unrecognized value')
        if self.is_nested_field:
            return self.nested.load(value)
        else:
            schema_result = self.nested.load(value)
            return FieldResult(
                value=schema_result.data, error=schema_result.errors
            )

    def dump(self, data):
        return self.load(data)


class Email(Field):
    def load(self, value):
        if isinstance(value, str):
            value = value.lower()
            if not RE_EMAIL.match(value):
                return FieldResult(error='not a valid e-mail address')
            return FieldResult(value=value)
        else:
            return FieldResult(error='expected an e-mail address')

    def dump(self, data):
        return self.load(data)


class Uuid(Field):

    _random_atfork = True
    _random = Random.new()

    @classmethod
    def next_uuid(cls):
        Random.atfork()
        return UUID(bytes=cls._random.read(16))

    def load(self, value):
        if isinstance(value, UUID):
            return FieldResult(value=value.hex)
        if isinstance(value, str):
            value = value.replace('-', '').lower()
            if not RE_UUID.match(value):
                return FieldResult(error='invalid UUID')
            else:
                return FieldResult(value=value)
        if isinstance(value, int):
            hex_str = hex(value)[2:]
            return FieldResult(value=('0' * (32 - len(hex_str))) + hex_str)
        return FieldResult(error='expected a UUID')

    def dump(self, value):
        return self.load(value)


class Int(Field):
    def load(self, value):
        if isinstance(value, int):
            return FieldResult(value=value)
        elif isinstance(value, str):
            if not value.isdigit():
                return FieldResult(error='expected an integer')
            return FieldResult(value=int(value))
        else:
            return FieldResult(error='expected an integer')

    def dump(self, data):
        return self.load(data)


class Float(Field):
    def load(self, value):
        if isinstance(value, float):
            return FieldResult(value=value)
        if isinstance(value, int):
            return FieldResult(value=float(value))
        if isinstance(value, str):
            if not RE_FLOAT.match(value):
                return FieldResult(error='expected a float')
            return FieldResult(value=float(value))
        return FieldResult(error='expected a float')

    def dump(self, data):
        return self.load(data)


class DateTime(Field):
    def load(self, value):
        if isinstance(value, datetime):
            return FieldResult(value=value.replace(tzinfo=pytz.utc))
        elif isinstance(value, date):
            return FieldResult(value=value)
        elif isinstance(value, (int, float)):
            try:
                return FieldResult(value=datetime.utcfromtimestamp(value))
            except ValueError:
                return FieldResult(error='invalid UTC timestamp')
        elif isinstance(value, str):
            try:
                value = dateutil.parser.parse(value)
                return FieldResult(value=value)
            except ValueError:
                return FieldResult(error='unrecongized datetime string')
        else:
            return FieldResult(error='expected a datetime string or timestamp')

    def dump(self, data):
        result = self.load(data)
        result.value = to_timestamp(result.value)
        return result
