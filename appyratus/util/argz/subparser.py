from .arg import Arg


class SubparserSchema(object):
    """
    Subparser schema
    """
    name = None
    help = None
    defaults = None


class Subparser(object):
    """
    Subparser
    """

    def __init__(self):
        self._args = []
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, Arg):
                self._args.append(value)

    @property
    def args(self):
        return self._args
