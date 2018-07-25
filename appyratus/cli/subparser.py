from .arg import Arg
from .parser import Parser


class Subparser(Parser):
    """
    Subparser
    """

    def __init__(
        self, name, usage=None, defaults=None, perform=None, *args, **kwargs
    ):
        self.name = name
        self.usage = usage or ''
        self.defaults = defaults or {'action': self.name}
        super().__init__(*args, **kwargs)
        if perform:
            self.perform = perform

    def perform(self, program):
        """
        Action that will be called upon subparser when selected
        """
        raise NotImplementedError('override in subclass')

    def build_parser(self, parent, *args, **kwargs):
        """
        Build the Subparsers parser
        """
        parser = parent.subparser_group.add_parser(self.name, help=self.usage)
        parser.set_defaults(**self.defaults)
        return parser

    def build_args(self, program):
        """
        Build a subparser and all of its arguments
        """

        # add arguments
        for arg in self.args():
            subparser_obj.add_argument(
                *arg.flags,
                type=arg.dtype,
                default=arg.default,
                help=arg.usage
            )
