import inspect

from typing import (
    Type, Text, Callable, Union, Tuple, Optional
)


class TypeUtils:

    @classmethod
    def get_class_name(cls, obj) -> Optional[Text]:
        if not obj:
            return None
        if isinstance(obj, type):
            return obj.__name__
        else:
            return obj.__class__.__name__

    @classmethod
    def get_function_name(cls, obj: Callable) -> Optional[Text]:
        if inspect.isfunction(obj):
            return obj.__name__
        elif inspect.ismethod(obj):
            return obj.__func__.__name__
        elif inspect.isawaitable(obj):
            return obj.__qualname__
        else:
            return None

    @classmethod
    def is_proper_subclass(
        cls,
        child: Type,
        parent: Union[Type, Tuple[Type]],
    ) -> bool:
        return (
            isinstance(child, type)
            and parent is not child
            and issubclass(child, parent)
        )
