class Arg(object):
    def __init__(
        self, name=None, flags=None, dtype=None, default=None, usage=None
    ):
        self.name = name
        self.flags = flags
        self.dtype = dtype
        self.default = default or {}
        self.usage = usage
