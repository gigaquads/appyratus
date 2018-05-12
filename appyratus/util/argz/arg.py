class ArgSchema(object):
    flags = None
    type = None
    default = None
    help = None


class Arg(object):
    def __init__(self, flags=None, type=None, default=None, help=None):
        self.flags = flags
        self.type = type
        self.default = default
        self.help = help


class StrArg(object):
    pass
