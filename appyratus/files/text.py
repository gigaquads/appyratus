from __future__ import absolute_import

from .base import File


class Text(File):

    @staticmethod
    def extensions():
        return {'txt'}
