from __future__ import absolute_import

import os
import yaml
import json
import io
import csv
import configparser

from abc import abstractclassmethod


class BaseFile(object):
    @classmethod
    def exists(cls, file_path: str):
        return os.path.exists(file_path)

    @abstractclassmethod
    def read(cls, file_path: str):
        pass

    @abstractclassmethod
    def write(cls, file_path: str, contents):
        pass

    @abstractclassmethod
    def from_file(cls, file_path: str, *args, **kwargs):
        pass

    @abstractclassmethod
    def to_file(cls, file_path: str, contents, *args, **kwargs):
        pass

    @abstractclassmethod
    def load(cls, data):
        pass

    @abstractclassmethod
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

    @classmethod
    def from_file(cls, file_path: str):
        return cls.read(file_path)

    @classmethod
    def to_file(cls, file_path: str, contents):
        cls.write(file_path, contents)
