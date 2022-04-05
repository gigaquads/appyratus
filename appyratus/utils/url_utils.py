from typing import (
    List,
    Text,
)
from urllib.parse import (
    parse_qs,
    unquote,
    urlencode,
    urlparse,
)


class UrlUtils(object):

    @classmethod
    def parse_url(cls, url: Text, relative=False):
        if not relative and '//' not in url:
            # urlparse will not interpret the host "netloc" if "//" is not
            # provided (as per rfc1808), so we will add them only if it is
            # requested to be relative
            url = '//' + url
        parsed_url = urlparse(url)
        return {
            'scheme': parsed_url.scheme,
            'host': parsed_url.hostname,
            'port': parsed_url.port,
            'path': parsed_url.path,
            'params': parsed_url.params,
            'query': parsed_url.query,
            'fragment': parsed_url.fragment,
        }

    @classmethod
    def unquote_encoded_string(cls, value: Text):
        return unquote(value)

    @classmethod
    def encode_params(cls, params: List, do_sequence: bool = True):
        if not params:
            return ''
        return urlencode(params, doseq=do_sequence)

    @classmethod
    def parse_query_string(cls, query_string: Text):
        if not query_string:
            return {}
        return parse_qs(query_string)
