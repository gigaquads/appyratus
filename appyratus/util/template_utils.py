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

    ```
    env = TemplateEnvironment(search_path='/tmp')
    tpl = env.from_string('Hello {{ name }}')
    tpl.render(dict(name='Johnny'))
    > "Hello Johnny"
    ```
    """
    filters = INTERNAL_FILTERS

    def __init__(self, search_path: str = None, filters: dict = None):
        """
        Initialize the necessities of a template environment, including the
        environment itself as well as any filters to use when building and
        rendering a template.

        Internal filters are elements of appyratus that are applied here, such
        as ujson or the TextTransform util, to add additional convenience to
        the templating engine.  They could also be optional.
        """
        self.env = self.build_jinja_env(search_path or '/tmp')
        if self.filters:
            self.apply_filters(self.filters)
        if filters:
            self.apply_filters(filters)

    def build_jinja_env(self, search_path: str):
        """
        Create an instance of jinja Environment
        """
        loader = jinja2.FileSystemLoader(search_path)
        env = jinja2.Environment(
            loader=loader, autoescape=True, trim_blocks=True
        )
        return env

    def apply_filters(self, filters: dict = None):
        """
        Apply filters
        """
        self.env.filters.update(filters)

    def from_string(self, value: str):
        """
        Providing a string, return a template 
        """
        return self.env.from_string(value)


    def from_filename(self, filename: str):
        """
        Providing a template filename, return a template
        """
        return self.env.get_template(filename)



class templatized(object):
    """
    Decorator for rendering templates
    """
    env = TemplateEnvironment()

    def __init__(self, name: str, *args, **kwargs):
        self._name = name

    def __call__(self, func):
        def inner_func(self, *args, **kwargs):
            context = func(*args, **kwargs)
            return self.env.render()

        return inner_func
