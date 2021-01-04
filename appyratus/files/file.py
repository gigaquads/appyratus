from __future__ import absolute_import

from typing import Text

from appyratus.logging import logger
from appyratus.utils.path_utils import PathUtils

from .base import BaseFile


class File(BaseFile):
    """
    # Generic File Type
    """
    ENCODINGS = ('utf-8', 'utf-16', 'ascii', 'latin')

    @classmethod
    def extensions(cls):
        return {}

    @classmethod
    def default_extension(cls):
        return [*cls.extensions()].pop(0)

    @classmethod
    def format_file_name(cls, basename):
        return f'{basename}.{cls.default_extension()}'

    @classmethod
    def read(cls, path: Text, mode: Text = None, **kwargs):
        if not cls.exists(path):
            return

        data = None
        is_read_success = False
        mode = mode if mode else 'r'

        if mode == 'r':
            for encoding in cls.ENCODINGS:
                try:
                    logger.debug(f'loading {path} [{mode},{encoding}]')
                    with open(path, mode, encoding=encoding) as contents:
                        data = contents.read()
                    is_read_success = True
                    break
                except UnicodeError as exc:
                    logger.error(exc)
        elif mode == 'rb':
            # when specifying binary mode (rb) the open command cannot
            # accept an encoding argument
            try:
                logger.debug(f'loading {path} [{mode}]')
                with open(path, mode) as contents:
                    data = contents.read()
                is_read_success = True
            except UnicodeError as exc:
                logger.error(exc)

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
