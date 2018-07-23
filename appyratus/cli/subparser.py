from .arg import Arg
from .parser import Parser


class Subparser(Parser):
    """
    Subparser
    """

    def __init__(
        self,
        name,
        usage=None,
        defaults=None,
        parent=None,
        subparsers=None,
        args=None,
        perform=None
    ):
        self.name = name
        self.usage = usage or ''
        self.defaults = defaults or {'action': self.name}
        self.args = args or []
        if perform:
            self.perform = perform

    def perform(self, program):
        """
        Action that will be called upon subparser when selected
        """
        raise NotImplementedError('override in subclass')

    def build(self, program):
        """
        Build a subparser and all of its arguments
        """
        subparser_obj = program.subparser_group.add_parser(
            self.name, help=self.usage
        )
        # set defaults for each subparser
        subparser_obj.set_defaults(**self.defaults)

        # add arguments
        for arg in self.args:
            subparser_obj.add_argument(
                *arg.flags,
                type=arg.dtype,
                default=arg.default,
                help=arg.usage
            )
