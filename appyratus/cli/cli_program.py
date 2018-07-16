import argparse
from inspect import isclass

from .subparser import Subparser

INFO_FORMAT = "{name} {version}, {tagline}"
DEFAULTS = dict(action=None)


class CliProgram(object):
    """
    # Prog
    An interface to your program.
    """

    def __init__(self, name=None, version=None, tagline=None, defaults=None):
        self.name = name
        self.version = version
        self.tagline = tagline
        self.defaults = defaults or DEFAULTS
        self.parser = self.build_parser()
        self.subparser_group = self.build_subparser_group()
        self.build_subparsers()
        self.args = self.parse_args()

    @staticmethod
    def subparsers():
        """
        The subparsers available to this program.
        """
        return []

    def parse_args(self):
        """
        Parse arguments from command-line
        """
        args, unknown = self.parser.parse_known_args()

        # now combine known and unknown arguments into a single dict
        args_dict = {
            k: getattr(args, k)
            for k in dir(args) if not k.startswith('_')
        }

        for i in range(0, len(unknown), 2):
            k = unknown[i]
            try:
                v = unknown[i + 1]
                args_dict[k.lstrip('-')] = v
            except Exception as err:
                print('unmatched arg "{}"'.format(k))

        # build a custom type with the combined argument names as attributes
        arguments = type('Arguments', (object, ), args_dict)()

        return arguments

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
                version=self.display_info()
            )

        return parser

    def build_subparser_group(self):
        """
        Build subparser group
        """
        subparser_group = self.parser.add_subparsers(
            title='sub-commands', help='sub-command help'
        )
        return subparser_group

    def build_subparsers(self):
        """
        For all of the initialized subparsers, proceed to build them.
        """
        for subparser in self.subparsers():
            subparser.build(self)

    def display_usage(self):
        """
        Output program usage
        """
        self.parser.print_usage()

    def display_info(self):
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
            self.display_usage()
        return res

    def run(self):
        """
        Run this program
        """
        action_res = self.route_action(action=self.args.action)
