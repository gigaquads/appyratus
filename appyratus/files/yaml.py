from __future__ import absolute_import
from typing import Dict, Text

import yaml
from appyratus.enum import Enum

from .file import File, FileObject

EXTENSIONS = Enum.of_strings('yml', 'yaml')


class Yaml(File):
    """
    # Yaml
    Yaml file type

    # References
    https://pyyaml.org/wiki/PyYAMLDocumentation
    """

    @staticmethod
    def extensions():
        return {v for v in EXTENSIONS}

    @staticmethod
    def default_extension():
        return EXTENSIONS.YML

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
    def load(cls, data=None, multi: bool = False):
        load_args = {'Loader': yaml.FullLoader}
        if data is None:
            return
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
        # TODO here as a last defense we should check here lamely if it is
        # already a yaml construct (with explicit --- prefix), otherwise a
        # string of yaml will dump as a list of characters in that string
        if multi:
            data = yaml.dump_all(data, **dump_args)
        else:
            data = yaml.dump(data, **dump_args)
        return data


class YamlFileObject(FileObject):

    @classmethod
    def get_file_type(cls):
        return Yaml
