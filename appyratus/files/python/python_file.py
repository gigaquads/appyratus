from __future__ import absolute_import

import ast
import re
from typing import (
    Dict,
    Text,
    Tuple,
)

import astor
from yapf.yapflib.yapf_api import FormatCode

from appyratus.files.file import (
    File,
    FileObject,
)

PYTHON_COMMENT_TAG = 'RUBBER-PANTS'


class PythonModule(File):

    @staticmethod
    def extensions():
        return {'py'}

    @classmethod
    def format_file_name(cls, basename):
        return f'{basename}.py'

    @classmethod
    def get_comment_tag(cls):
        return PYTHON_COMMENT_TAG

    @classmethod
    def read(cls, path: Text, **kwargs):
        data = super().read(path, **kwargs)
        return cls.load(data, **kwargs)

    @classmethod
    def write(cls, path: Text, data=None, **kwargs):
        file_data = cls.dump(data, **kwargs) if data else ''
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data, preserve_comments: bool = True):
        """
        # Load
        Load python file contents into AST objects

        # Args
        - `data`, file contents
        - `preserve_comments` (`bool`, `True`) load a python module and
          preserve hashed comments, e.g., (`# COMMENT`),  that would otherwise
          be removed by the AST parsing process.  If this is set to `False` then
          you will lose these comments when writing the AST objects back to disk.
        """
        if not data:
            return
        if preserve_comments:
            clean_data = cls._hashed_comments_to_strings(data)
        else:
            clean_data = cls._format_code(data)
        ast_data = ast.parse(clean_data)
        return ast_data

    @classmethod
    def dump(
        cls,
        data,
        restore_comments: bool = True,
        format_code: bool = True,
        style_config: Dict = None,
        **kwargs
    ):
        """
        # Dump

        # Args
        - `data`, AST source objects
        - `restore_comments`, revert comments injected back to their original state from when `load` was performed and comments were translated
        - `format_code`, format the python code according to yapf conventions
        - `style_config`, additional style configuration to apply to yapf formatting
        """
        if isinstance(data, str):
            source_data = data
        else:
            source_data = astor.to_source(data)
        if restore_comments:
            clean_data = cls._string_comments_to_hashed(source_data)
        else:
            clean_data = source_data
        if format_code:
            clean_data = cls.format_code(clean_data, style_config=style_config)
        return clean_data

    @classmethod
    def _hashed_comments_to_strings(cls, data):
        """
        # Hashed Comments To Strings
        Using the provided string data, convert all matching hashed comments.

        In example:
          from `# MY COMMENT`, 
          into `\"\"\" MY TAG#MY COMMENT \"\"\"`
        """

        # detect string literals
        str_literal_regex = r'(\"\"\"[\W\w]*?\"\"\")'
        str_literal_spans = [
            k.span() for k in re.finditer(str_literal_regex, data, re.MULTILINE)
        ]

        def between(value: Text, value_range: Tuple):
            return value_range[0] <= value <= value_range[1]

        def exclude_comments_in_string_literals(match):
            """
            If a comment is within range of any detected string literals, then
            do not perform processing as it is not

            # Args
            - `match`, the match object provided by `re`
            """
            match_span = match.span()
            in_match = any(
                [all([between(m, sp) for m in match_span]) for sp in str_literal_spans]
            )
            if in_match:
                # hash in match is located in string literal spans, do nothing
                return match.group(1)
            else:
                # hash is likely a comment, so add the tag to and enclose in quotes
                return '""" {tag}{match} """'.format(
                    tag=cls.get_comment_tag(),
                    match=match.group(1),
                )

        match_basic = [
        # get all comments, this is sufficient enough when we perform
            r'(\#.*)',
        # custom method to exclude conversion of comments like in string literals
            exclude_comments_in_string_literals,
        ]
        sub_res = re.sub(*match_basic, data)
        return sub_res

    @classmethod
    def _string_comments_to_hashed(cls, data):
        """
        Convert any string literals with tag identifier back to their hashed
        format, primarily for writing back to file.

        In example:
          from `# MY COMMENT`, 
          into `\"\"\" MY TAG#MY COMMENT \"\"\"`
        """
        match_basic = [
            r'\"\"\" {tag}(.*) \"\"\"'.format(tag=cls.get_comment_tag()),
            r'\1',
        ]
        sub_res = re.sub(*match_basic, data)
        return sub_res

    @classmethod
    def format_code(cls, data, style_config: Dict = None):
        """
        # Format Code
        Format python code using yapf style conventions
        """
        if not style_config:
            style_config = {}
        res = FormatCode(data, style_config=style_config)
        return res[0]


class PythonModuleFileObject(FileObject):

    def file_type(cls):
        return PythonModule
