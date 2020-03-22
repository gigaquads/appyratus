from typing import List
from appyratus.utils import DictUtils


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
        nargs=None,
        choices: List = None
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
        self.default = default
        self.usage = usage
        self.action = action
        self.nargs = nargs
        self.choices = choices

    @property
    def kwargs(self):
        return {
            'default': self.default,
            'help': self.usage,
            'action': self.action,
            'nargs': self.nargs,
            'type': self.dtype,
            'choices': self.choices,
        }

    def build(self, parent):
        """
        """
        # add arguments

        # remove empty values from kwargs. argparser will shit the
        # bed if it finds one that is empty and shouldn't belong in
        # conjunction with another Args' kwargs
        kwargs = DictUtils.remove_keys(self.kwargs, values=[None])
        return parent._parser.add_argument(*self.flags, **kwargs)


class PositionalArg(Arg):
    """
    # Positional Arg
    A positional argument is required by nature.  By default will set the flags
    to match the provided name of the argument.
    """

    def __init__(self, name=None, flags=None, usage=None, dtype=None, action=None):
        if name and not flags:
            flags = (name, )
        super().__init__(name=name, flags=flags, usage=usage, dtype=dtype, action=action)


class OptionalArg(Arg):
    """
    # Optional Arg
    An optional argument is not required, however like a positional argument it
    will default flags to look as such. In that it uses the first letter of the
    name `-j`, and the name itself `--jesus`.
    """

    def __init__(
        self, name=None, flags=None, short_flag=None, long_flag=None, *args, **kwargs
    ):
        short_flag = True if short_flag is None else short_flag
        long_flag = True if long_flag is None else long_flag
        if flags is None:
            flags = []
        if name and not flags:
            if short_flag:
                flags.append('-{}'.format(name[0]))
            if long_flag:
                flags.append('--{}'.format(name))
        super().__init__(name=name, flags=tuple(flags), *args, **kwargs)


class FlagArg(Arg):
    """
    # Flag Arg
    An argument for specifying a client flag, most commonly connected to a boolean
    "on/off" value.  This is similar to an optional argument, in that it is
    not required, yet it only exists with a single dash prefix, and
    requires no value to be specified.  E.g., `-lame`, `-lamest`
    """

    def __init__(self, name=None, default=None, usage=None, **kwargs):
        """
        # Intialize the Flag Arg

        # Args
        - `name`, the name of the arg
        - `value`, the boolean value that this flag will take on,
          True or False.  As this arg is optional and does not
          require a keyword value to be specified, it would be used
        """
        flags = ('-{}'.format(name), )
        if default is None:
            default = True
        if default is True:
            action = 'store_true'
        else:
            action = 'store_false'
        super().__init__(name=name, action=action, flags=flags, usage=usage)


class ListArg(OptionalArg):
    """
    # List Arg
    An argument for specifying multiple values for the same argument key
    """

    def __init__(
        self,
        name=None,
        default=None,
        usage=None,
        choices=None,
        comma_separated=True,
        **kwargs
    ):
        if not choices:
            choices = None
        if choices is not None:
            # dedupe choices
            pass
        self._choices = choices

        # by default the list arg supports parsing via the comma separated list
        # type, which splits up strings by comma.  this must utilize the extend
        # action as the result is a list
        if comma_separated:
            action = 'extend'
            dtype = 'comma_separated_list'
        else:
            action = 'append'
            dtype = None

        super().__init__(
            name=name,
            default=default,
            usage=usage,
            choices=choices,
            action=action,
            dtype=dtype
        )


class FileArg(Arg):
    pass
