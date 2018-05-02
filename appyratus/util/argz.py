import argparse

VERSION_FORMAT = "{name} {version}, {tagline}"
DEFAULTS = dict(action=None)


class ProgSchema(object):
    prog = None
    name = None
    version = None
    tagline = None


class Prog(object):
    def __init__(self, data: dict=None):
        self.data = data

        self._subparsers = []
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, Subparser):
                self._subparsers.append(value)

        self.parser = self.build_parser()
        self.args = self.parse_args()

    @property
    def name(self):
        return self.data.get('name')

    @property
    def defaults(self):
        return self.data.get('defaults', DEFAULTS)

    @property
    def version(self):
        return self.data.get('version')

    @property
    def subparsers(self):
        import ipdb
        ipdb.set_trace()
        return self._subparsers

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
                    subparser.name, help=subparser.help
                )
                # set defaults for each subparser
                subparser_obj.set_defaults(**subparser.defaults)
                for arg in subparser.args:
                    subparser_obj.add_argument(
                        *arg.flags,
                        type=arg.type,
                        default=arg.default,
                        help=arg.help
                    )
        return parser

    def print_usage(self):
        self.parser.print_usage()

    def route_action(self, action: str):
        """
        The default action is to print usage
        """
        res = None
        if action and hasattr(self, action):
            res = getattr(self, action)()
        else:
            self.print_usage()
        return res

    def run(self):
        action_res = self.route_action(action=self.args.action)


class ArgSchema(object):
    flags = None
    type = None
    default = None
    help = None


class Arg(object):
    def __init__(self, flags=None, type=None, default=None, help=None):
        self.flags = flags
        self.type = type
        self.default = default
        self.help = help


class StrArg(object):
    pass


class SubparserSchema(object):
    name = None
    help = None
    defaults = None


class Subparser(object):
    def __init__(self):
        self._args = []
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, Arg):
                self._args.append(value)

    @property
    def args(self):
        return self._args


def version():
    return VERSION_FORMAT.format(**CONFIG)
