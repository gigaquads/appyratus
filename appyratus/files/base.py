from __future__ import absolute_import

import os
from typing import (
    Set,
    Text,
)

from appyratus.utils import FileUtils


class BaseFile(object):

    @classmethod
    def exists(cls, path: Text):
        return os.path.exists(path)

    @staticmethod
    def extensions() -> Set[Text]:
        raise NotImplementedError('override in subclass')

    @staticmethod
    def default_extension():
        """
        # Default Extension
        The default extension to be used when handling File types
        
        By default this will use the first extension in the sorted list of
        extensions bearing your File type provided it
        """
        extensions = self.extensions()
        if not extensions:
            return None
        return sorted(list(self.extensions()))[0]

    @staticmethod
    def has_extension(extension: Text):
        """
        # Has Extension
        If your File type has the appropriate extension registered in it.

        As there is normalizing of extension happening, it will return the
        normalized extension if one has been found, otherwise None
        """
        if not extension:
            return None
        extension = extension.lower()
        return extension in self.extensions()

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
        return FileUtils.get_name(self.path)

    @property
    def filename(self):
        return FileUtils.get_filename(self.path)

    @property
    def extension(self):
        return FileUtils.get_extension(self.path)

    @property
    def dir_path(self):
       return FileUtils.get_dir_path(self.path)
