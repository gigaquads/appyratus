from __future__ import absolute_import

import io
import configparser

from .base import File


class Ini(File):

    @staticmethod
    def extensions():
        return {'ini'}

    @classmethod
    def from_file(cls, file_path: str):
        file_data = cls.load_file(file_path=file_path)
        return file_data

    @classmethod
    def to_file(cls, file_path: str, data):
        output = io.StringIO()
        config = configparser.ConfigParser()
        config.read_dict(data)
        config.write(output)
        cls.write(file_path=file_path, contents=output.getvalue())

    @classmethod
    def load_file(cls, file_path: str):
        file_data = cls.read(file_path=file_path)
        ini_data = cls.data_from_blob(blob=file_data)
        return ini_data

    @classmethod
    def data_from_blob(cls, blob: dict):
        config = configparser.ConfigParser()
        config.read_string(blob)
        d = dict(config._sections)
        for k in d:
            d[k] = dict(config._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

    @classmethod
    def blob_from_data(cls, data):
        config.write()
        pass
