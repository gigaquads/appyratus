from __future__ import absolute_import

from .file import File


class Text(File):
    """
    # Text File Type
    """

    @classmethod
    def extensions(cls):
        return {'txt'}
