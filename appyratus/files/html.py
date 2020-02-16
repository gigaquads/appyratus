from __future__ import absolute_import
from bs4 import BeautifulSoup
import ast
import astor

from typing import Text

from .file import File


class Html(File):
    @staticmethod
    def extensions():
        return {'htm', 'html'}

    @classmethod
    def format_file_name(cls, basename):
        return f'{basename}.html'

    @classmethod
    def read(cls, path: Text):
        data = super().read(path)
        return cls.load(data)

    @classmethod
    def write(cls, path: Text, data=None, **kwargs):
        file_data= cls.dump(data) if data else ''
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data):
        if not data:
            return
        parser = cls.get_parser(data)
        return parser

    @classmethod
    def dump(cls, data):
        parser = cls.get_parser(data)
        return parser.prettify()
        pass

    @classmethod
    def get_parser(cls, data):
        return BeautifulSoup(data, features='html.parser')