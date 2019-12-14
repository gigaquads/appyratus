from os import walk
from os.path import (
    basename,
    dirname,
    exists,
    join,
    realpath,
    splitext,
)
from typing import (
    List,
    Text,
)


class PathUtils(object):

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
            import ipdb
            ipdb.set_trace()
            print('=' * 100)

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
    def exists(cls, path: Text) -> Text:
        """
        # Exists
        """
        return exists(path)

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
                add_file = True
                if predicate is not None and callable(predicate):
                    add_file = predicate(fpath)
                if file_ext is not None:
                    add_file = cls.get_extension(fpath) == file_ext
                if add_file:
                    nfiles.append(cls.join(root, fpath))
            # directory processing
            for d in dirs:
                ndirs.append(cls.join(root, d))
            cur_depth += 1
            if depth is not None and cur_depth > depth:
                # limit recursion
                break
        return (ndirs, nfiles)
