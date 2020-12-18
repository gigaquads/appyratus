from typing import Type, Callable, Text, Dict


class FieldAdapter(object):
    """
    TypeAdapter is used by anything that needs to be able to convert an
    appyratus Field type to a corresponding field type used by some other
    library. See the SqlalchemyDao in the `ravel` project for an example.
    """

    def __init__(
        self,
        field_class: Type['Field'],
        on_adapt: Callable = None,
        on_encode: Callable = lambda x: x,
        on_decode: Callable = lambda x: x,
    ):
        self.field_class = field_class
        self.on_adapt = on_adapt
        self.on_encode = on_encode
        self.on_decode = on_decode

    def encode(self, obj):
        return self.on_encode(obj)

    def decode(self, obj):
        return self.on_decode(obj)