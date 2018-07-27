import argparse
from inspect import isclass

from .parser import Parser

INFO_FORMAT = "{name} {version}, {tagline}"


class CliProgram(Parser):
    """
    # Command-line interface program
    An interface to your program

    """

    def __init__(
        self, version=None, tagline=None, defaults=None, *args, **kwargs
    ):
        """
        # Args
        - `version`, TODO
        - `tagline`, TODO
        - `defaults`, TODO
        """
        self.version = version
        self.tagline = tagline
        self.defaults = defaults or dict(action=None)
        super().__init__(*args, **kwargs)

    def build_parser(self, *args, **kwargs):
        """
        Build main program parser for interactivity.
        """
        # setup the parser with defaults and version information
        parser = argparse.ArgumentParser(prog=self.name)
        parser.set_defaults(**self.defaults)
        return parser

    def build_subparser(self):
        """
        Build subparser
        """
        subparser = self._parser.add_subparsers(
            title='sub-commands', help='sub-command help'
        )
        return subparser

    def add_version_arg(self):
        # TODO
        # support version number
        if self.version:
            self._parser.add_argument(
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
        return INFO_FORMAT.format(
            **{
                'name': self.name,
                'version': self.version,
                'tagline': self.tagline
            }
        )

    def route_action(self, action: str):
        """
        Using the provided action, locate the matching subparser and perform
        the action bound to this method.  The default action is to print usage.
        """
        res = None
        self.cli_args.func(self)
        if action in self.subparsers_by_name.keys():
            subparser = self.subparsers_by_name[action]
            perform = getattr(subparser, 'perform')
            if not perform:
                raise Exception('no perform for subparser {}'.format(action))
            res = perform(1, 2)
        else:
            self.show_usage()
        return res

    def run(self):
        """
        Run this program
        """
        self.build()
        action_res = self.route_action(action=self.cli_args.action)
