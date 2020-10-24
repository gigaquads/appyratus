import argparse
from inspect import isclass
from typing import (
    List,
    Tuple,
)

from appyratus.logging import logger 
from appyratus.utils import DictUtils

from .parser import Parser


class CliProgram(Parser):
    """
    # Command-line interface program
    An interface to your program


    # Example Usage
    from appyratus.cli import CliProgram, Args
    ```
    class MyLameProgram(CliProgram):
        lame_positional_arg = PositionalArg()
        lame_optional_arg = OptionalArg()
        lame_flag_arg = FlagArg()

    program = MyLameProgram()
    program.run()
    ```
    """

    def __init__(
        self,
        version=None,
        tagline=None,
        defaults=None,
        cli_args=None,
        merge_unknown: bool = True,
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
        self._func = None
        self._cli_args = None
        self._unknown_cli_args = None or cli_args
        self._raw_cli_args = cli_args
        self._merge_unknown = merge_unknown or True

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
            help='{} sub-command help'.format(self.name)
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
        if not self._perform:
            self.show_usage()
            return
        res = self._perform(self)
        return res

    def run(self):
        """
        # Run this program and return the results
        """
        self.build()
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

        last_arg_id = 0
        for i in range(0, len(cli_unknown_args)-1):
            v = cli_unknown_args[i]
            if v[0] == '-':
                last_arg_id = i
                break
            unknown_args.append(v)

        for i in range(last_arg_id, len(cli_unknown_args), 2):
            k = cli_unknown_args[i]
            try:
                v = cli_unknown_args[i + 1]
                unknown_kwargs[k.lstrip('-')] = v
            except Exception as err:
                logger.info(f'unmatched arg "{k}"')

        if merge_unknown:
            # and any unknown args pairs will get added
            args_dict.update(unknown_kwargs)

        if unflatten_keys:
            # this will expand any keys that are dot notated with the
            # expectation of being a nested dictionary reference
            args_dict = DictUtils.unflatten_keys(args_dict)

        arguments = type('Arguments', (object, ), args_dict)()

        return arguments, cli_unknown_args
