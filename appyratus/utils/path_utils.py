from os.path import splitext, basename, dirname, realpath, exists


class PathUtils(object):

    @classmethod
    def get_file_name(cls, path):
        """
        # Get File Name
        """
        return basename(path)

    @classmethod
    def get_name(cls, path):
        """
        # Get Name
        """
        return splitext(cls.get_file_name(path))[0]

    @classmethod
    def get_extension(cls, path):
        """
        # Get Extension
        """
        return splitext(path)[-1].split('.')[1]

    @classmethod
    def get_dir_name(cls, path):
        """
        # Get Dir Name
        """
        return basename(cls.get_dir_path(path))

    @classmethod
    def get_dir_path(cls, path):
        """
        # Get Dir Path
        """
        return dirname(realpath(path))

    @classmethod
    def replace_extension(cls, path, extension=None):
        """
        # Replace Extension
        """
        name = cls.get_name(path)
        if extension is None:
            return name
        return f'{name}.{extension}'

    @classmethod
    def exists(cls, path):
        """
        # Exists
        """
        return exists(path)
