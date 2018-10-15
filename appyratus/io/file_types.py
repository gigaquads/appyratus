from __future__ import absolute_import
from abc import abstractmethod

import os
import yaml
import json
import io
import csv
import configparser


class BaseFile(object):
    @classmethod
    def exists(cls, file_path: str):
        return os.path.exists(file_path)

    @abstractmethod
    def read(cls, file_path: str):
        pass

    @abstractmethod
    def write(cls, file_path: str, contents):
        pass

    @abstractmethod
    def from_file(cls, file_path: str, *args, **kwargs):
        pass

    @abstractmethod
    def to_file(cls, file_path: str, contents, *args, **kwargs):
        pass

    @abstractmethod
    def load(cls, data):
        pass

    @abstractmethod
    def dump(cls, data):
        pass


class File(BaseFile):
    @classmethod
    def exists(cls, file_path: str):
        return os.path.exists(file_path)

    @classmethod
    def read(cls, file_path: str):
        if not cls.exists(file_path):
            return

        data = None
        for encoding in ['utf-8', 'utf-16']:
            try:
                with open(file_path, encoding=encoding) as contents:
                    data = contents.read()
                    break
            except:
                pass
        return data

    @classmethod
    def write(cls, file_path: str, contents=None):
        with open(file_path, 'wb') as write_bytes:
            write_bytes.write(contents.encode())

    @classmethod
    def dir_path(cls, path):
        return os.path.dirname(os.path.realpath(path))


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


class Json(BaseFile):
    @classmethod
    def load_file(cls, file_path):
        data = File.read(file_path)
        if not data:
            return
        return json.loads(data)

    @classmethod
    def dump(cls, content):
        pass


class Ini(File):
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


class Csv(BaseFile):
    @classmethod
    def from_file(cls, file_path: str, delimiter: str=None):
        file_data = cls.load_file(file_path=file_path, delimiter=delimiter)
        return file_data

    @classmethod
    def load_file(cls, file_path: str, delimiter: str=None):
        file_data = File.read(file_path=file_path)
        csv_data = cls.data_from_blob(blob=file_data, delimiter=delimiter)
        return csv_data

    @classmethod
    def blob_from_data(cls, data):
        """
        Convert a list of dicts into a blob
        """
        # only interested in lists
        if not isinstance(data, list):
            return
        # and only if the first item is a dict
        if not isinstance(data[0], dict):
            return
        # store CSV data in memory
        output = io.StringIO('')
        # write header from dictionary keys
        fieldnames = data[0].keys()
        writer = csv.DictWriter(
            output, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC
        )
        writer.writeheader()
        # write row data
        for row in data:
            writer.writerow(row)
        csv_blob = output.getvalue()
        return csv_blob

    @classmethod
    def data_from_blob(cls, blob: str, delimiter=None):
        """
        Convert a csv blob into a list of dicts
        """
        buff = io.StringIO(blob)
        if not delimiter:
            delimiter = ','
        reader = csv.DictReader(buff, delimiter=delimiter)
        return [row for row in reader]
