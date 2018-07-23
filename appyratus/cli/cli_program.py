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
        self,
        name=None,
        version=None,
        tagline=None,
        defaults=None,
        *args,
        **kwargs
    ):
        self.name = name
        self.version = version
        self.tagline = tagline
        self.defaults = defaults or dict(action=None)
        super().__init__(*args, **kwargs)

    def build_parser(self):
        """
        Build parser for interactivity
        """
        # setup the parser with defaults and version information
        parser = argparse.ArgumentParser(prog=self.name)
        parser.set_defaults(**self.defaults)
        # support version number
        if self.version:
            parser.add_argument(
                '-v',
                '--version',
                action='version',
                help='The version of {}'.format(self.name),
                version=self.show_info()
            )

        return parser

    def show_usage(self):
        """
        Output program usage
        """
        self.parser.print_usage()

    def show_info(self):
        """
        Construct a program display line representing information about the
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
        subparsers_by_name = {s.name: s for s in self.subparsers()}
        if action in subparsers_by_name.keys():
            subparser = subparsers_by_name[action]
            perform = getattr(subparser, 'perform')
            if not perform:
                raise Exception('no perform for subparser {}'.format(action))
            res = perform(self)
        else:
            self.show_usage()
        return res

    def run(self):
        """
        Run this program
        """
        action_res = self.route_action(action=self.args.action)
