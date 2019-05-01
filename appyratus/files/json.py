from __future__ import absolute_import

import ujson

from .base import BaseFile, File


class Json(BaseFile):

    @staticmethod
    def extensions():
        return {'json'}

    @classmethod
    def load_file(cls, file_path):
        data = File.read(file_path)
        return ujson.loads(data) if data else None

    @classmethod
    def dump(cls, content):
        return ujson.dumps(content)
