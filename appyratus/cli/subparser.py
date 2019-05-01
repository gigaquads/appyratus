from .arg import Arg
from .parser import Parser


class Subparser(Parser):
    """
    # Subparser
    """

    def __init__(self, usage=None, defaults=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #if not self.name:
        #    self.name = self.__class__
        self.usage = usage or ''
        self.defaults = defaults if defaults and defaults is not None else {}
        self.defaults['func'] = self._perform

    def build_parser(self, *args, **kwargs):
        """
        Build the Subparser's parser
        """
        parser = self.parent._subparser.add_parser(self.name, help=self.usage)
        parser.set_defaults(**self.defaults)
        return parser

    def build_subparser(self, *args, **kwargs):
        """
        Build the Subparser's subparser
        """
        subparser = self._parser.add_subparsers(
            title='{} sub-commands'.format(self.name),
            help='{} sub-command help'.format(self.name)
        )
        return subparser
