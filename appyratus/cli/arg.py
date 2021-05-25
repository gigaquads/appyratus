from typing import (
    Callable,
    List,
)

from appyratus.utils.dict_utils import DictUtils
from appyratus.utils.string_utils import StringUtils


class Arg(object):
    """
    # Arg
    """

    def __init__(
        self,
        name=None,
        flags=None,
        dtype=None,
        dest=None,
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
        self.dest = dest
        self.default = default
        self.usage = usage
        self.action = action
        self.nargs = nargs
        self.choices = choices

    @property
    def kwargs(self):
        return {
            'default': self.default,
            'dest': self.dest,
            'help': self.usage,
            'action': self.action,
            'nargs': self.nargs,
            'type': self.dtype,
            'choices': self.choices,
        }

    def build(self, parent, custom_dtype_converter: Callable = None):
        """
        """
        # add arguments

        # remove empty values from kwargs. argparser will shit the
        # bed if it finds one that is empty and shouldn't belong in
        # conjunction with another Args' kwargs
        kwargs = DictUtils.remove_keys(self.kwargs, values=[None])
        dtype = kwargs.get('type')
        if custom_dtype_converter:
            dtype = custom_dtype_converter(dtype)
        if dtype:
            # in cases when an unknown type is provided, like perhaps a class,
            # then assume a str type
            basic_type_known = dtype in (str, int, dict, list)
            registry_type_known = dtype in parent._parser._registries['type']
            if not callable(dtype) and not any([basic_type_known, registry_type_known]):
                kwargs['type'] = str
        return parent.add_argument(*self.flags, **kwargs)


class PositionalArg(Arg):
    """
    # Positional Arg
    A positional argument is required by nature.  By default will set the flags
    to match the provided name of the argument.
    """

    def __init__(
        self,
        name=None,
        flags=None,
        usage=None,
        dtype=None,
        action=None,
        choices=None,
    ):
        if name and not flags:
            flags = (name, )
        super().__init__(
            name=name,
            flags=flags,
            usage=usage,
            dtype=dtype,
            action=action,
            choices=choices
        )


class OptionalArg(Arg):
    """
    # Optional Arg
    An optional argument is not required, however like a positional argument it
    will utilize the name in order to gnerate the short and long flag. For
    example if the arg is `jesus`, it uses the first letter of the
    name `-j`, and the name in full `--jesus`.
    """

    def __init__(
        self, name=None, flags=None, short_flag=None, long_flag=None, *args, **kwargs
    ):
        short_flag = True if short_flag is None else short_flag
        long_flag = True if long_flag is None else long_flag
        if flags is None:
            flags = []
        if not isinstance(flags, list):
            flags = [flags]
        if not flags or short_flag or long_flag:
            if short_flag:
                short_name = name
                if short_flag is not True:
                    short_name = short_flag
                if short_name:
                    flags.append(f'-{short_name[0]}')
            if long_flag:
                long_name = name
                if long_flag is not True:
                    long_name = long_flag
                if long_name:
                    flags.append('--{}'.format(StringUtils.dash(long_name)))
                    flags.append('--{}'.format(StringUtils.snake(long_name)))
        super().__init__(name=name, flags=tuple(flags), *args, **kwargs)


class FlagArg(Arg):
    """
    # Flag Arg
    An argument for specifying a client flag, most commonly connected to a boolean
    "on/off" value.  This is similar to an optional argument, in that it is
    not required, yet it only exists with a single dash prefix, and
    requires no value to be specified.  E.g., `-lame`, `-lamest`
    """

    def __init__(self, name=None, store=None, usage=None, **kwargs):
        """
        # Intialize the Flag Arg

        # Args
        - `name`, the name of the arg
        - `store`, the boolean value that this flag will take on when the arg
          has been specified. when True default is False, when False default is True
        """
        flags = (
            '-{}'.format(StringUtils.dash(name)),
            '-{}'.format(StringUtils.snake(name)),
        )
        if store is None:
            store = True
        if store is True:
            action = 'store_true'
        else:
            action = 'store_false'
        dest = StringUtils.snake(name)
        super().__init__(name=name, dest=dest, action=action, flags=flags, usage=usage)


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


class FileArg(OptionalArg):
    """
    # File Arg
    Use the provided value as a file path, and load the file if a known
    extension can be detected.  Will return the contents of the file in a data
    structure
    """

    def __init__(self, allow_types: List = None, dtype=None, **kwargs):
        super().__init__(dtype='file_type', **kwargs)
