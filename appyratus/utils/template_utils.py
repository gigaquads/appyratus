from typing import Text, Dict, List
import inspect
import jinja2
import json
import re
import ujson

from .string_utils import StringUtils

# TODO: Scan for filters rather than using init
#  Use inspect.getmembers(env, predicate=inspect.ismethod)
#   -> (method_name, method)
# XXX how to know _which_ method is meant to be a filter?


class BaseTemplateEnvironment(object):
    """
    # Template Environment

    ```
    env = TemplateEnvironment(search_path='/tmp')
    tpl = env.from_string('Hello {{ name }}')
    tpl.render(dict(name='Johnny'))
    > "Hello Johnny"
    ```
    """

    def __init__(self, search_path: Text = None, templates: List = None, *args, **kwargs):
        self.search_path = search_path or '/tmp'
        self.templates = templates or {}
        #class_filters = self.resolve_class_filters()

    def resolve_class_filters(self, klass):
        members = inspect.getmembers(klass, predicate=inspect.ismethod)
        return

    def build(self):
        """
        # Build template environment
        """
        pass

    def from_string(self, value: Text):
        """
        # From a string, return an instance of Template
        """
        pass

    def from_filename(self, filename: Text):
        """
        # From a filename, return an instance of Template
        """
        pass


class Template(object):
    """
    # Template
    The template object
    """

    def __init__(self, template_obj=None):
        self._template_obj = template_obj

    def render(self):
        """
        # Render
        """
        pass


class JinjaTemplateEnvironment(BaseTemplateEnvironment):
    """
    # Jinja Template Environment
    """

    def __init__(
        self, search_path: Text = None, filters: Dict = None, templates: Dict = None
    ):
        """
        Initialize the necessities of a template environment, including the
        environment itself as well as any filters to use when building and
        rendering a template.

        Internal filters are elements of appyratus that are applied here, such
        as ujson or the StringUtils util, to add additional convenience to
        the templating engine.  They could also be optional.
        """
        import ipdb; ipdb.set_trace(); print('=' * 100)
        super().__init__(search_path=search_path, templates=templates)
        from appyratus.json import JsonEncoder
        self.env = self.build()
        self.json_encoder = JsonEncoder()
        self.add_filters(
            {
                'snake': StringUtils.snake,
                'dash': StringUtils.dash,
                'title': StringUtils.title,
                'camel': StringUtils.camel,
                'dot': StringUtils.dot,
                'json':
                    lambda obj: (
                        json.dumps(
                            ujson.loads(self.json_encoder.encode(obj)),
                            indent=2,
                            sort_keys=True
                        )
                    ),
            }
        )
        if filters:
            self.add_filters(filters)

    def build(self, loader=None):
        """
        Create an instance of jinja Environment
        """
        if not loader:
            if self.search_path:
                loader = jinja2.FileSystemLoader(self.search_path)
            elif self.templates:
                loader = jinja2.DictLoader(self.templates)
        env = jinja2.Environment(
            loader=loader,
            autoescape=True,
            trim_blocks=True,
        )
        return env

    def add_filters(self, filters: dict = None):
        """
        Apply filters
        """
        self.env.filters.update(filters)

    def from_string(self, value: Text):
        """
        Providing a string, return a template
        """
        return self.env.from_string(value)

    def from_filename(self, filename: Text):
        """
        Providing a template filename, return a template
        """
        return self.env.get_template(filename)


class TemplateEnvironment(JinjaTemplateEnvironment):
    # XXX Temporary because of refactoring
    pass
