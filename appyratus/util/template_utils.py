import re
import jinja2
import ujson
import json

from appyratus.util.text_transform import TextTransform
from appyratus.json import JsonEncoder

encoder = JsonEncoder()

INTERNAL_FILTERS = {
    'snake': TextTransform.snake,
    'dash': TextTransform.dash,
    'title': TextTransform.title,
    'camel': TextTransform.camel,
    'dot': TextTransform.dot,
    'json': lambda obj: (
        json.dumps(ujson.loads(encoder.encode(obj)),
        indent=2, sort_keys=True
    )),
}


class TemplateEnvironment(object):
    """
    Template Environment
    """

    def __init__(self, search_path: str=None, filters: dict=None):
        """
        Initialize the necessities of a template environment, including the
        environment itself as well as any filters to use when building and
        rendering a template.

        Internal filters are elements of appyratus that are applied here, such
        as ujson or the TextTransform util, to add additional convenience to
        the templating engine.  They could also be optional.
        """
        self.env = self.build_jinja_env(search_path or '/tmp')
        self.apply_filters(INTERNAL_FILTERS)
        if filters:
            self.apply_filters(filters)

    def build_jinja_env(self, search_path: str):
        """
        Create an instance of jinja Environment
        Templates are ideally generated from this, e.g.,

        ```
        tpl = env.from_string('Hello {{ name }}')
        tpl.render(dict(name='Johnny'))
        > "Hello Johnny"
        ```

        """
        loader = jinja2.FileSystemLoader(search_path)
        env = jinja2.Environment(
            loader=loader, autoescape=True, trim_blocks=True
        )
        return env

    def apply_filters(self, filters: dict=None):
        """
        Apply filters
        """
        self.env.filters.update(filters)

    def from_string(self, value):
        """
        Providing a string, run it against the templating environment
        """
        return self.env.from_string(value)
