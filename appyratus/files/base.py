from __future__ import absolute_import

from typing import (
    Set,
    Text,
)

from appyratus.utils.path_utils import PathUtils



class BaseFile(object):

    @classmethod
    def exists(cls, path: Text):
        return PathUtils.exists(path)

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

    def read(cls, path: str, **kwargs):
        """
        Read the contents of a file from it's destination
        """
        raise NotImplementedError('override in subclass')

    def write(cls, path: str, data, encode: bool = True, **kwargs):
        """
        Write the contents to a file's destination
        """
        raise NotImplementedError('override in subclass')

    def load(cls, data, **kwargs):
        """
        Load contents into a Python data structure
        """
        raise NotImplementedError('override in subclass')

    def dump(cls, data, **kwargs):
        """
        Dump the contents of a python data structure to the expected format
        """
        raise NotImplementedError('override in subclass')

    def prettify(cls, data, **kwargs):
        """
        Perform superficial prettification of provided data
        """
        raise NotImplementedError('override in subclass')

