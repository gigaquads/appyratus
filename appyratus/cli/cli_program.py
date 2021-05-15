from appyratus.schema.schema import Schema
import argparse

from typing import (List, Tuple, Text, Callable, Union, Dict, Optional)

from appyratus.logging import logger
from appyratus.utils.dict_utils import DictUtils
from appyratus.schema import fields
from appyratus.schema.fields import Field

from .parser import Parser
from .arg import ListArg, PositionalArg, FlagArg, OptionalArg


class CliProgram(Parser):
    """
    # Command-line interface program
    An interface to your program


    # Example Usage
    from appyratus.cli import CliProgram, Args
    ```python
    class MyLameProgram(CliProgram):
        lame_positional_arg = PositionalArg()
        lame_optional_arg = OptionalArg()
        lame_flag_arg = FlagArg()

    program = MyLameProgram()
    program.run()
    ```
    """

    @classmethod
    def from_schema(
        cls,
        func: Callable,
        schema: Union['Schema', Dict[Text, Field]] = None,
    ) -> 'CliProgram':

        if schema is None:
            schema = Schema(allow_additional=True)
        elif not isinstance(schema, Schema):
            fields_dict = schema
            schema_class = Schema.factory('CliArgumentsSchema', fields_dict)
            schema = schema_class(allow_additional=True)

        arguments = []
        for name, field in schema.fields.items():
            if isinstance(field, fields.Bool):
                arg = FlagArg(name)
            elif isinstance(field, (fields.List, fields.Set)):
                arg = ListArg(name)
            elif field.required or not field.nullable:
                if field.default is None:
                    arg = PositionalArg(name)
                else:
                    arg = OptionalArg(name)
            else:
                arg = OptionalArg(name)

            if field.default is not None:
                if not isinstance(field.default, type) and callable(field.default):
                    arg.default = field.default()
                else:
                    arg.default = field.default

            arguments.append(arg)

        program_class = type(
            'CliProgram', (cls, ), {
                'perform': staticmethod(func),
                'args': arguments,
            }
        )

        return program_class(func=func, schema=schema, expand_args=True)

    def __init__(
        self,
        version=None,
        tagline=None,
        defaults=None,
        func=None,
        cli_args=None,
        merge_unknown: bool = True,
        expand_args: bool = False,
        schema: Optional['Schema'] = None,
        unknown_prefix: Text = '_',
        custom_dtype_converter: Callable = None,
        *args,
        **kwargs
    ):
        """
        # Args
        - `version`, TODO
        - `tagline`, TODO
        - `defaults`, TODO
        """
        super().__init__(*args, **kwargs)
        self.version = version
        self.tagline = tagline
        self.defaults = defaults or {}
        self._expand_args = expand_args
        self._func = func
        self._schema = schema
        self._cli_args = None
        self._unknown_cli_args = None or cli_args
        self._unknown_prefix = unknown_prefix or '_'
        self._raw_cli_args = cli_args
        self._merge_unknown = merge_unknown if merge_unknown is not None else True
        self._custom_dtype_converter = custom_dtype_converter

    @property
    def cli_args(self):
        return self._cli_args

    @property
    def unknown_cli_args(self):
        return self._unknown_cli_args

    def build(self, *args, **kwargs):
        """
        Build program
        """
        super().build(*args, **kwargs)
        self.add_version_arg()
        self._cli_args, self._unknown_cli_args = self.parse_cli_args(
            args=self._unknown_cli_args, merge_unknown=self._merge_unknown
        )

    def build_parser(self, *args, **kwargs):
        """
        Build main program parser for interactivity.
        """
        # setup the parser with defaults and version information
        parser = argparse.ArgumentParser(prog=self.name, description='', epilog='')
        parser.set_defaults(**self.defaults)
        return parser

    def build_subparser(self):
        """
        Build subparser
        """
        subparser = self._parser.add_subparsers(
            title='{} sub-commands'.format(self.name),
            help='{} sub-command help'.format(self.name),
        )
        return subparser

    def add_version_arg(self):
        # XXX this uses the underlying parser structure make it an Arg
        if self.version:
            self.add_argument(
                '-v',
                '--version',
                action='version',
                help='The version of {}'.format(self.name),
                version=self.show_info()
            )

    def show_usage(self):
        """
        Output program usage
        """
        self._parser.print_usage()

    def show_info(self):
        """
        Construct a display line representing information about the
        program.
        """
        return "{name} {version}, {tagline}".format(
            name=self.name, version=self.version, tagline=self.tagline
        )

    def route_action(self, action: str = None):
        """
        Argparser will recognize the called subparser (at whatever depth) and
        use the supplied func to deliver

        The default action is to print usage.
        """
        kwargs = {arg.name: getattr(self.cli_args, arg.name) for arg in self._args}
        if not self._perform:
            res = self.show_usage()
        elif self._expand_args:
            res = self._perform(**kwargs)
        else:
            res = self._perform(self)
        return res

    def run(self):
        """
        # Run this program and return the results
        """
        self.build(custom_dtype_converter=self._custom_dtype_converter)
        action_res = self.route_action()
        return action_res

    def parse_cli_args(
        self,
        args: list = None,
        merge_unknown: bool = True,
        unflatten_keys: bool = True,
    ) -> Tuple['Arguments', List]:
        """
        # Parse arguments from command-line
        """
        # let argparser do the initial parsing
        cli_args, cli_unknown_args = self._parser.parse_known_args(args)

        # now combine known and unknown arguments into a single dict
        args_dict = {
            k: getattr(cli_args, k)
            for k in dir(cli_args) if not k.startswith('_') and k != 'func'
        }

        # XXX we want the func reference as this points directly to the
        # subparsers perform, and we don't want it in the cli args, and
        # handling it should probably not go here anyway, but it is
        if hasattr(cli_args, 'func'):
            self._perform = cli_args.func

        # process unknown args
        unknown_args = []
        unknown_kwargs = {}

        skip_next = False
        for i in range(0, len(cli_unknown_args)):
            k = cli_unknown_args[i]
            kid = k.lstrip('-')
            has_dash = (k[0] == '-') if k else False
            is_arg = not has_dash and not skip_next
            if skip_next:
                skip_next = False
                continue
            if is_arg:
                unknown_args.append(k)
            else:
                try:
                    v = cli_unknown_args[i + 1]
                    unknown_kwargs[kid] = v
                    skip_next = True
                except Exception as err:
                    logger.info(f'unmatched kwarg "{kid}"')

        if merge_unknown:
            # and any unknown args pairs will get added
            args_dict.update(unknown_kwargs)

        if unflatten_keys:
            # this will expand any keys that are dot notated with the
            # expectation of being a nested dictionary reference
            args_dict = DictUtils.unflatten_keys(args_dict)

        if self._schema:
            processed_args_dict = self._schema.process(args_dict, strict=True)
            for k, v in processed_args_dict.items():
                args_dict[k] = v

        arguments = type('Arguments', (object, ), args_dict)()
        arguments.unknown = unknown_kwargs

        return arguments, cli_unknown_args
