from __future__ import absolute_import

import yaml

from .base import BaseFile


class Yaml(BaseFile):
    @classmethod
    def from_file(cls, file_path: str, multi=False):
        try:
            if not multi:
                return cls.load_file(file_path)
        except yaml.composer.ComposerError:
            multi = True
        if multi:
            return cls.load_all_file(file_path)

    @classmethod
    def load_file(cls, file_path):
        data = File.read(file_path)
        if not data:
            return
        return yaml.load(data)

    @classmethod
    def load_all_file(cls, file_path):
        data = File.read(file_path)
        if not data:
            return []
        docs = yaml.load_all(data)
        if not docs:
            return []
        return [doc for doc in docs]

    @classmethod
    def to_file(cls, file_path: str, data=None, multi=False):
        with open(file_path, 'wb') as yaml_file:
            yaml_args = dict(
                default_flow_style=False,
                explicit_start=True,
                explicit_end=True
            )
            if multi:
                data = yaml.dump_all(data, **yaml_args)
            else:
                data = yaml.dump(data, **yaml_args)
            yaml_file.write(data.encode())

    @classmethod
    def format_file_name(cls, file_name):
        return "{}.yml".format(file_name)
