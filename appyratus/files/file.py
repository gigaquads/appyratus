from __future__ import absolute_import

from typing import Text

from appyratus.logging import logger
from appyratus.utils import PathUtils

from .base import BaseFile


class File(BaseFile):
    """
    # File
    """
    ENCODINGS = {'utf-8', 'utf-16', 'ascii', 'latin'}

    @staticmethod
    def extensions():
        return {}

    @classmethod
    def get_data(cls, path, **settings):
        is_read_success = False
        data = None
        try:
            with open(path, **settings) as contents:
                data = contents.read()
                is_read_success = True
        except Exception as exc:
            logger.warning(exc)
        return is_read_success, data

    @classmethod
    def decode_data(cls, data, encoding):
        result = None
        is_decoded = False
        try:
            result = data.decode(encoding)
            is_decoded = True
        except Exception as exc:
            logger.warning(exc)
        return is_decoded, result

    @classmethod
    def read(cls, path: Text, is_binary: bool = None, **kwargs):
        if not cls.exists(path):
            return

        data = None
        is_read_success = False
        is_binary = True if is_binary else False
        # todo look for binary file checker that supports utf/ascii/latin
        do_read_binary = is_binary

        if do_read_binary:
            is_read_success, raw_data = cls.get_data(path, mode='rb')
            is_decoded = None
            if is_read_success:
                for encoding in cls.ENCODINGS:
                    is_decoded, data = cls.decode_data(raw_data, encoding)
                    if is_decoded:
                        break
                if not is_decoded:
                    raise IOError(
                        'could not decode {}. the file must be '
                        'encoded in any of the following formats: '
                        '{}'.format(path, ', '.join(cls.ENCODINGS))
                    )

        else:
            for encoding in cls.ENCODINGS:
                is_read_success, data = cls.get_data(path, mode='r', encoding=encoding)
                if is_read_success:
                    break

        if not is_read_success:
            raise IOError(
                'could not open {}. the file must be '
                'encoded in any of the following formats: '
                '{}'.format(path, ', '.join(cls.ENCODINGS))
            )

        return data

    @classmethod
    def write(cls, path: Text, data=None, encode=True, **kwargs):
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
    def prettify(cls, data: Text):
        return data


class FileObject(object):

    @classmethod
    def get_file_type(cls):
        raise NotImplementedError('implement in subclass')

    def __init__(self, path: Text = None, data=None, **kwargs):
        self._path = path
        self._data = data

    @property
    def path(self):
        return self._path

    @property
    def data(self):
        return self._data

    def read(self):
        self._data = self.get_file_type().read(self.path)
        return self._data

    def write(self):
        self.get_file_type.write(self.path, self.data)

    @property
    def file_name(self):
        return PathUtils.get_file_name(self.path)

    @property
    def name(self):
        return PathUtils.get_name(self.path)

    @property
    def extension(self):
        return PathUtils.get_extension(self.path)

    @property
    def dir_path(self):
        return PathUtils.get_dir_path(self.path)

    @property
    def dir_name(self):
        return PathUtils.get_dir_name(self.path)

