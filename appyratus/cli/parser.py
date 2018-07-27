from appyratus.decorators import memoized_property


class Parser(object):
    def subparsers(self):
        """
        The subparsers available to this parser.
        """
        if self._subparsers:
            return self._subparsers
        return []

    def args(self):
        """
        The args available to this parser.
        """
        if self._args:
            return self._args
        return []

    def __init__(
        self, name=None, parent=None, args=None, subparsers=None, parser=None
    ):
        """
        # Args
        - `name`, TODO
        - `args`, TODO
        - `subparsers`, TODO
        - `parent`, TODO
        """
        self.name = name
        print('>>> INIT {} ({})'.format(self.name, self))
        self.parent = parent
        # set any provided args or subparsers
        # they will be processed later on
        self._args = []
        if hasattr(self, 'args') and callable(self.args):
            self._args.extend(self.args())
        if args:
            self._args.extend(args)
        # subparsers
        self._subparsers = []
        if hasattr(self, 'subparsers') and callable(self.subparsers):
            self._subparsers.extend(self.subparsers())
        if subparsers:
            self._subparsers.extend(subparsers)
        # these are only available at time of build
        self._parser = None
        self.cli_args = None

    def build(self, parser=None, *args, **kwargs):
        """
        Build
        """
        print('>>> BUILD {} ({})'.format(self.name, self))
        self._parser = self.build_parser()
        self._subparser = self.build_subparser()
        self.build_subparsers()
        cli_args, unknown_cli_args = self.parse_cli_args()
        self.cli_args = cli_args
        self.build_args()

    def build_subparsers(self):
        """
        For all of the initialized subparsers, proceed to build them.
        """
        if not self._subparser or not self._subparsers:
            return
        for subparser in self._subparsers:
            subparser.build(self)

    def build_args(self):
        """
        Build parser arguments
        """
        if not self._args:
            return
        for arg in self._args:
            arg.build(self)

    def build_parser(self, *args, **kwargs):
        raise NotImplementedError('define in subclass')

    def build_subparser(self):
        raise NotImplementedError('define in subclass')

    def perform(self, *args, **kwargs):
        pass

    @property
    def subparsers_by_name(self):
        return {s.name: s for s in self._subparsers}

    def parse_cli_args(self):
        """
        Parse arguments from command-line
        """
        cli_args, unknown = self._parser.parse_known_args()

        # now combine known and unknown arguments into a single dict
        args_dict = {
            k: getattr(cli_args, k)
            for k in dir(cli_args) if not k.startswith('_')
        }

        # build a custom type with the combined argument names as attributes
        arguments = type('Arguments', (object, ), args_dict)()

        return (
            arguments,
            unknown,
        )

    def parse_unknown_args(self):
        for i in range(0, len(unknown), 2):
            k = unknown[i]
            try:
                v = unknown[i + 1]
                args_dict[k.lstrip('-')] = v
            except Exception as err:
                print('unmatched arg "{}"'.format(k))
