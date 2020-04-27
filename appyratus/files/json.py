from __future__ import absolute_import

from typing import Text

import jsbeautifier

from appyratus.json import JsonEncoder

from .file import File


class Json(File):
    """
    # Json File Type
    """

    _encoder = JsonEncoder.get_instance()

    @staticmethod
    def extensions():
        return {'json'}

    @classmethod
    def read(cls, path: Text):
        data = super().read(path)
        return cls.load(data)

    @classmethod
    def write(cls, path: Text, data=None, **kwargs):
        file_data = cls.dump(data, **kwargs)
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data):
        return cls._encoder.decode(data) if data else None


    @classmethod
    def dump(cls, data, indent: int = 2, sort_keys: bool = True, prettify: bool = True, **kwargs):
        data = cls._encoder.encode(
            data,
            indent=indent,
            sort_keys=sort_keys,
        )
        if prettify:
            cls.prettify(data)
        return data

    @classmethod
    def prettify(cls, data):
        return jsbeautifier.beautify(data)
