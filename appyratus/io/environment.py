import os
import re

from appyratus.exc import AppyratusError
from appyratus.validation import Schema


class EnvironmentError(AppyratusError):
    pass


class UndefinedVariableError(EnvironmentError):
    pass


class EnvironmentValidationError(EnvironmentError):
    pass


class Environment(Schema):
    def __init__(self):
        super().__init__(strict=False, allow_additional=True)
        result = self.load(os.environ)
        if result.errors:
            raise EnvironmentValidationError(result.errors)
        self._data = result.data

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        clean_key = key.upper()
        if clean_key in self._data:
            return self._data[clean_key]
        else:
            return os.environ[clean_key]

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
