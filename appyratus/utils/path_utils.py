
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
        return splitext(path)[-1].split('.')[1]

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
