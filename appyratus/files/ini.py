from __future__ import absolute_import

import io
import configparser

from .base import File


class Ini(File):
    @staticmethod
    def extensions():
        return {'ini'}

    @classmethod
    def read(cls, path: Text):
        file_data = cls.read(path=path)
        ini_data = cls.load(file_data)
        return ini_data

    @classmethod
    def write(cls, path: Text, data):
        file_data = cls.dump(data)
        cls.write(path=path, data=file_data)

    @classmethod
    def load(cls, data):
        config = configparser.ConfigParser()
        config.read_string(data)
        ini_data = dict(config._sections)
        for k in ini_data:
            ini_data[k] = dict(config._defaults, **ini_data[k])
            ini_data[k].pop('__name__', None)
        return ini_data

    @classmethod
    def dump(cls, data):
        output = io.StringIO()
        config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation()
        )
        config.read_dict(data)
        config.write(output)
        return output.getvalue()
