from __future__ import absolute_import
import ast
import astor

from typing import Dict

from .base import File


class Python(File):
    @staticmethod
    def extensions():
        return {'py'}

    @classmethod
    def format_file_name(cls, basename):
        return f'{basename}.py'

    @classmethod
    def from_file(cls, file_path: str):
        return cls.load_file(file_path)

    @classmethod
    def from_string(cls, data: str):
        return cls.load_string(data)

    @classmethod
    def load_file(cls, file_path: str):
        data = cls.read(file_path)
        if not data:
            return
        return cls.load_string(data)

    @classmethod
    def load_string(cls, data: str):
        """
        # Load String
        Load a string of python code into AST
        """
        return ast.parse(data)

    @classmethod
    def to_file(cls, file_path: str, contents=None):
        with open(file_path, 'wb') as python_file:
            import ipdb; ipdb.set_trace(); print('=' * 100)
            data = cls.dump_data(contents) if contents else ''
            python_file.write(data.encode())

    @classmethod
    def dump_data(cls, data: Dict):
        return astor.to_source(data)
