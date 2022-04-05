import mimetypes
import os
import stat
from os import (
    chmod,
    makedirs,
    walk,
)
from os.path import (
    basename,
    dirname,
    exists,
    join,
    realpath,
    expanduser,
    splitext,
    relpath,
)
from shlex import shlex
from typing import (
    List,
    Text,
)


class PathUtils(object):
    """
    # Path Utils
    """

    @classmethod
    def get_file_name(cls, path: Text) -> Text:
        """
        # Get File Name
        """
        return basename(path)

    @classmethod
    def get_name(cls, path: Text) -> Text:
        """
        # Get Name
        """
        return splitext(cls.get_file_name(path))[0]

    @classmethod
    def get_extension(cls, path: Text) -> Text:
        """
        # Get Extension
        """
        try:
            file_name = cls.get_file_name(path)
            # splitext returns a tuple like `('file',
            # '.zip')`, or `('file.tar', '.gz')` if it
            # contains multiple packaged extensions
            name, ext = splitext(file_name)
            if name == file_name and ext == '':
                # file name like .gitignore and .vimrc
                ext = ''
            else:
                # normal extension like style.yapf and necronomicon.pdf
                # splitext also puts the dot on an extension
                # so we will trim that if anything is there
                ext = ext.split('.')[-1]
            return ext
        except Exception as exc:
            raise exc

    @classmethod
    def get_dir_name(cls, path: Text) -> Text:
        """
        # Get Dir Name
        """
        return basename(cls.get_dir_path(path))

    @classmethod
    def get_dir_path(cls, path: Text) -> Text:
        """
        # Get Dir Path
        """
        return dirname(path)

    @classmethod
    def replace_extension(cls, path: Text, extension: Text = None) -> Text:
        """
        # Replace Extension
        With the provided file path, replace its extension with
        """
        name = cls.get_name(path)
        if extension is None:
            return name
        name_pos = path.rfind(name)
        return cls.join(path[:name_pos], f'{name}.{extension}')

    @classmethod
    def remove_extension(cls, path: Text) -> Text:
        """
        # Remove Extension
        With the provided file path, replace its extension with
        """
        name = cls.get_name(path)
        name_pos = path.rfind(name)
        return cls.join(path[:name_pos], f'{name}')

    @classmethod
    def exists(cls, path: Text) -> Text:
        """
        # Exists
        """
        return exists(path)

    @classmethod
    def relative_path(cls, path: Text, relative_path: Text) -> Text:
        """
        # Relative Path
        Returns the path relative to the provide relative path
        """
        return relpath(path, relative_path)

    @classmethod
    def join(cls, path: Text, *paths) -> Text:
        """
        # Join
        """
        return join(path, *paths)

    @classmethod
    def split(cls, path: Text, separator=None) -> List[Text]:
        """
        # Split
        Different implementation than os's path split where the split segments
        all path parts into a list, not just the last one.
        """
        if separator is None:
            separator = '/'
        split_path = path.split(separator)
        if split_path[0] == '':
            split_path.pop(0)
        return split_path

    @classmethod
    def create(cls, path: Text, exist_ok=True) -> None:
        """
        # Create a directory
        """
        makedirs(path, exist_ok=exist_ok)

    @classmethod
    def get_nodes(
        cls,
        path: Text,
        depth: int = 0,
        file_ext=None,
        predicate=None,
    ) -> List[tuple]:
        """
        # Get Nodes
        Get directory and file nodes for a specified path
        By default the depth is `0` and will not traverse
        the sub paths in your path.

        # Args
        - `path`, The path to get the nodes from
        - `depth`, How far down the path do you want to traverse
        - `file_ext`, optional and when provided allows you to selectively
          filter files with extensions that match the one provided.  see
          `get_extension` for how the extension is fetched
        - `predicate`, callable, Additional filtering capabilities beyond what
          this method can provide. Callable must accept a path as an argument.
          return boolean true to indicate that the file should be collected,
          otherwise false to ignore it

        # Return
        A tuple of 
        """
        cur_depth = 0
        ndirs = []
        nfiles = []
        for root, dirs, files in walk(path):
            # file processing, here we support optionally
            # filtering paths by file extension
            for fpath in files:
                matches = []
                if predicate is not None and callable(predicate):
                    matches.append(predicate(fpath))
                if file_ext is not None:
                    matches.append(cls.get_extension(fpath) == file_ext)
                if any(matches):
                    nfiles.append(cls.join(root, fpath))
            # directory processing
            for d in dirs:
                # it is to be determined if directories should qualify as
                # participants of the predicate check, right now they do so
                # that the returned directories list does not return all
                # directories that it normally would
                if predicate:
                    add_dir = predicate(d)
                else:
                    add_dir = True
                if add_dir:
                    ndirs.append(cls.join(root, d))
            cur_depth += 1
            if depth is not None and cur_depth > depth:
                # limit recursion
                continue
        return (ndirs, nfiles)

    @classmethod
    def get_parts(cls, path, separator=None):
        """
        # Get path parts
        A more advanced form of `split`
        """
        if not separator:
            separator = '/'
        spath = [s for s in shlex(path, posix=True)]
        path_parts = []
        rpath = []
        for s in spath:
            if s == separator:
                rpath.append(''.join(path_parts))
                path_parts = []
                continue
            if s is not None:
                path_parts.append(s)
        if path_parts:
            rpath.append(''.join(path_parts))
        return rpath

    @classmethod
    def make_executable(cls, path, user: bool = None, group: bool = None, world: bool = None):
        """
        Make a path executable
        """

        if not path:
            return
        cur_stat = os.stat(path).st_mode
        next_stat = 0
        exec_user, exec_group, exec_world = stat.S_IXUSR, stat.S_IXGRP, stat.S_IXOTH
        clear_stat = exec_user | exec_group | exec_world
        if user and user is not None:
            next_stat |= exec_user
        if group and group is not None:
            next_stat |= exec_group
        if world and world is not None:
            next_stat |= exec_world
        chmod(path, cur_stat ^ clear_stat | next_stat)

    @classmethod
    def get_mime_type(cls, path: Text):
        """
        Get the mime_type of a filepath
        """
        mime_type, _ = mimetypes.guess_type(path)
        return mime_type

    @classmethod
    def expand_path(cls, path: Text) -> Text:
        """
        # Expand a path
        """
        if path.startswith('~'):
            path = expanduser(path)
        return path
