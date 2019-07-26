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

    def write(cls, path: Text, data):
        json = cls.dump(data)
        cls.write(json)

    @classmethod
    def load(cls, data):
        return ujson.loads(data) if data else None

    @classmethod
    def dump(cls, data):
        return ujson.dumps(data)
