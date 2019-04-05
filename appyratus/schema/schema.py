import venusian

from typing import Type, Dict, Text, Set
from copy import deepcopy
from collections import namedtuple

from appyratus.memoize import memoized_property

from .fields import Field, Nested, List
from .exc import ValidationError


class schema_type(type):
    def __init__(cls, name, bases, dict_):
        type.__init__(cls, name, bases, dict_)
        fields = {}    # aggregator for all fields declared on the class

        def get_schema_from_field(field):
            schema = None
            if isinstance(field, Schema):
                schema = field
            if isinstance(field, Nested):
                schema = field.schema
            if isinstance(field, List):
                if isinstance(field.nested, Schema):
                    schema = field.nested
                elif isinstance(field.nested, Nested):
                    schema = field.nested.schema
            return schema

        for k, v in dict_.items():
            if isinstance(v, Field):
                delattr(cls, k)
                fields[k] = v
                if v.name is None:
                    # set field name to name declared on the class
                    v.name = k
                if v.source is None:
                    # default source key to declared name
                    v.source = v.name

        # save aggregated fields dict and child
        # schema list set on the new class
        cls.fields = fields
        cls.children = []
        cls.required_fields = {}
        cls.optional_fields = {}

        for k, field in cls.fields.items():
            # track required and optional fields
            if field.required:
                cls.required_fields[k] = field
            else:
                cls.optional_fields[k] = field
            # call any non-null on_create methods
            if field.on_create is not None:
                field.on_create(cls)
            # accumulate any schema delcared in the field
            child = get_schema_from_field(field)
            if child is not None:
                cls.children.append(child)


class Schema(Field, metaclass=schema_type):

    fields = None
    children = None

    @classmethod
    def factory(cls, name: str, fields: dict) -> Type['Schema']:
        """
        Convenience method for building new Schema classes from a dict of Field
        objects, using the given name as the name of the class object.
        """
        return type(name, (cls, ), fields)

    def __init__(self, allow_additional=False, **kwargs):
        super().__init__(**kwargs)
        self.tuple_factory = namedtuple(
            'results', field_names=['data', 'errors']
        )
        self.allow_additional = allow_additional

    def __getitem__(self, field_name: Text) -> 'Field':
        return self.fields[field_name]

    def process(
        self,
        source: Dict,
        context: Dict = None,
        strict=False,
        ignore_required=False,
        ignore_nullable=False,
        pre_process=None,
        post_process=None,
    ):
        """
        Marshal each value in the "source" dict into a new "dest" dict.
        """
        errors = {}
        context = context or {}

        if self.allow_additional:
            dest = deepcopy(source)
        else:
            dest = {}

        post_process_fields = []

        for field in self.fields.values():
            # is key simply present in source?
            exists_key = field.source in source

            # do we ultimately call field.process?
            skip_field = not exists_key

            # get source value, None is handled below
            source_val = source.get(field.source)

            if pre_process:
                # pre-process some shit
                source_val = pre_process(field, source_val, context=context)

            def generate_default(field):
                # generate default val from either
                # the supplied constant or callable.
                if callable(field.default):
                    source_val = field.default()
                else:
                    source_val = deepcopy(field.default)
                return source_val

            if not exists_key:
                # source key not present but required
                # try to generate default value if possible
                # or error.
                if field.default is not None:
                    skip_field = False
                    source_val = generate_default(field)
                elif field.required and not ignore_required:
                    errors[field.name] = 'missing'
                    continue
                else:
                    continue

            if (source_val is None):
                if field.default is not None:
                    # field has a default specified, attempt to generate
                    # the default from it
                    skip_field = False
                    source_val = generate_default(field)
                if not field.nullable:
                    # field cannot be null
                    if source_val is not None:
                        # source val is now populated with a default, set it
                        dest[field.name] = source_val
                    elif not ignore_nullable:
                        # but None not allowed!
                        errors[field.name] = 'null'
                    continue
                else:
                    # when it is nullable then set to None
                    dest[field.name] = None
                    continue

            if skip_field:
                # the key isn't in source, but that's ok,
                # as this means that the field isn't required
                # and has no default value.
                continue

            # apply field to the source value
            dest_val, field_err = field.process(source_val)


            if not field_err:
                dest[field.name] = dest_val
            else:
                errors[field.name] = field_err

            if field.post_process is not None:
                post_process_fields.append(field)

        # call all post-process callbacks
        for field in post_process_fields:
            dest_val = dest.pop(field.name)
            field_val, field_err = field.post_process(
                dest_val, dest, context=context
            )
            # now recheck nullity of the post-processed field value
            if (
                (dest_val is None) and
                (not field.nullable and not ignore_nullable)
            ):
                errors[field.name] = 'null'
            elif not field_err:
                dest[field.name] = field_val
            else:
                errors[field.name] = field_err

        # "strict" means we raise an exception
        if errors and strict:
            raise ValidationError(self, errors)

        results = self.tuple_factory(dest, errors)
        return results

    @memoized_property
    def children(self):
        pass
