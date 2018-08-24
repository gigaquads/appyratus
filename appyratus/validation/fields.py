import copy

import pytz
import numpy as np
import dateutil.parser
import pickle

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


class FieldMeta(type, metaclass=ABCMeta):
    def __init__(cls, name, bases, dct):
        type.__init__(cls, name, bases, dct)
        setattr(cls, 'dump', cls.build_pickled_dump_wrapper(cls.dump))
        setattr(cls, 'load', cls.build_pickled_load_wrapper(cls.load))

    @staticmethod
    def build_pickled_dump_wrapper(dump):
        def wrapper(self, value):
            result = dump(self, value)
            if self.pickled:
                result.value = pickle.dumps(value)
            return result

        return wrapper

    @staticmethod
    def build_pickled_load_wrapper(load):
        def wrapper(self, value):
            result = load(self, value)
            if self.pickled and isinstance(result.value, bytes):
                result.value = pickle.loads(result.value)
            return result

        return wrapper


class Field(metaclass=FieldMeta):
    def __init__(
        self,
        name=None,
        allow_none=False,
        load_only=False,
        load_from=None,
        dump_to=None,
        required=False,
        load_required=False,
        dump_required=False,
        default=None,
        transform=None,
        pickled=False,
    ):
        """
        Kwargs:
            - allow_none: the field may have a value of None.
            - required: the field must be present when loaded and dumped.
            - load_only: do not dump this field.
            - load_from: the name of the field in the pre-loaded data.
            - load_required: the field must be present when loaded.
            - dump_to: the name of the field in the dumped data.
            - dump_required: the field must be present when dumped.
            - default: the default field value when none provided.
            - transform: transformations to perform on a field when dumped.
            - pickled: indicates whether stored data is pickled.
        """
        self.load_only = load_only
        self.load_from = load_from
        self.dump_to = dump_to
        self.allow_none = allow_none
        self.required = required
        self.dump_required = dump_required
        self.load_required = load_required
        self.name = name
        self.default = default
        self.transform = transform
        self.pickled = pickled

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

    @property
    def load_key(self):
        return self.load_from or self.name

    @property
    def dump_key(self):
        return self.dump_to or self.name

    @abstractmethod
    def load(self, value):
        pass

    @abstractmethod
    def dump(self, value):
        pass


class Anything(Field):
    def load(self, value):
        return FieldResult(value=value)

    def dump(self, value):
        return FieldResult(value=value)


class Object(Field):
    def __init__(self, nested, *args, **kwargs):
        """
        # Args:
            - nested: either a Schema instance or a dict, containing field
              names mapped to field objects.
        """
        super().__init__(*args, **kwargs)

        if isinstance(nested, dict):
            # create a new schema class and instatiate it
            from appyratus.validation.schema import Schema
            schema_class = type('ObjectSchema', (Schema, ), nested)
            self.nested = schema_class()
        else:
            self.nested = nested

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
        super().__init__(*args, **kwargs)
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

    def dump(self, value):
        if not isinstance(value, (list, tuple, set)):
            return FieldResult(error='expected a valid sequence')

        result_list = []
        if isinstance(self.nested, Field):
            for i, x in enumerate(value):
                result = self.nested.dump(x)
                if result.error:
                    return FieldResult(error={i: result.error})
                result_list.append(result.value)
        else:
            for i, x in enumerate(value):
                result = self.nested.dump(x)
                if result.errors:
                    return FieldResult(error={i: result.errors})
                result_list.append(result.data)

        return FieldResult(value=result_list)


class Array(Field):
    def __init__(self, nested, dtype=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nested = nested
        self.dtype = dtype

    def load(self, value):
        if not isinstance(value, (list, tuple, set, np.ndarray)):
            return FieldResult(error='expected a valid sequence')
        return FieldResult(value=np.array(value, dtype=self.dtype))

    def dump(self, value):
        if not isinstance(value, np.ndarray):
            return FieldResult(error='expected a valid sequence')
        return FieldResult(value=value.tolist())


class Regexp(Field):
    def __init__(self, pattern, re_flags=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern = pattern
        self.flags = flags or ()
        self.regexp = re.compile(self.pattern, *self.flags)

    def load(self, value):
        if not isinstance(value, str):
            return FieldResult(error='expected a string')
        if not self.regexp.match(value):
            return FieldResult(error='illegal string format')

        return FieldResult(value=value)

    def dump(self, value):
        return self.load(value)


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

    def dump(self, value):
        return self.load(value)


class CompositeStr(Str):
    composite = True


class Dict(Field):
    def __init__(
        self, key: Field = None, value: Field = None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._key_field = key
        self._value_field = value

    def load(self, value):
        if not isinstance(value, dict):
            return FieldResult(error='expected a dict')
        data = {}
        for k, v in value.items():
            if self._key_field:
                key_result = self._key_field.load(k)
                if key_result.error:
                    return FieldResult(
                        error='dict key "{}" - {}'.format(k, key_result.error)
                    )
                else:
                    k = key_result.value
            if self._value_field:
                value_result = self._value_field.load(v)
                if value_result.error:
                    return FieldResult(
                        error='dict value "{}" - {}'.format(
                            v, value_result.error
                        )
                    )
                else:
                    v = value_result.value
            data[k] = v
        return FieldResult(data)

    def dump(self, value):
        return self.load(value)


class Enum(Field):
    def __init__(self, nested, allowed_values, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def dump(self, value):
        return self.load(value)


class Email(Field):
    def load(self, value):
        if isinstance(value, str):
            value = value.lower()
            if not RE_EMAIL.match(value):
                return FieldResult(error='not a valid e-mail address')
            return FieldResult(value=value)
        else:
            return FieldResult(error='expected an e-mail address')

    def dump(self, value):
        return self.load(value)


class Uuid(Field):

    _random_atfork = True
    _random = Random.new()

    @classmethod
    def next_uuid(cls, as_hex=False):
        Random.atfork()
        uuid = UUID(bytes=cls._random.read(16))
        return uuid if not as_hex else uuid.hex

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
        if isinstance(value, str):
            return FieldResult(value=value.replace('-', '').lower())
        if isinstance(value, UUID):
            return FieldResult(value=value.hex)
        else:
            return FieldResult(
                error='expected a valid UUID object or hex string'
            )

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

    def dump(self, value):
        return self.load(value)


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

    def dump(self, value):
        return self.load(value)


class DateTime(Field):
    def __init__(self, format_spec: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_spec = format_spec

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

    def dump(self, value):
        result = self.load(value)
        # format string exists, use it with strptime
        if self.format_spec:
            result.value = datetime.strftime(result.value, self.format_spec)
        # default dump format is as a unix timestamp
        else:
            result.value = to_timestamp(result.value)
        return result


class Bool(Field):
    TRUTHY = {'T', 't', 'True', 'true', 1}
    FALSEY = {'F', 'f', 'False', 'false', 0}

    def load(self, value):
        if isinstance(value, bool):
            return FieldResult(value=value)
        if value in self.TRUTHY:
            return FieldResult(value=True)
        if value in self.FALSEY:
            return FieldResult(value=False)
        return FieldResult(error='unable to cast value as boolean')

    def dump(self, value):
        return self.load(value)
