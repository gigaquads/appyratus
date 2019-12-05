import inspect

from typing import Tuple, Dict
from inspect import (
    Parameter,
    Signature,
    _empty as EMPTY,
)


class FuncUtils(object):
    @classmethod
    def partition_arguments(cls, signature, arguments: Dict) -> (Tuple, Dict):
        """
        Uses the function signature to partition the elements of the arguments
        dict into a list of positional arguments and a dict of keyword arguments
        that are expected by the function.
        """
        args, kwargs = [], {}
        if not isinstance(signature, Signature):
            assert callable(signature)
            signature = inspect.signature(signature)
        for param_name, param in signature.parameters.items():
            if param.kind == Parameter.POSITIONAL_OR_KEYWORD:
                if param.default is EMPTY:
                    args.append(arguments[param_name])
                else:
                    kwargs[param_name] = arguments.get(param_name)
            elif param.kind == Parameter.POSITIONAL_ONLY:
                args.append(arguments[param_name])
            elif param.kind == Parameter.KEYWORD_ONLY:
                kwargs[param_name] = arguments.get(param_name)
        return (tuple(args), kwargs)
