class ArgSchema(object):
    flags = None
    type = None
    default = None
    help = None


class Arg(object):
    def __init__(
        self, name=None, flags=None, type=None, default=None, help=None
    ):
        self.name = name
        self.flags = flags
        self.type = type
        self.default = default or {}
        self.help = help


class StrArg(object):
    pass
