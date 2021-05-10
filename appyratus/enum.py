import re

from typing import Set, Tuple
from abc import ABCMeta, abstractmethod

from appyratus.utils.type_utils import TypeUtils


class Enum(tuple):
    """
    This implementation of Enum is derived from `tuple` so it can be used as
    an argument to functions that expect a simple sequence of values.
    Internally, the key-value pairs are kept in a auxiliary dict, which
    provides O(1) lookup in place of the tuple's O(N) lookup.
    """

    @classmethod
    def of_strings(cls, *keys, name=None, default=None):
        """
        Return an enum where the keys and values are mapped 1-1.

        Args:
            - `keys`: a sequence of strings.
        """
        value_map = {}

        for key in keys:
            assert isinstance(key, str)
            value_map[key.lower()] = key

        enum = cls(value_map, name=name)
        enum.default = default
        return enum

    def __new__(cls, value_map: dict=None, name=None, **value_map_kwargs):
        return super().__new__(cls,
            set((value_map or {}).values()) | set(value_map_kwargs.values())
        )

    def __init__(
        self,
        value_map: dict=None,
        name=None,
        default=None,
        **value_map_kwargs
    ):
        super().__init__()
        self.default = default
        self._name = name
        self._value_map = value_map or {}
        self._value_map.update(value_map_kwargs)
        self._value_map = {
            self._normalize_key(k): v for k, v in self._value_map.items()
        }

    def __repr__(self):
        name = self._name or TypeUtils.get_class_name(self)
        return f'Enum({name})'

    def __getattr__(self, key: str):
        if key.startswith('__'):
            raise AttributeError(key)
        return self._value_map[self._normalize_key(key)]

    def __getitem__(self, key: str):
        return self._value_map[self._normalize_key(key)]

    def __contains__(self, key: str):
        return self._normalize_key(key) in self._value_map.values()

    def validate(self, value, ignore_case=True):
        if ignore_case and isinstance(value, str):
            value = value.upper()
            if value not in {x.upper() for x in self._value_map}:
                raise ValueError(f'{self} does not recognize value: {value}')
        else:
            if value not in self:
                raise ValueError(f'{self} does not recognize value: {value}')
        return value

    @staticmethod
    def _normalize_key(key):
        return key.replace('-', '_').lower()

    @property
    def name(self):
        return self._name

    def to_tuple(self) -> Tuple:
        return tuple(self._value_map.values())


class EnumValueMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        ABCMeta.__init__(cls, name, bases, dct)
        if name == 'EnumValue':
            return

        setattr(cls, '_is_cls_init', False)
        setattr(cls, '_impl', cls.impl())
        setattr(cls, '_allowed_values', set())
        setattr(cls, '_value2name', {})
        setattr(cls, '_name2value', {})

        values = cls.values()

        if isinstance(values, (set, list, tuple)):
            # do this for EnumValueStr specifically so that we don't have to
            # return something like {'foo': 'foo', 'bar': 'bar'}
            values = {k: k for k in values}

        for k, v in values.items():
            k = cls.get_normalized_key(k)
            if isinstance(v, cls._impl):
                cls._allowed_values.add(v)
                cls._name2value[k] = v
                cls._value2name[v] = k
                setattr(cls, k, v)

        cls._is_cls_init = True


class EnumValue(object, metaclass=EnumValueMeta):

    RE_NON_WORD = re.compile(r'\W+')

    @staticmethod
    @abstractmethod
    def impl() -> type:
        return None

    @staticmethod
    @abstractmethod
    def values() -> Set:
        return {}

    @classmethod
    def to_name(cls, value):
        return cls._value2name.get(cls(value))

    @classmethod
    def validate(cls, value):
        if value not in cls._value2name:
            raise EnumValueError(str(value))

    @classmethod
    def get_normalized_key(cls, key):
        return cls.RE_NON_WORD.sub('_', key.lower())

    def __init__(self, value, *args, **kwargs):
        if self._is_cls_init and value not in self._allowed_values:
            raise NoSuchEnumValueError(self, value)

    def __eq__(self, other):
        return self == cls(other)

    def __neq__(self, other):
        return self == cls(other)

    def __le__(self, other):
        return self < cls(other)

    def __leq__(self, other):
        return self <= cls(other)

    def __geq__(self, other):
        return self >= cls(other)

    def __ge__(self, other):
        return self > cls(other)

    @property
    def name(self):
        return self.to_name(self)


class EnumValueStr(str, EnumValue):

    def impl():
        return str

    def __repr__(self):
        return '<{}({})>'.format(
            self.__class__.__name__, super().__str__()
        )

    def __str__(self):
        return repr(self)

    def __getattr__(self, name):
        raise EnumValueError(name)


class EnumValueInt(int, EnumValue):

    def impl():
        return int

    def __repr__(self):
        return '<{}({})>'.format(
            self.__class__.__name__, super().__str__()
        )

    def __str__(self):
        return repr(self)


class EnumValueError(Exception):
    pass


class NoSuchEnumValueError(EnumValueError):
    def __init__(self, enum_value: EnumValue, illegal_value):
        super().__init__(
            '{} does not recognize "{}" as an allowed value.'.format(
                enum_value.__class__.__name__, illegal_value
            ))


class IllegalEnumValueError(EnumValueError):
    def __init__(self, enum_value_class, illegal_value):
        super().__init__(
            '{0} does not recognize "{1}" as an allowed value '
            'because it has the wrong type. Got {2}, expects {3}.'.format(
                enum_value_class.__name__,
                illegal_value,
                type(illegal_value),
                enum_value_class.impl(),
            ))
