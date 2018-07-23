class Parser(object):
    @staticmethod
    def subparsers():
        """
        The subparsers available to this parser.
        """
        return []

    @staticmethod
    def args():
        """
        The args available to this parser.
        """
        return []

    def __init__(self, *args, **kwargs):
        self.parser = self.build_parser()
        self.subparser_group = self.build_subparser_group()
        self.build_subparsers()
        self.args = self.parse_args()

    def build_parser(self):
        raise NotImplementedError('define in subclass')

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

        import ipdb
        ipdb.set_trace()
        print('wat')
        return arguments
