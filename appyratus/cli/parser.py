from abc import abstractmethod

from appyratus.decorators import memoized_property


class Parser(object):
    def __init__(self, name=None, args=None, subparsers=None, perform=None):
        """
        # Args
        - `name`, TODO
        - `args`, TODO
        - `subparsers`, TODO
        - `perform`, TODO
        """
        #print('>>> INIT {} ({})'.format(name, self.__class__.__name__))
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
        if perform:
            self._perform = perform
        elif hasattr(self, 'perform') and callable(self.perform):
            self._perform = self.perform
        else:
            self._perform = None

    def build(self, parent=None, *args, **kwargs):
        """
        Build
        """
        #print('>>> BUILD {} ({})'.format(self.name, self.__class__.__name__))
        self.parent = parent
        self._parser = self.build_parser()
        if self._subparsers:
            self._subparser = self.build_subparser()
        self.build_subparsers()
        self.build_args()

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
