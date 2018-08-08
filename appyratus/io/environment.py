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
        result = self.load({k.lower(): v for k, v in os.environ.items()})
        if result.errors:
            raise EnvironmentValidationError(result.errors)
        self._data = result.data
        for k, v in result.data.items():
            setattr(self, k, v)

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
