class Arg(object):
    """
    # Arg
    """

    def __init__(
        self,
        name=None,
        flags=None,
        dtype=None,
        default=None,
        usage=None,
        action=None,
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
        self.dtype = dtype or str
        self.default = default
        self.usage = usage
        self.action = action

    def build(self, parent):
        """
        """
        # add arguments
        return parent._parser.add_argument(
            *self.flags,
            type=self.dtype,
            default=self.default,
            help=self.usage,
            action=self.action
        )


class PositionalArg(Arg):
    """
    # Positional Arg
    A positional argument is required by nature.  By default will set the flags
    to match the provided name of the argument.
    """

    def __init__(self, name=None, flags=None, *args, **kwargs):
        if name and not flags:
            flags = (name, )
        super().__init__(name=name, flags=flags, *args, **kwargs)


class OptionalArg(Arg):
    """
    # Optional Arg
    An optional argument is not required, however like a positional argument it
    will default flags to look as such. In that it uses the first letter of the
    name `-j`, and the name itself `--jesus`.
    """

    def __init__(
        self,
        name=None,
        flags=None,
        short_flag=None,
        long_flag=None,
        *args,
        **kwargs
    ):
        short_flag = True if short_flag is None else short_flag
        long_flag = True if long_flag is None else long_flag
        if name and not flags:
            flags = []
            if short_flag:
                flags.append('-{}'.format(name[0]))
            if long_flag:
                flags.append('--{}'.format(name))
        print(name, flags)
        super().__init__(name=name, flags=tuple(flags), *args, **kwargs)


class FlagArg(Arg):
    """
    # Flag Arg
    An argument for specifying a client flag, likely connected to a
    boolean value.  This is similar to an optional argument, in that
    it is not required, yet it only exists with a single dash prefix,
    and requires no value to be specified.  E.g., `-verbose`, `-all`
    """

    def __init__(self, name=None, flags=None, *args, **kwargs):
        flags = ('-{}'.format(name), )
        super().__init__(name=name, flags=flags, *args, **kwargs)
