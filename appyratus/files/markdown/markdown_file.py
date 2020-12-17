from typing import Text

import mistune

from appyratus.files.file import File


class Markdown(File):

    @classmethod
    def extensions(cls):
        return {'md'}

    @classmethod
    def read(cls, path: Text):
        data = super().read(path)
        return cls.load(data)

    @classmethod
    def write(cls, path: Text, data=None, **kwargs):
        file_data = cls.dump(data)
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data):
        return data

    @classmethod
    def dump(cls, data):
        return data

    @classmethod
    def get_parser(cls, data):
        raise NotImplemented()
