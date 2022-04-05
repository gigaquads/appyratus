from typing import Text

from appyratus.test import (
    BaseTests,
    mark,
)
from appyratus.utils.url_utils import UrlUtils


@mark.unit
class TestUrlUtils(BaseTests):

    @classmethod
    def __klass__(cls):
        return UrlUtils

    @mark.parametrize(
        'url, expected', [
            ('', {
                'scheme': '',
                'host': None,
                'port': None,
                'path': '',
                'params': '',
                'query': '',
                'fragment': ''
            }),
            (
                'https://appyrat.us', {
                    'scheme': 'https',
                    'host': 'appyrat.us',
                    'port': None,
                    'path': '',
                    'params': '',
                    'query': '',
                    'fragment': ''
                }
            ),
            (
                'appyrat.us', {
                    'scheme': '',
                    'host': 'appyrat.us',
                    'port': None,
                    'path': '',
                    'params': '',
                    'query': '',
                    'fragment': ''
                }
            )
        ]
    )
    def test_parse_url(self, url, expected):
        res = self.klass.parse_url(url)
        assert res == expected

    @mark.parametrize('value, expected', [('', ''), ('%20', ' ')])
    def test_unquote_encoded_string(self, value, expected):
        res = self.klass.unquote_encoded_string(value)
        assert res == expected

    @mark.parametrize('value, expected', [('', ''), ({'yes': '1'}, 'yes=1')])
    def test_encode_params(self, value, expected):
        res = self.klass.encode_params(value)
        assert res == expected

    @mark.parametrize('value, expected', [('', {})])
    def test_parse_query_string(self, value, expected):
        res = self.klass.parse_query_string(value)
        assert res == expected
