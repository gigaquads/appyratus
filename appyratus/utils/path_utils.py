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
        return dirname(realpath(path))

    @classmethod
    def replace_extension(cls, path: Text, extension: Text = None) -> Text:
        """
        # Replace Extension
        """
        name = cls.get_name(path)
        if extension is None:
            return name
        return f'{name}.{extension}'

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
    def get_nodes(cls, path: Text, depth: int = 1) -> List[tuple]:
        """
        # Get Nodes
        Get directory and file nodes for a specified path
        """
        cur_depth = 0
        ndirs = []
        nfiles = []
        for root, dirs, files in walk(path):
            if files:
                for f in files:
                    nfiles.append(cls.join(root, f))
            if dirs:
                for d in dirs:
                    ndirs.append(cls.join(root, d))
            cur_depth += 1
            if depth is not None and cur_depth >= depth:
                # limit recursion
                break
        return (ndirs, nfiles)
