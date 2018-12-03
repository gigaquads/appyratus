from __future__ import absolute_import

import ujson

from .base import File, BaseFile


class Json(BaseFile):
    @classmethod
    def load_file(cls, file_path):
        data = File.read(file_path)
        return ujson.loads(data) if data else None

    @classmethod
    def dump(cls, content):
        return ujson.dumps(content)
