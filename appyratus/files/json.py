from __future__ import absolute_import
from typing import Text

import ujson

from .base import BaseFile, File


class Json(File):

    @staticmethod
    def extensions():
        return {'json'}

    @classmethod
    def load_file(cls, file_path):
        return cls.read(file_path)

    @classmethod
    def dump(cls, content):
        return ujson.dumps(content)

    @classmethod
    def read(self, file_path: Text):
        data = File.read(file_path)
        return ujson.loads(data) if data else None
