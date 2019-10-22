import os


class FileUtils(object):

    @staticmethod
    def get_name(path):
        return os.path.splitext(FileUtils.get_filename(path))[0]

    @staticmethod
    def get_filename(path):
        return os.path.basename(path)

    @staticmethod
    def get_extension(path):
        return os.path.splitext(path)[-1].split('.')[1]

    @staticmethod
    def get_dir_path(path):
        return os.path.dirname(os.path.realpath(path))

    @staticmethod
    def replace_extension(path, extension=None):
        name = FileUtils.get_name(path)
        if extension is None:
            return name
        return f'{name}.{extension}'
