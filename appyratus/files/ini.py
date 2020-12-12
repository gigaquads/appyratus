from __future__ import absolute_import
from typing import Text
import io
import configparser

from appyratus.utils.dict_utils import DictUtils

from .file import File


class Ini(File):
    """
    # Ini File Type
    """

    @classmethod
    def extensions(cls):
        return {'ini', 'cfg'}

    @classmethod
    def read(cls, path: Text):
        file_data = super().read(path=path)
        ini_data = cls.load(file_data)
        return ini_data

    @classmethod
    def write(cls, path: Text, data=None, **kwargs):
        file_data = cls.dump(data)
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data, list_format: Text = None):
        config = configparser.ConfigParser()
        config.read_string(data)
        ini_data = dict(config._sections)
        for k in ini_data:
            ini_data[k] = dict(config._defaults, **ini_data[k])
            ini_data[k].pop('__name__', None)
        ini_data = DictUtils.traverse(ini_data, cls.load_value, list_format=list_format)
        return ini_data

    @staticmethod
    def load_value(key, value, list_format: Text = None, depth: int = None):
        if not list_format:
            list_format = 'dangling'
        separator = None
        if list_format == 'dangling':
            separator = "\n"
        elif list_format == 'csv':
            separator = ","
        if separator and separator in value:
            value = [v for v in value.split(separator) if v]
        return value

    @staticmethod
    def dump_value(key, value=None, list_format: Text = None, depth: int = None):
        if not list_format:
            list_format = 'dangling'
        if isinstance(value, list):
            if list_format == 'dangling':
                value = "\n{}".format('\n'.join(value))
            elif list_format == 'csv':
                value = ','.join(value)
        return value

    @classmethod
    def dump(cls, data, list_format: Text = None):
        data = DictUtils.traverse(data, cls.dump_value, list_format=list_format)
        data = DictUtils.remove_keys(data, empty_values={type(None)})
        output = io.StringIO()
        config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation()
        )
        config.read_dict(data)
        config.write(output)
        return output.getvalue()
