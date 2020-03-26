import inspect
from abc import abstractmethod

from appyratus import files
from appyratus.memoize import memoized_property
from appyratus.utils import PathUtils


class Parser(object):

    def __init__(self, name=None, args=None, subparsers=None, perform=None):
        """
        # Args
        - `name`, the name of this parser
        - `args`, arguments for this parser
        - `subparsers`, subparsers related to this parser, which are
          just parsers themselves.  Subparsers can also be defined as
          a method on the parser class, however this method will take precedence
        - `perform`, a callable to execute when this parser runs
        """
        self.name = name
        self._parser = None
        self._subparser = None
        # args
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
        # perform
        if perform is not None:
            self._perform = perform
        elif hasattr(self, 'perform') and callable(self.perform):
            self._perform = self.perform
        else:
            self._perform = None

    def build(self, parent=None, *args, **kwargs):
        """
        Build
        """
        self.parent = parent
        self._parser = self.build_parser()
        self.register_custom_types(self._parser)
        if self._subparsers:
            self._subparser = self.build_subparser()
        self.build_subparsers()
        self.build_args()

    def register_custom_types(self, parser):
        """
        Register custom types for this program
        """

        def comma_separated_list(value):
            """
            Take a value and split it by the all-separating comma
            """
            if not value:
                return
            return value.split(',')

        parser.register('type', 'comma_separated_list', comma_separated_list)

        def file_type(value):
            ext = PathUtils.get_extension(value)

            known_file_type = None
            classes = inspect.getmembers(files)
            for name, obj in classes:
                if not issubclass(obj, files.File):
                    continue
                if ext in obj.extensions():
                    known_file_type = obj
                    break
            data = known_file_type.read(value)
            return data

        parser.register('type', 'file_type', file_type)

    @abstractmethod
    def build_parser(self):
        """
        Build parser
        """
        raise NotImplementedError('define in subclass')

    @abstractmethod
    def build_subparser(self):
        """
        Build subparser
        """
        raise NotImplementedError('define in subclass')

    def args(self):
        """
        The args available to this parser.
        """
        if self._args:
            return self._args
        return []

    def build_args(self):
        """
        Build parser arguments
        """
        if not self._args:
            return
        for arg in self._args:
            arg.build(self)

    def subparsers(self):
        """
        The subparsers available to this parser.
        """
        if self._subparsers:
            return self._subparsers
        return []

    def build_subparsers(self):
        """
        For all of the initialized subparsers, proceed to build them.
        """
        if not self._subparsers:
            return
        for subparser in self._subparsers:
            subparser.build(self)

    @property
    def subparsers_by_name(self):
        return {s.name: s for s in self._subparsers}
