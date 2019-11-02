from __future__ import absolute_import

from typing import Text

from appyratus.utils import PathUtils

from .base import BaseFile


class File(BaseFile):
    """
    # File
    """

    UTF_ENCODINGS = {'utf-8', 'utf-16'}

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
    def name(self):
        return PathUtils.get_name(self.path)

    @property
    def filename(self):
        return PathUtils.get_filename(self.path)

    @property
    def extension(self):
        return PathUtils.get_extension(self.path)

    @property
    def dir_path(self):
        return PathUtils.get_dir_path(self.path)
