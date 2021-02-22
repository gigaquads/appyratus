from __future__ import absolute_import

import re
from typing import (
    Dict,
    Text,
)

import yaml

from yaml import FullLoader
from appyratus.enum import Enum

from .file import (
    File,
    FileObject,
)

EXTENSIONS = Enum.of_strings('yml', 'yaml')


class Yaml(File):
    """
    # Yaml
    Yaml file type

    # References
    https://pyyaml.org/wiki/PyYAMLDocumentation
    """

    @classmethod
    def extensions(cls):
        return {v for v in EXTENSIONS}

    @classmethod
    def default_extension(cls):
        return EXTENSIONS.YML

    @classmethod
    def read(cls, path: Text, multi=False, loader_class=FullLoader):
        try:
            with open(path) as yaml_file:
                return cls.load(
                    yaml_file, multi=multi, loader_class=loader_class
                )
        except yaml.composer.ComposerError:
            # this should occur when you attempt to load in a yaml file that
            # that contains multiple documents and you did not specify multiple
            with open(path) as yaml_file:
                return cls.load(
                    yaml_file, multi=True, loader_class=loader_class
                )

    @classmethod
    def write(cls, path: Text, data=None, multi=False, **kwargs):
        file_data = cls.dump(data, multi=multi)
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data=None, multi: bool = False, loader_class=FullLoader):
        load_args = {'Loader': loader_class}
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
    def dump(
        cls,
        data,
        multi: bool = False,
        default_flow_style: bool = None,
        explicit_start: bool = None,
        explicit_end: bool = None,
        indent: int = None
    ):
        dump_args = {
            'default_flow_style': default_flow_style if default_flow_style else False,
            'explicit_start': explicit_start if explicit_start is not None else True,
            'explicit_end': explicit_end if explicit_end is not None else True,
            'indent': indent if indent is not None else 2,
        }
        # here as a last defense we should check if this data is yaml construct
        # otherwise a string of yaml erroneously dumped will result in a
        # document with a a list of characters from that dumped string
        if not cls.is_dumped(data):
            if multi:
                data = yaml.dump_all(data, **dump_args)
            else:
                data = yaml.dump(data, **dump_args)
        return data

    @staticmethod
    def is_dumped(data) -> bool:
        """
        # Is Dumped
        Checks for explicit YAML document "---" prefix)
        """
        r_header = r"^---\n"
        dumped = False
        if isinstance(data, str):
            # we check here to see if the string has
            match = re.match(r_header, data)
            if match:
                dumped = True
            # TODO an intensive check would be to load the data and capture any
            # exceptions- if loaded without error then that is an expensive
            # indication that the string is yaml
        return dumped


class YamlFileObject(FileObject):

    @classmethod
    def get_file_type(cls):
        return Yaml
