import os
import re
import copy
import inspect

from appyratus.schema import Schema, Field


class EnvironmentError(Exception):
    pass


class UndefinedVariableError(EnvironmentError):
    pass


class EnvironmentValidationError(EnvironmentError):
    def __init__(self, errors):
        super().__init__(str(errors))
        self.errors = errors


class Environment(object):
    _data = {}
    _raw_data = {}

    def __init__(self, **fields):
        base_fields = {}
        for k, v in inspect.getmembers(
            self.__class__, predicate=lambda v: isinstance(v, Field)
        ):
            base_fields[k] = v

        merged_fields = dict(base_fields, **(fields or {}))

        self.schema_type = type('EnvironmentSchema', (Schema, ), merged_fields)
        self.schema = self.schema_type(allow_additional=True)

        data, errors = self.schema.process(dict(os.environ))
        if not errors:
            self._data.update(data)
        else:
            raise EnvironmentValidationError(errors)

        for k, v in self._data.items():
            setattr(self, k, v)

    def get(self, key, default=None, dtype=None):
        if key in self._data:
            value = self._data[key]
            return dtype(value) if dtype else value
        return default

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        return self._data.get(key)

    def __repr__(self):
        return '<Environment>'

    def __keys__(self):
        return self._data.keys()

    def __values__(self):
        return self._data.values()

    def __items__(self):
        return self._data.items()

    def __contains__(self, key):
        return key in self._data

    def __len__(self):
        return len(self._data)
