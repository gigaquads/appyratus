import re

import inflect

from typing import Type, Callable, Text, Dict

RE_FIELD_NAME_SUFFIX = re.compile(r'^.+_([^_]+)$')


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

    def generate(self, field: 'Field', *args, **kwargs):
        """
        Apply a callback to generate a value for the given field, using its name
        to determine the callback.
        """
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
