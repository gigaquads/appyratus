import os
import re

from appyratus.exc import AppyratusError
from appyratus.schema import Schema


class EnvironmentError(AppyratusError):
    pass


class UndefinedVariableError(EnvironmentError):
    pass


class EnvironmentValidationError(EnvironmentError):
    def __init__(self, errors):
        super().__init__(str(errors))
        self.errors = errors


class Environment(Schema):
    def __init__(self):
        super().__init__()
        raw_data = os.environ.copy()
        data, errors = self.process(raw_data)
        if not errors:
            self.data = raw_data
            self.data.update(data)
        else:
            raise EnvironmentValidationError(errors)

    def __getitem__(self, key):
        return self._data.get(key, self._raw_data.get(key))

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
