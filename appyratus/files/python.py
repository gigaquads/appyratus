from __future__ import absolute_import
import ast
import astor

from typing import Text

from .base import File


class PythonModule(File):
    @staticmethod
    def extensions():
        return {'py'}

    @classmethod
    def format_file_name(cls, basename):
        return f'{basename}.py'

    @classmethod
    def read(cls, path: Text):
        data = super().read(path)
        return cls.load(data)

    @classmethod
    def write(cls, path: Text, data=None):
        source = cls.dump(data) if data else ''
        cls.write(source.encode())

    @classmethod
    def load(cls, data):
        if not data:
            return
        return ast.parse(data)

    @classmethod
    def dump(cls, data):
        return astor.to_source(data)
