from __future__ import absolute_import
import ast
import astor

from typing import Dict

from .base import File


class PythonModule(File):
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
        """
        # To File
        """
        with open(file_path, 'wb') as python_file:
            source = cls.to_source(contents) if contents else ''
            python_file.write(source.encode())

    @classmethod
    def to_source(cls, ast):
        """
        # Dump Source
        Dump AST to source code
        """
        return astor.to_source(ast)
