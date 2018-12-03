import re
import jinja2
import ujson
import json

from .string_utils import StringUtils


# TODO: Turn this into a JinjaUtils class
# TODO: Build Base class for TemplateEnvironment
# TODO: Scan for filters rather than using init Use inspect.getmembers(env,
# predicate=inspect.ismethod) -> (method_name, method)


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
        as ujson or the StringUtils util, to add additional convenience to
        the templating engine.  They could also be optional.
        """
        from appyratus.json import JsonEncoder

        self.env = self.build(search_path or '/tmp')
        self.json_encoder = JsonEncoder()
        self.add_filters({
            'snake': StringUtils.snake,
            'dash': StringUtils.dash,
            'title': StringUtils.title,
            'camel': StringUtils.camel,
            'dot': StringUtils.dot,
            'json': lambda obj: (
                json.dumps(ujson.loads(self.json_encoder.encode(obj)),
                indent=2, sort_keys=True
            )),
        })
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
