import re

from typing import Set
from abc import ABCMeta, abstractmethod


class Enum(tuple):
    """
    This implementation of Enum is derived from `tuple` so it can be used as
    an argument to functions that expect a simple sequence of values.
    Internally, the key-value pairs are kept in a auxiliary dict, which
    provides O(1) lookup in place of the tuple's O(N) lookup.
    """

    @classmethod
    def of_strings(cls, *keys, name=None):
        """
        Return an enum where the keys and values are mapped 1-1.

        Args:
            - `keys`: a sequence of strings.
        """
        value_map = {}

        for key in keys:
            assert isinstance(key, str)
            value_map[key.lower()] = key

        return cls(value_map, name=name)

    def __new__(cls, value_map: dict=None, name=None, **value_map_kwargs):
        return super().__new__(cls,
            set((value_map or {}).values()) | set(value_map_kwargs.values())
        )

    def __init__(self, value_map: dict=None, name=None, **value_map_kwargs):
        super().__init__()
        self._name = name
        self._value_map = value_map or {}
        self._value_map.update(value_map_kwargs)
        self._value_map = {
            k.lower(): v for k, v in self._value_map.items()
        }

    def __getattr__(self, key: str):
        if key.startswith('__'):
            raise AttributeError(key)
        return self._value_map[key.lower()]

    def __getitem__(self, key: str):
        return self._value_map[key.lower()]

    def __contains__(self, key: str):
        return key in self._value_map.values()

    @property
    def name(self):
        return self._name


class EnumValueMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        ABCMeta.__init__(cls, name, bases, dct)
        if name == 'EnumValue':
            return

        setattr(cls, '_is_cls_init', False)
        setattr(cls, '_impl', cls.impl())
        setattr(cls, '_allowed_values', set())
        setattr(cls, '_value2name', {})

        for k, v in cls.values().items():
            if isinstance(v, cls._impl):
                _v = cls(v)
                cls._allowed_values.add(_v)
                cls._value2name[_v] = k
                setattr(cls, k, _v)

        cls._is_cls_init = True


class EnumValue(object, metaclass=EnumValueMeta):

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
        return cls._value2name[cls(value)]

    def __init__(self, value, *args, **kwargs):
        if self._is_cls_init and value not in self._allowed_values:
            raise NoSuchEnumValueError(self, value)

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
            '{} does not recognize {} as an allowed value.'.format(
                enum_value.__class__.__name__, illegal_value
            ))


class IllegalEnumValueError(EnumValueError):
    def __init__(self, enum_value_class, illegal_value):
        super().__init__(
            '{0} does not recognize {1} as an allowed value '
            'because it has the wrong type. Got {2}, expects {3}.'.format(
                enum_value_class.__name__,
                illegal_value,
                type(illegal_value),
                enum_value_class.impl(),
            ))
