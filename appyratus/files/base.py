from __future__ import absolute_import

import os

from typing import Set, Text


class BaseFile(object):
    @classmethod
    def exists(cls, path: str):
        return os.path.exists(path)

    @staticmethod
    def extensions() -> Set[Text]:
        raise NotImplementedError('override in subclass')

    def read(cls, path: str):
        """
        Read the contents of a file from it's destination
        """
        raise NotImplementedError('override in subclass')

    def write(cls, path: str, data, encode: bool = True):
        """
        Write the contents to a file's destination
        """
        raise NotImplementedError('override in subclass')

    def load(cls, data):
        """
        Load contents into a Python data structure
        """
        raise NotImplementedError('override in subclass')

    def dump(cls, data):
        """
        Dump the contents of a python data structure to the expected format
        """
        raise NotImplementedError('override in subclass')


class File(BaseFile):

    UTF_ENCODINGS = {'utf-8', 'utf-16'}

    @classmethod
    def exists(cls, path: str):
        return os.path.exists(path)

    @classmethod
    def read(cls, path: str):
        if not cls.exists(path):
            return

        data = None
        is_read_success = False

        for encoding in cls.UTF_ENCODINGS:
            try:
                with open(path, encoding=encoding) as contents:
                    data = contents.read()
                    is_read_success = True
                    break
            except:
                pass

        if not is_read_success:
            raise IOError(
                'could not open {}. the file must be '
                'encoded in any of the following formats: '
                '{}'.format(path, ', '.join(cls.UTF_ENCODINGS))
            )

        return data

    @classmethod
    def write(cls, path: str, data=None, encode=True):
        with open(path, 'wb') as write_bytes:
            file_data = data.encode() if encode else data
            write_bytes.write(file_data)

    @classmethod
    def load(cls, data: Text):
        return data

    @classmethod
    def dump(cls, data: Text):
        return data

    @classmethod
    def dir_path(cls, path):
        return os.path.dirname(os.path.realpath(path))
