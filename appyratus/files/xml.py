from __future__ import absolute_import

import xml.etree.ElementTree as ET
from io import StringIO
from typing import Text

from .file import File


class Xml(File):
    """
    # XML File Type
    """

    @classmethod
    def extensions(cls):
        return {'xml'}

    @classmethod
    def format_file_name(cls, basename):
        return f'{basename}.xml'

    @classmethod
    def get_parser(cls):
        return ET

    @classmethod
    def read(cls, path: Text):
        data = super().read(path)
        return cls.load(data)

    @classmethod
    def write(cls, path: Text, data=None, **kwargs):
        file_data = cls.dump(data) if data else ''
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data=None):
        if not data:
            return
        parser = cls.get_parser().parse(StringIO(data))
        return parser

    @classmethod
    def dump(cls, data):
        return cls.get_parser().tostring(data)
