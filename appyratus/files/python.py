from __future__ import absolute_import
import ast
import astor
import re

from typing import Text

from .base import File


class PythonModule(File):

    @staticmethod
    def extensions():
        return {'py'}

    @classmethod
    def format_file_name(cls, basename):
        return f'{basename}.py'

    @classmethod
    def get_comment_tag(cls):
        return 'RUBBER-PANTS'

    @classmethod
    def read(cls, path: Text, preserve_comments: bool = True):
        data = super().read(path)
        return cls.load(data, preserve_comments=preserve_comments)

    @classmethod
    def write(cls, path: Text, data=None, restore_comments: bool = True, **kwargs):
        file_data = cls.dump(data, restore_comments=restore_comments) if data else ''
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data, preserve_comments: bool = True):
        if not data:
            return
        if preserve_comments:
            clean_data = cls.hashed_comments_to_quoted(data)
        else:
            clean_data = data
        ast_data = ast.parse(clean_data)
        return ast_data

    @classmethod
    def dump(cls, data, restore_comments: bool = True):
        source_data = astor.to_source(data)
        if restore_comments:
            clean_data = cls.quoted_comments_to_hashed(source_data)
        else:
            clean_data = source_data
        return clean_data

    @classmethod
    def hashed_comments_to_quoted(cls, data):
        list_data = data.split("\n")
        for idx, line in enumerate(list_data):
            """
            (\#.*)
            Get all comments

            (\#.*)(?!([.\s\w]*\"\"\"))
            Does not match comment at top of class due to no negative lookbehind

            (\#.*)|(\#.*)(?!([.\s\w]*\"\"\"))
            By alternating both, we get success
			"""
            match_comment = r'^([^#][.\s]*)?(\#.*)$'
            match_comment = r'(\#.*)(?!([.\s\w]*\"\"\"))'
            match_replace = r'\1""" {}\2 """'.format(cls.get_comment_tag())
            match = re.match(match_comment, line)
            if not match:
                continue
            clean_line = re.sub(match_comment, match_replace, line)
            list_data[idx] = clean_line
        return "\n".join(list_data)

    @classmethod
    def quoted_comments_to_hashed(cls, data):
        list_data = data.split("\n")
        for idx, line in enumerate(list_data):
            match_comment = r'(.*)\"\"\" {}(.*) \"\"\"'.format(cls.get_comment_tag())
            match_replace = r'\1\2'
            match = re.match(match_comment, line)
            if not match:
                continue
            clean_line = re.sub(match_comment, match_replace, line)
            list_data[idx] = clean_line
        return "\n".join(list_data)


class FileObject(object):

    @classmethod
    def file_type(cls):
        raise NotImplementedError('implement in subclass')

    def __init__(self, path: Text = None, data=None, **kwargs):
        self._path = path
        self._data = data

    @property
    def path(self):
        return self._path

    @property
    def data(self):
        return self._data

    def read(self):
        self._data = self.file_type.read(self.path)
        return self._data

    def write(self):
        self.file_type.write(self.path, self.data)


class PythonModuleFileObject(FileObject):

    def file_type(cls):
        return PythonModule
