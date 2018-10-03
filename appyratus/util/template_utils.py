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

# XXX Build Base class for TemplateEnvironment
# XXX Scan for filters rather than using init Use inspect.getmembers(env, predicate=inspect.ismethod) -> (method_name, method)


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

    def __init__(self, search_path: str = None, filters: dict = None):
        """
        Initialize the necessities of a template environment, including the
        environment itself as well as any filters to use when building and
        rendering a template.

        Internal filters are elements of appyratus that are applied here, such
        as ujson or the TextTransform util, to add additional convenience to
        the templating engine.  They could also be optional.
        """
        self.env = self.build(search_path or '/tmp')
        self.add_filters(INTERNAL_FILTERS)
        if filters:
            self.add_filters(filters)

    def build(self, search_path: str):
        """
        Create an instance of jinja Environment
        """
        loader = jinja2.FileSystemLoader(search_path)
        env = jinja2.Environment(
            loader=loader, autoescape=True, trim_blocks=True
        )
        return env

    def add_filters(self, filters: dict = None):
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
        def inner_func(self, request, response, *args, **kwargs):
            response.content_type = 'text/html'
            context = func(*args, **kwargs)
            template = self.env.from_template(self._name)
            return template.render(**context)

        return inner_func

    @classmethod
    def set_env(cls, env):
        cls.env = env

    @classmethod
    def get_env(cls):
        return cls.env
