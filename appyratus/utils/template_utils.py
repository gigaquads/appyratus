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

    def __init__(self, search_path: str = None, *args, **kwargs):
        self.search_path = search_path or '/tmp'
        #class_filters = self.resolve_class_filters()

    def resolve_class_filters(self, klass):
        members = inspect.getmembers(klass, predicate=inspect.ismethod)
        import ipdb; ipdb.set_trace(); print('=' * 100)
        return 


    def build(self):
        """
        # Build template environment
        """
        pass

    def from_string(self, value: str):
        """
        # From a string, return an instance of Template
        """
        pass

    def from_filename(self, filename: str):
        """
        # From a filename, return an instance of Template
        """
        pass


class Template(object):
    """
    # Template
    The template object
    """
    def __init__(self, template_obj = None):
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

    def __init__(self, search_path: str = None, filters: dict = None):
        """
        Initialize the necessities of a template environment, including the
        environment itself as well as any filters to use when building and
        rendering a template.

        Internal filters are elements of appyratus that are applied here, such
        as ujson or the StringUtils util, to add additional convenience to
        the templating engine.  They could also be optional.
        """
        super().__init__(search_path=search_path)
        from appyratus.json import JsonEncoder
        self.env = self.build()
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

    def build(self):
        """
        Create an instance of jinja Environment
        """
        loader = jinja2.FileSystemLoader(self.search_path)
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


class TemplateEnvironment(JinjaTemplateEnvironment):
    # XXX Temporary because of refactoring
    pass
