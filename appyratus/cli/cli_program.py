import argparse
from inspect import isclass

from .parser import Parser


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
        super().__init__(*args, **kwargs)
        self.version = version
        self.tagline = tagline
        self.defaults = defaults or {}
        self._func = None

    def build(self, *args, **kwargs):
        """
        Build program
        """
        super().build(*args, **kwargs)
        self.add_version_arg()
        self.cli_args = self.parse_cli_args()

    def build_parser(self, *args, **kwargs):
        """
        Build main program parser for interactivity.
        """
        # setup the parser with defaults and version information
        parser = argparse.ArgumentParser(
            prog=self.name, description='', epilog=''
        )
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
        return "{name} {version}, {tagline}".format(
            name=self.name, version=self.version, tagline=self.tagline
        )

    def route_action(self, action: str = None):
        """

        Argparser will recognize the called subparser (at whatever depth) and
        use the supplied func to deliver

        Previously, using the provided action, locate the matching subparser
        and perform the action bound to this method.

        The default action is to print usage.
        """
        if not self._perform:
            self.show_usage()
            return
        res = self._perform()
        return res

    def run(self):
        """
        # Run this program
        """
        self.build()
        action_res = self.route_action()


    def parse_cli_args(self):
        """
        # Parse arguments from command-line
        """
        # let argparser do the initial parsing
        cli_args, unknown = self._parser.parse_known_args()

        # now combine known and unknown arguments into a single dict
        args_dict = {
            k: getattr(cli_args, k)
            for k in dir(cli_args) if not k.startswith('_') and k is not 'func'
        }

        # XXX we want the func reference as this points directly to the
        # subparsers perform, and we don't want it in the cli args, and
        # handling it should probably not go here anyway, but it is
        if hasattr(cli_args, 'func'):
            self._perform = cli_args.func

        # and any unknown pairs will get added
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
