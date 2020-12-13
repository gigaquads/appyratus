from typing import (
    Dict,
    List,
    Text,
)

from appyratus.exc import BaseError
from appyratus.schema import Schema
from appyratus.utils.dict_utils import DictUtils
from appyratus.utils.string_utils import StringUtils


class UsageError(BaseError):
    error_code = 'usage'
    error_message = 'Generic Usage Error'


class InvalidUsageRendererError(UsageError):
    error_code = 'invalid-usage-renderer'
    error_message = 'Invalid Usage Renderer Error'


class UnknownUsageRendererError(UsageError):
    error_code = 'unknown-usage-renderer'
    error_message = 'Unknown Usage Renderer Error'


class RenderersNotDefinedError(UsageError):
    error_code = 'renderers-not-defined'
    error_message = 'Renderers Not Defined Error'


class BaseUsage(object):
    """
    # Base Usage
    """

    _renderers = None

    def __init__(
        self,
        name: Text = None,
        description: Text = None,
        renderers: List = None,
        data: Dict = None,
        **kwargs
    ):
        """
        # Initialize Base Usage
        """
        self._name = name
        self._description = description
        self._renderer = None
        self._renderers = renderers or {}

    def __call__(self, renderer: Text = None, context: Dict = None, **kwargs):
        return self.render(renderer=renderer, context=context, **kwargs)

    def get_renderer(self, name: Text = None):
        """
        # Get Renderer
        Get a renderer by the provided name.  Name is a mapping available in
        `_renderers`
        """
        renderer = None
        if name is None and self._renderer:
            renderer = self._renderer
        if not self._renderers:
            raise RenderersNotDefinedError()
        if isinstance(name, str):
            # renderer is a string.  let's find a suitable renderer
            renderer = self._renderers.get(StringUtils.dash(name))
            if not renderer:
                raise InvalidUsageRendererError(data={'renderer': name})
        if not renderer:
            raise UnknownUsageRendererError()
        return renderer

    def render(self, renderer: Text = None, context: Dict = None):
        """
        # Render
        Render the usage example
        """
        renderer = self.renderer = self.get_renderer(renderer)(usage=self)
        base_context = {
            'name': self._name,
            'description': self._description,
            'kwargs': self._data
        }
        # merge context with base
        context = self._merge_context(base_context, context)
        # finally call the renderer with the modified context
        return renderer.perform(context)

    def _merge_context(self, left: Dict = None, right: Dict = None):
        # remove none type values from the dict to be merged in
        DictUtils.remove_keys(right, values=[type(None)], in_place=True)
        # merge base with our cleaned context
        return DictUtils.merge(left, right)


class ShellCommand(object):
    pass


class BaseUsageRenderer(object):
    """
    # Base Usage Renderer
    Responsible for rendering usage examples 
    """

    def __init__(self, usage, context: Dict = None):
        self._usage = usage
        self._context = context if context is not None else {}

    def __call__(self, context: Dict = None, **kwargs):
        return self.perform(context, **kwargs)

    def perform(self, context: Dict = None, **kwargs):
        if context is None:
            context = {}
        if context is not None:
            context = {**self._context, **context}
        template = self.get_template()
        res = template.format(**context)
        return res

    @classmethod
    def get_template(cls):
        raise NotImplementedError('implement in subclass')

    def build_template(self, context: Dict = None):
        if context is None:
            context = {}
        template = self.get_template()
        return f'{template}'

    @property
    def usage(self):
        return self._usage

class CurlUsageRenderer(BaseUsageRenderer):

    def __init__(self):
        pass

    def perform(self, data):
        pass

    @classmethod
    def get_template(self):
        entrypoint = 'curl'
        return """{entrypoint}"""
