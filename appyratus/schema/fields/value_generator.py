import re

import inflect

from typing import Type, Callable, Text, Dict

RE_FIELD_NAME_SUFFIX = re.compile(r'^.+_([^_]+)$')


class ValueGenerator(object):
    """
    Used to generate field values when generating fixtures.
    """

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
