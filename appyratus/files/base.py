from __future__ import absolute_import

import os

from typing import Set, Text


class BaseFile(object):

    @classmethod
    def exists(cls, file_path: str):
        return os.path.exists(file_path)

    @staticmethod
    def extensions() -> Set[Text]:
        raise NotImplementedError('override in subclass')

    def read(cls, file_path: str):
        raise NotImplementedError('override in subclass')

    def write(cls, file_path: str, contents):
        raise NotImplementedError('override in subclass')

    def from_file(cls, file_path: str, *args, **kwargs):
        raise NotImplementedError('override in subclass')

    def to_file(cls, file_path: str, contents, *args, **kwargs):
        raise NotImplementedError('override in subclass')

    def load(cls, data):
        raise NotImplementedError('override in subclass')

    def dump(cls, data):
        raise NotImplementedError('override in subclass')

class File(BaseFile):

    UTF_ENCODINGS = {'utf-8', 'utf-16'}

    @classmethod
    def exists(cls, file_path: str):
        return os.path.exists(file_path)

    @classmethod
    def read(cls, file_path: str):
        if not cls.exists(file_path):
            return

        data = None
        is_read_success = False

        for encoding in cls.UTF_ENCODINGS:
            try:
                with open(file_path, encoding=encoding) as contents:
                    data = contents.read()
                    is_read_success = True
                    break
            except:
                pass

        if not is_read_success:
            raise IOError(
                'could not open {}. the file must be '
                'encoded in any of the following formats: '
                '{}'.format(
                    file_path, ', '.join(cls.UTF_ENCODINGS)
                )
            )

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
