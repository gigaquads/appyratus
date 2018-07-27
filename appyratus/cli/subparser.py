from .arg import Arg
from .parser import Parser


class Subparser(Parser):
    """
    # Subparser
    """

    def __init__(
        self,
        name=None,
        usage=None,
        defaults=None,
        perform=None,
        *args,
        **kwargs
    ):
        self.name = name
        self.usage = usage or ''
        if perform:
            self.perform = perform
        self.defaults = defaults or {
            'action': self.name,
            'func': self.perform,
        }
        super().__init__(*args, **kwargs)

    def perform(self, program):
        """
        Action that will be called upon subparser when selected
        """
        print('wooop')

    def build_parser(self, parent, *args, **kwargs):
        """
        Build the Subparsers parser
        """
        parser = parent._subparser.add_parser(self.name, help=self.usage)
        parser.set_defaults(**self.defaults)
        return parser

    def build_subparser(self, *args, **kwargs):
        subparser = self._parser.add_subparsers(
            title='sub-sub-commands', help='sub-sub-command help'
        )
        return subparser
