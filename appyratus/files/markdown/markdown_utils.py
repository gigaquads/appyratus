import mistune
from mistune import HTMLRenderer
import re

from appyratus.files.yaml import Yaml


class HtmlRenderer(object):
    pass


class MarkdownUtils(object):
    encoder = mistune.Markdown(renderer=HTMLRenderer(escape=False))

    @classmethod
    def extract_metadata(cls, value):
        regex = r"^<!--\n(.*?)-->"
        # extract the metadata for processing and convert it to yaml
        match = re.match(regex, value, re.S)
        if not match:
            return {}, value
        raw_metadata = match.group(1)
        metadata = Yaml.load(raw_metadata)
        # now remove the metadata from the original value
        cregex = re.compile(regex, re.S)
        res = cregex.sub('', value)
        return metadata, res

    @classmethod
    def to_html(cls, value):
        if value is None:
            return
        metadata, value = cls.extract_metadata(value)
        return cls.encoder(value), metadata
