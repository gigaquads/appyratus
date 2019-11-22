
from os.path import splitext, basename, dirname, realpath, exists


class PathUtils(object):

    @staticmethod
    def get_name(path):
        return splitext(PathUtils.get_filename(path))[0]

    @staticmethod
    def get_filename(path):
        return basename(path)

    @staticmethod
    def get_extension(path):
        # splitext returns a tuple like `('file',
        # '.zip')`, or `('file.tar', '.gz')` if it
        # contains multiple packaged extensions
        ext_parts = splitext(path)
        ext = ext_parts[-1]
        if ext:
            # splitext also puts the dot on an extension
            # so we will trim that if anything is there
            ext = ext.split('.')[1]
        return ext

    @staticmethod
    def get_dir_path(path):
        return dirname(realpath(path))

    @staticmethod
    def replace_extension(path, extension=None):
        name = PathUtils.get_name(path)
        if extension is None:
            return name
        return f'{name}.{extension}'

    @staticmethod
    def exists(path):
        return exists(path)
