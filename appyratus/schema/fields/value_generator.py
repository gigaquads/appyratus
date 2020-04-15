import re

import inflect

from types import MethodType
from typing import Type, Callable, Text, Dict, List, Set

RE_FIELD_NAME_SUFFIX = re.compile(r'^.+_([^_]+)$')


class Bounds(object):
    def __init__(
        self,
        lower=None,
        upper=None,
        lower_inclusive=True,
        upper_inclusive=False,
        exclude: Set = None,
    ):
        self.lower = lower
        self.upper = upper
        self.lower_inclusive = lower_inclusive
        self.upper_inclusive = upper_inclusive
        self.exclude = set(exclude) if not isinstance(exclude, set) else exclude


class ValueGenerator(object):
    """
    ValueGenerator is used internally to generate values for Field when
    generating data for test fixtures and such.
    """

    def __init__(self, callbacks: Dict[Text, Callable] = None, default: Callable = None):
        self.default = default or (lambda field, *args, **kwargs: None)
        self.callbacks = callbacks or {}
        self.inflect = inflect.engine()

    def register(self, field_name: Text, callback: Callable):
        """
        Register a callback. The `field_name` arg is the name of the field that
        triggers the callback.
        """
        self.callbacks[field_name] = callback

    def unregister(self, field_name: Text) -> Callable:
        """
        Unregister a callback.
        """
        return self.callbacks.pop(field_name, None)

    def generate(
        self,
        field: 'Field',
        bounds: Bounds = None,
        **kwargs
    ):
        """
        Apply a callback to generate a value for the given field, using its name
        to determine the callback.
        """
        if field.name is None or (bounds is not None):
            if bounds is None:
                func = field.on_generate
            else:
                func = field.on_generate_range
                kwargs['bounds'] = bounds
        else:
            func = self.callbacks.get(field.name, field.on_generate)
            if func is self.default:
                singular_name = self.inflect.singular_noun(field.name)
                func = self.callbacks.get(singular_name, self.default)
            if func is self.default:
                match = RE_FIELD_NAME_SUFFIX.match(field.name)
                if match:
                    name = match.groups()[0]
                    func = self.callbacks.get(name, field.on_generate)

        # if func resolves to the instance method, don't pass "field"
        # as the first positional argument to the on_generate* callback
        if (
            isinstance(func, MethodType) and
            isinstance(func.__self__, type(field))
        ):
            return func(**kwargs)
        else:
            return func(field, **kwargs)
