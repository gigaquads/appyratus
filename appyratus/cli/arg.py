class Arg(object):
    """
    # Arg
    """

    def __init__(
        self, name=None, flags=None, dtype=None, default=None, usage=None
    ):
        """
        # Args
        - `name`, TODO
        - `flags`, TODO
        - `dtype`, TODO
        - `default`, TODO
        - `usage`, TODO
        """
        self.name = name
        self.flags = flags
        self.dtype = dtype
        self.default = default or {}
        self.usage = usage

    def build(self, parent):
        """
        """
        # add arguments
        return parent._parser.add_argument(
            *arg.flags,
            type=arg.dtype,
            default=arg.default,
            help=arg.usage
        )
