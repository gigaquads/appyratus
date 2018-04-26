import argparse

VERSION_FORMAT = "{name} {version}, {tagline}"
DEFAULTS = dict(action=None)


class ProgSchema(object):
    pass


class Prog(object):
    def __init__(self, prog, subparsers=None):
        self.prog = prog
        self.subparsers = subparsers
        self.parser = self.build_parser()
        self.args = self.parse_args()

    @property
    def name(self):
        return self.prog.get('name')

    @property
    def defaults(self):
        return self.prog.get('defaults', DEFAULTS)

    @property
    def version(self):
        return self.prog.get('version')

    def parse_args(self):
        args, unknown = self.parser.parse_known_args()

        # now combine known and unknown arguments into a single dict
        args_dict = {
            k: getattr(args, k)
            for k in dir(args) if not k.startswith('_')
        }

        for i in range(0, len(unknown), 2):
            k = unknown[i]
            v = unknown[i + 1]
            args_dict[k.lstrip('-')] = v

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
        if version:
            parser.add_argument(
                '-v',
                '--version',
                action='version',
                help='The version of {}'.format(self.version),
                version=version
            )
        # build subparsers for actionable requests
        subparser_groups = parser.add_subparsers(
            title='subcommands', help='sub-command help'
        )
        if self.subparsers:
            for subparser in self.subparsers:
                subparser_obj = subparser_groups.add_parser(
                    subparser.get('name'), help=subparser.get('help')
                )
                # set defaults for each subparser
                subparser_obj.set_defaults(**subparser.get('defaults'))
                for arg in subparser.get('args'):
                    subparser_obj.add_argument(
                        *arg.get('flags'),
                        type=arg.get('type'),
                        default=arg.get('default'),
                        help=arg.get('help')
                    )
        return parser

    def print_usage(self):
        self.parser.print_usage()


def version():
    return VERSION_FORMAT.format(**CONFIG)
