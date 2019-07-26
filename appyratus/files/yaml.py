from __future__ import absolute_import
from typing import Dict, Text

import yaml

from .base import File


class Yaml(File):
    @staticmethod
    def extensions():
        return {'yml', 'yaml'}

    @classmethod
    def format_file_name(cls, basename):
        return f'{basename}.yml'

    @classmethod
    def read(cls, file_path: Text, multi=False):
        try:
            data = cls.read(file_path)
            return cls.load(data, multi=multi)
        except yaml.composer.ComposerError:
            # this should occur when you attempt to load in a yaml file that
            # that contains multiple documents and you did not specify multiple
            return cls.load(data, multi=True)

    @classmethod
    def write(cls, file_path: Text, contents=None, multi=False):
        with open(file_path, 'wb') as yaml_file:
            data = cls.from_data(data, multi=multi)
            yaml_file.write(data.encode())

    @classmethod
    def load(cls, data, multi: bool = False):
        load_args = {'Loader': yaml.FullLoader}
        if multi:
            return yaml.load_all(data, **load_args)
        else:
            if not data:
                return []
            docs = yaml.load(data, **load_args)
            return [doc for doc in docs]

    @classmethod
    def dump(cls, data, multi: bool = False):
        dump_args = {
            'default_flow_style': False,
            'explicit_start': True,
            'explicit_end': True
        }
        if multi:
            data = yaml.dump_all(data, **dump_args)
        else:
            data = yaml.dump(data, **dump_args)
        return data
