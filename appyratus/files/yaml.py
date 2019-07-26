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
    def read(cls, path: Text, multi=False):
        try:
            data = super().read(path)
            return cls.load(data, multi=multi)
        except yaml.composer.ComposerError:
            # this should occur when you attempt to load in a yaml file that
            # that contains multiple documents and you did not specify multiple
            return cls.load(data, multi=True)

    @classmethod
    def write(cls, path: Text, data=None, multi=False, **kwargs):
        file_data = cls.dump(data, multi=multi)
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data, multi: bool = False):
        load_args = {'Loader': yaml.FullLoader}
        if multi:
            if not data:
                return []
            docs = yaml.load_all(data, **load_args)
            # a generator comes back
            return [doc for doc in docs]
        else:
            return yaml.load(data, **load_args)

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
