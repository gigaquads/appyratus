import re

from abc import ABCMeta, abstractmethod


class TypeCodeMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        ABCMeta.__init__(cls, name, bases, dct)
        if name == 'TypeCode':
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


class TypeCode(object, metaclass=TypeCodeMeta):

    @staticmethod
    @abstractmethod
    def impl() -> type:
        return None

    @staticmethod
    @abstractmethod
    def values() -> {}:
        return {}

    @classmethod
    def to_name(cls, value):
        return cls._value2name[cls(value)]

    def __init__(self, value, *args, **kwargs):
        if self._is_cls_init and value not in self._allowed_values:
            raise NoSuchTypeCodeError(self, value)

    @property
    def name(self):
        return self.to_name(self)


class TypeCodeStr(str, TypeCode):

    def impl():
        return str

    def __repr__(self):
        return '<{}({})>'.format(
            self.__class__.__name__, super().__str__()
        )

    def __str__(self):
        return repr(self)


class TypeCodeInt(int, TypeCode):

    def impl():
        return int

    def __repr__(self):
        return '<{}({})>'.format(
            self.__class__.__name__, super().__str__()
        )

    def __str__(self):
        return repr(self)


class TypeCodeError(Exception):
    pass


class NoSuchTypeCodeError(TypeCodeError):
    def __init__(self, code: TypeCode, illegal_value):
        super().__init__(
            '{} does not recognize {} as an allowed value.'.format(
                code.__class__.__name__, illegal_value
            ))


class IllegalTypeCodeError(TypeCodeError):
    def __init__(self, code_class, illegal_value):
        super().__init__(
            '{0} does not recognize {1} as an allowed value '
            'because it has the wrong type. Got {2}, expects {3}.'.format(
                code_class.__name__,
                illegal_value,
                type(illegal_value),
                code_class.impl(),
            ))
