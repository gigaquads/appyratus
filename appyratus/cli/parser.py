from appyratus.decorators import memoized_property


class Parser(object):
    @memoized_property
    def subparsers(self):
        """
        The subparsers available to this parser.
        """
        if self._subparsers:
            return self._subparsers
        return []

    @memoized_property
    def args(self):
        """
        The args available to this parser.
        """
        if self._args:
            return self._args
        return []

    def __init__(self, parent=None, args=None, subparsers=None, parser=None):
        """
        # Args
        - `args`, TODO
        - `subparsers`, TODO
        - `parent`, TODO
        """
        print('>>> INIT {} ({})'.format(self.name, self))
        self.parent = parent
        # set any provided args or subparsers
        # they will be processed later on
        self._args = args
        import ipdb
        ipdb.set_trace()
        print('wat')
        self._subparsers = [s for s in subparsers]
        # these are only available at time of build
        self._parser = None
        self.cli_args = None

    def build(self, parent=None, *args, **kwargs):
        """
        Build
        """
        print('>>> BUILD {} ({})'.format(self.name, self))
        self._parser = self.build_parser(self)
        import ipdb
        ipdb.set_trace()
        print('wat')
        #if self._parser:

    #if self.subparsers():
    #self.subparser_group = self.build_subparser_group()
    #    self.build_subparsers()
    #cli_args, unknown_cli_args = self.parse_cli_args()
    #self.cli_args = cli_args

    def build_parser(self, *args, **kwargs):
        raise NotImplementedError('define in subclass')

    def build_subparser_group(self):
        """
        Build subparser group
        """
        raise NotImplementedError('define in subclass')

    def build_subparsers(self):
        """
        For all of the initialized subparsers, proceed to build them.
        """
        pass
        for subparser in self.subparsers:
            subparser.build()

    @property
    def subparsers_by_name(self):
        return {s.name: s for s in self.subparsers}

    def parse_cli_args(self):
        """
        Parse arguments from command-line
        """
        cli_args, unknown = self._parser.parse_known_args()
        #for k, v in self.subparsers_by_name.items():
        #    print(k, v)

        # now combine known and unknown arguments into a single dict
        args_dict = {
            k: getattr(cli_args, k)
            for k in dir(cli_args) if not k.startswith('_')
        }

        # build a custom type with the combined argument names as attributes
        arguments = type('Arguments', (object, ), args_dict)()

        return arguments, unknown

    def parse_unknown_args(self):
        for i in range(0, len(unknown), 2):
            k = unknown[i]
            try:
                v = unknown[i + 1]
                args_dict[k.lstrip('-')] = v
            except Exception as err:
                print('unmatched arg "{}"'.format(k))
