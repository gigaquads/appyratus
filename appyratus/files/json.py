from __future__ import absolute_import
from typing import Text

import ujson

from .base import File


class Json(File):
    @staticmethod
    def extensions():
        return {'json'}

    @classmethod
    def read(cls, path: Text):
        data = super().read(path)
        return cls.load(data)

    def write(cls, path: Text, data=None, **kwargs):
        file_data = cls.dump(data, **kwargs)
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data):
        return ujson.loads(data) if data else None

    @classmethod
    def dump(cls, data, indent: int = 2, sort_keys: bool = True, **kwargs):
        return ujson.dumps(data, indent=indent, sort_keys=sort_keys)
