import inspect
import json
import re
from copy import deepcopy
from typing import (
    Dict,
    List,
    Text,
)

import jinja2


from .string_utils import StringUtils

# TODO: Scan for filters rather than using init
#  Use inspect.getmembers(env, predicate=inspect.ismethod)
#   -> (method_name, method)
# XXX how to know _which_ method is meant to be a filter?


class TemplateUtils(object):
    pass


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

    def __init__(self, template_obj=None, context: Dict = None):
        self._template_obj = template_obj
        self._context = context if context is not None else {}

    def render(self, context: Dict = None):
        """
        # Render
        """
        if context is None:
            context = {}
        base_context = deepcopy(self._context)
        base_context.update(context)
        return self._template_obj.render(base_context)


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
        as json or the StringUtils util, to add additional convenience to
        the templating engine.  They could also be optional.
        """
        super().__init__(search_path=search_path, templates=templates)
        # XXX imported here as it causes circular depedency 
        from appyratus.files import Json
        self.env = self.build()
        self.add_filters(
            {
                'snake': StringUtils.snake,
                'dash': StringUtils.dash,
                'title': StringUtils.title,
                'camel': StringUtils.camel,
                'dot': StringUtils.dot,
                'json': lambda obj: (Json.dump(obj, indent=2, sort_keys=True)),
                'jinja': lambda tpl, ctx: self.env.from_string(tpl).render(ctx)
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
        jtpl = self.env.from_string(value)
        return Template(jtpl)

    def from_filename(self, filename: Text):
        """
        Providing a template filename, return a template
        """
        jtpl = self.env.get_template(filename)
        return Template(jtpl)


class TemplateEnvironment(JinjaTemplateEnvironment):
    # XXX Temporary because of refactoring
    pass
