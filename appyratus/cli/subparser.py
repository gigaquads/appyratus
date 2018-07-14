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

    def __init__(self, name, help=None, defaults=None, args=None):
        self.name = name
        self.help = help
        self.defaults = defaults or {}
        self.args = args or []
