import inspect
import json
import re

from copy import deepcopy
from typing import Dict, List, Text

import jinja2

from jinja2 import meta

from .string_utils import StringUtils
from appyratus.files.python.python_utils import PythonUtils
from appyratus.files.markdown.markdown_utils import MarkdownUtils

# TODO: Scan for filters rather than using init
#  Use inspect.getmembers(env, predicate=inspect.ismethod)
#   -> (method_name, method)
# XXX how to know _which_ method is meant to be a filter?


class TemplateUtils(object):

    @classmethod
    def get_environment(cls):
        return TemplateEnvironment

    @classmethod
    def get_template_variables(cls, template: Text = None):
        env = cls.get_environment()
        parsed_content = env()._env.parse(template)
        return meta.find_undeclared_variables(parsed_content)


class Template(object):
    """
    # Template
    The template object
    """

    def __init__(self, template_obj=None, context: Dict = None, env=None):
        self._template_obj = template_obj
        self._env = env
        self._context = context if context is not None else {}

    def render(self, context: Dict = None):
        """
        # Render
        """
        if context is None:
            context = {}
        base_context = deepcopy(self._context)
        base_context.update(context)
        return self._template_obj.render(**base_context)


class TemplateFilter(object):

    def __call__(self, value=None):
        return self.perform(value)

    def perform(self, value=None):
        raise NotImplementedError()


from jinja2 import nodes
from jinja2.ext import Extension
from jinja2 import Markup


class IncludeRawExtension(Extension):
    tags = {"include_raw"}

    def parse(self, parser):
        lineno = parser.stream.expect("name:include_raw").lineno
        filename = nodes.Const(parser.parse_expression().value)
        result = self.call_method("_render", [filename], lineno=lineno)
        return nodes.Output([result], lineno=lineno)

    def _render(self, filename):
        return Markup(self.environment.loader.get_source(self.environment, filename)[0])


class Markdown2HtmlFilter(TemplateFilter):
    """
    # Markdown2HTML
    With provided markdown, convert to html
    """

    def perform(self, value: Text) -> Text:
        if value is None:
            return
        return MarkdownUtils.to_html(value)


class FormatPythonFilter(TemplateFilter):
    """
    # Python Format Filter
    Format python source code
    """

    def perform(self, value: Text) -> Text:
        return PythonUtils.format_python(value)


class Python2HtmlFilter(TemplateFilter):
    """
    # Python2HTML Filter
    Convert Python source to Html 
    """

    def perform(self, value: Text) -> Text:
        if isinstance(value, Markup):
            # jinja will provide a Markupsafe class to escape characters.. we
            # don't want this at this point
            value = value.unescape()
        return PythonUtils.to_html(value)


class IncludeFileFilter(TemplateFilter):
    """
    # Include File Filter
    Include a file directly into the template
    """

    def __init__(self, loader, env):
        self._loader = loader
        self._env = env

    def perform(self, value: Text) -> Text:
        return jinja2.Markup(self._loader.get_source(self._env, value)[0])


class BaseTemplateEnvironment(object):
    """
    # Template Environment

    ```
    env = TemplateEnvironment(search_path='/tmp')
    tpl = env.from_string('Hello {{ name }}')
    tpl.render({'name':'Johnny'})
    > "Hello Johnny"
    ```
    """

    def __init__(
        self,
        search_path: Text = None,
        templates: Dict = None,
        methods: Dict = None,
        *args,
        **kwargs
    ):
        self.search_path = search_path
        self.templates = templates or {}
        self._methods = methods if methods is not None else {}
        #class_filters = self.resolve_class_filters()

    def resolve_class_filters(self, klass):
        members = inspect.getmembers(klass, predicate=inspect.ismethod)
        return

    def build(self):
        """
        # Build template environment
        """
        pass

    def from_string(self, value: Text, context: Dict = None):
        """
        # From a string, return an instance of Template
        """
        pass

    def from_filename(self, value: Text, context: Dict = None):
        """
        # From a filename, return an instance of Template
        """
        pass


class JinjaTemplateEnvironment(BaseTemplateEnvironment):
    """
    # Jinja Template Environment
    """
    BASE_FILTERS = {
        'snake': StringUtils.snake,
        'dash': StringUtils.dash,
        'title': StringUtils.title,
        'camel': StringUtils.camel,
        'camel_lower': lambda x: StringUtils.camel(x, lower=True),
        'plural': StringUtils.plural,
        'singular': StringUtils.singular,
        'alphanumeric': StringUtils.alphanumeric,
        'constant': StringUtils.constant,
        'format_python': FormatPythonFilter(),
        'python2html': Python2HtmlFilter(),
        'markdown2html': Markdown2HtmlFilter(),
        'dot': StringUtils.dot,
        'wrap': StringUtils.wrap,
        'json': lambda obj: (Json.dump(obj, indent=2, sort_keys=True)),
        'jinja': lambda tpl, ctx: self.env.from_string(tpl).render(ctx),
        'jinja_exp': lambda x: "{{ " + x + " }}",
        'jinja_stmt': lambda x: "{% " + x + " %}",
    }

    def __init__(
        self,
        search_path: Text = None,
        filters: Dict = None,
        templates: Dict = None,
        **kwargs
    ):
        """
        Initialize the necessities of a template environment, including the
        environment itself as well as any filters to use when building and
        rendering a template.

        Internal filters are elements of appyratus that are applied here, such
        as json or the StringUtils util, to add additional convenience to
        the templating engine.  They could also be optional.
        """
        # XXX imported here as it causes circular depedency
        from appyratus.files import Json

        super().__init__(search_path=search_path, templates=templates, **kwargs)

        self._env = None
        self._loaders = None

        self.add_filters(self.BASE_FILTERS)
        if filters:
            self.add_filters(filters)

    @property
    def env(self):
        if not self._env:
            self._env = self.build()
        return self._env

    def build(self, loader=None):
        """
        Create an instance of jinja Environment
        """
        loaders = []
        if not loader:
            if self.templates:
                loaders.append(jinja2.DictLoader(self.templates))
            if self.search_path:
                loaders.append(jinja2.FileSystemLoader(self.search_path))
            package_loader = jinja2.PackageLoader(__name__, self.search_path)
            loaders.append(package_loader)
        else:
            loaders.append(loader)

        self._loaders = loaders

        extensions = [IncludeRawExtension]
        env = jinja2.Environment(
            loader=jinja2.ChoiceLoader(loaders),
            autoescape=True,
            trim_blocks=True,
            extensions=extensions,
        )
        self._methods['include_file'] = IncludeFileFilter(package_loader, env)
        env.globals.update(self._methods)

        return env

    def add_filters(self, filters: Dict = None):
        """
        Apply filters
        """
        self.env.filters.update(filters)

    def from_string(self, value: Text, context: Dict = None):
        """
        Providing a string, return a template
        """
        jtpl = self.env.from_string(value)
        return Template(jtpl, env=self, context=context)

    def from_filename(self, filename: Text, context: Dict = None):
        """
        Providing a template filename, return a template
        """
        jtpl = self.env.get_template(filename)
        return Template(jtpl, env=self, context=context)


class TemplateEnvironment(JinjaTemplateEnvironment):
    # XXX Temporary because of refactoring
    pass
