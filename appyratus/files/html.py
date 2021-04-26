from __future__ import absolute_import
from bs4 import BeautifulSoup
import ast
import astor

from typing import Text, List, Dict

from .file import File


class Html(File):
    """
    # HTML File Type
    """

    @classmethod
    def extensions(cls):
        return {'html', 'htm'}

    @classmethod
    def read(cls, path: Text):
        data = super().read(path)
        return cls.load(data)

    @classmethod
    def write(cls, path: Text, data=None, **kwargs):
        file_data = cls.dump(data) if data else ''
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def load(cls, data):
        if not data:
            return
        parser = cls.get_parser(data)
        return parser

    @classmethod
    def dump(cls, data, prettify: bool = True):
        if prettify:
            data = cls.prettify(data)
        return data

    @classmethod
    def get_parser(cls, data):
        return BeautifulSoup(data, features='html.parser')

    @classmethod
    def prettify(cls, data):
        return cls.get_parser(data).prettify()


class MetaData(object):

    def __init__(self, site: Dict = None, page: Dict = None, **kwargs):
        self._site_data = self.build_metadata(**site or {})
        self._page_data = self.build_metadata(**page or {})
        self._full_data = self.append(self._site_data, self._page_data)

    def build_metadata(
        self,
        title=None,
        description=None,
        author=None,
        keywords: List = None,
        robots: List = None,
        language=None,
        revisit_after=None,
        charset=None,
        content_type=None,
        created_at=None,
        **kwargs
    ):
        charset = charset or 'utf-8'
        data = {
            'title': title or '',
            'description': description or '',
            'author': author or '',
            'keywords': keywords if keywords is not None else [],
            'language': language or 'English',
            'robots': robots or {'index', 'follow'},
            'revisit_after': revisit_after or '90 days',
            'charset': charset,
            'created_at': created_at,
            'content_type': content_type or f'text/html; charset={charset}',
        }
        data.update(kwargs)
        return data

    @property
    def site(self):
        return self._site_data

    @property
    def page(self):
        return self._page_data

    @property
    def full(self):
        return self._full_data

    def meta_format(self, **kwargs):
        attrs = [f'{k}="{v}"' for k, v in kwargs.items()]
        return f"<meta {' '.join(attrs)}>"

    def append(self, ldata, rdata):
        from copy import deepcopy

        data = deepcopy(ldata)
        rdata = deepcopy(rdata)

        for k, v in rdata.items():
            if k not in data:
                data[k] = v
                continue
            # only values with data may proceed to append
            if not v:
                continue
            if isinstance(data[k], list):
                data[k].extend(v)
            elif k in ('title', 'description'):
                data[k] = f'{data[k]} - {v}'
        return data

    def render(self):
        content = []
        for k, v in self._full_data.items():
            # prep the value depending on type
            if isinstance(v, (set, list)):
                v = ', '.join(v)
            # prepare the base kwargs
            kkwargs = {'name': k, 'content': v}
            # some custom kwarg configuration for a few keys
            if k == 'content_type':
                del kkwargs['name']
                kkwargs['http-equiv'] = "Content-Type"
            elif k == 'charset':
                kkwargs = {'charset': v}
            # header is read to format and add to list
            content.append(self.meta_format(**kkwargs))
        return '\n'.join(content)
