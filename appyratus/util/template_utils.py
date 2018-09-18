import re
import jinja2
import ujson
import json

from appyratus.util.text_transform import TextTransform
from appyratus.json import JsonEncoder


class TemplateEnvironment(object):
    """
    Template Environment
    """
    def __init__(self):
        self.env = self.build_jinja_env()
        self.apply_custom_filters()

    def build_jinja_env(self):
        """
        Create an instance of jinja Environment
        Templates are ideally generated from this, e.g.,

        ```
        tpl = env.from_string('Hello {{ name }}')
        tpl.render(dict(name='Johnny'))
        > "Hello Johnny"
        ```

        """
        loader = jinja2.FileSystemLoader('/tmp')
        env = jinja2.Environment(
            autoescape=True, loader=loader, trim_blocks=True
        )
        return env

    def apply_internal_filters(self):
        """
        Add internal filters

        Internal filters are elements of appyratus that are applied here, such
        as ujson or the TextTransform util, to add additional
        convenience to the templating engine.
        """
        encoder = JsonEncoder()

        internal_filters = {
            'snake': TextTransform.snake,
            'dash': TextTransform.dash,
            'title': TextTransform.title,
            'camel': TextTransform.camel,
            'dot': TextTransform.dot,
            'json': lambda obj: (
                json.dumps(ujson.loads(encoder.encode(obj)),
                indent=2, sort_keys=True
            ))
                }
        self.env.filters.update(internal_filters)

    def from_string(self, value):
        """
        Providing a string, run it against the templating environment
        """
        return self.env.from_string(value)
