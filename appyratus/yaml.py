import os
import yaml


class Yaml(object):
    @classmethod
    def from_file(cls, file_path: str):
        if not os.path.exists(file_path):
            return
        with open(file_path) as yaml_file:
            data = yaml.load(yaml_file.read())
            return data

    @classmethod
    def to_file(cls, file_path: str, data=None):
        with open(file_path, 'wb') as yaml_file:
            data = yaml.dump(data)
            yaml_file.write(data)

    @classmethod
    def format_file_name(cls, file_name):
        return "{}.yml".format(file_name)
