from appyratus.utils.dict_utils import DictObject
from uuid import UUID
from inspect import getmembers
from datetime import datetime, date
from collections import namedtuple, defaultdict
from copy import deepcopy
from typing import (
    Callable,
    Dict,
    List,
    Set,
    Text,
    Type,
    Union,
)

from faker import Faker

from appyratus.utils.string_utils import StringUtils
from appyratus.utils.dict_utils import DictObject

from . import fields
from .exc import ValidationError
from .fields import Field, List, Nested


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

        # inherit any fields provided by bases of schema type before applying
        # fields defined from this class
        cls.fields = {}
        cls.inherit_fields(bases)
        cls.fields.update(fields)

        # save aggregated fields dict and child
        # schema list set on the new class
        cls.children = []
        cls.nullable_fields = {}
        cls.required_fields = {}
        cls.optional_fields = {}
        cls.source_2_field = {}
        cls.scalar_fields = {}

        for k, field in cls.fields.items():
            cls.source_2_field[field.source] = field
            # track required and optional fields
            if field.nullable:
                cls.nullable_fields[k] = field
            if field.scalar:
                cls.scalar_fields[k] = field
            if field.required:
                cls.required_fields[k] = field
            else:
                cls.optional_fields[k] = field
            # call any non-null on_create methods
            if field.on_create is not None:
                field.on_create()
            # accumulate any schema declared in the field
            child = get_schema_from_field(field)
            if child is not None:
                cls.children.append(child)

    def inherit_fields(cls, bases: List):
        """
        # Inherit Fields
        Inherit fields from a base class
        """
        for base in bases:
            if getattr(base, '_is_schema_class', False):
                cls.fields.update(deepcopy(base.fields))


class Schema(Field, metaclass=schema_type):

    fields = {}
    children = None
    _is_schema_class = True

    @classmethod
    def factory(cls, name: str, fields: dict) -> Type['Schema']:
        """
        Convenience method for building new Schema classes from a dict of Field
        objects, using the given name as the name of the class object.
        """
        return type(name, (cls, ), fields)

    def __init__(self, allow_additional=False, **kwargs):
        super().__init__(**kwargs)
        self.tuple_factory = namedtuple('results', field_names=['data', 'errors'])
        self.allow_additional = allow_additional

    def copy(self):
        schema_copy = super().copy()
        schema_copy.allow_additional = self.allow_additional
        return schema_copy

    def process(
        self,
        source: Dict,
        context: Dict = None,
        strict=False,
        ignore_required=False,
        ignore_nullable=False,
        before=None,
        after=None,
    ):
        """
        Marshal each value in the "source" dict into a new "dest" dict.
        """
        errors = {}

        context = DictObject(context or {})
        context.schema = self
        context.source = source

        if self.allow_additional:
            dest = source.copy()
        else:
            dest = {}

        after_fields = []

        def generate_default(field):
            # generate default val from either
            # the supplied constant or callable.
            if callable(field.default):
                source_val = field.default()
            else:
                source_val = deepcopy(field.default)
            return source_val

        self.before(source, context)

        for field in self.fields.values():
            # is key simply present in source?
            field_key = field.source or field.name
            exists_key = source is not None and field_key in source

            # do we ultimately call field.process?
            skip_field = not exists_key

            # get source value, None is handled below
            source_val = source.get(field.source) if isinstance(source, dict) else None

            # pre-process some fields, first by the schema if provided, then by
            # the field itself if provided
            if field.before:
                source_val, source_err = field.before(
                    field, source_val, context=context
                )
                if source_err:
                    errors[field.name] = source_err

            if not exists_key:
                # source key not present but required
                # try to generate default value if possible
                # or error.
                if field.default is not None:
                    skip_field = False
                    source_val = generate_default(field)
                elif field.required and not ignore_required:
                    errors[field.name] = f'{field.name} is required'
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
                        errors[field.name] = f'{field.name} not nullable'
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

            if field.after is not None:
                after_fields.append(field)

        # call all post-process callbacks
        for field in after_fields:
            dest_val = dest.pop(field.name, None)
            field_val, field_err = field.after(
                field, dest_val, dest, context=context
            )
            # now recheck nullity of the post-processed field value
            if (
                (dest_val is None) and
                (not field.nullable and not ignore_nullable)
            ):
                errors[field.name] = f'{field.name} not nullable'
            elif not field_err:
                dest[field.name] = field_val
            else:
                errors[field.name] = field_err

        # "strict" means we raise an exception
        # or return just the processed dict
        if strict:
            if errors:
                raise ValidationError(self, errors)
            else:
                return dest

        self.after(dest, context)
        results = self.tuple_factory(dest, errors)
        return results

    def before(self, source: Dict, context):
        pass

    def after(self, data: Dict, context):
        pass

    def translate_source(self, data: Dict) -> Dict:
        """
        Translate any keys of the input data dict into their field names as keys
        in the return dict. Otherwise, just add the existing k, v pair to the
        return dict as they are.
        """
        results = {}
        for k, v in data.items():
            field = self.fields.get(k)
            if field:
                results[k] = v
            else:
                field = self.source_2_field.get(k)
                if field:
                    results[field.name] = v
        return results

    @classmethod
    def replace_field(cls, new_field: Field, overwrite=True):
        name = new_field.name
        cls.fields[name] = new_field
        old_field = cls.fields.get(name)

        if old_field is not None:
            if not overwrite:
                raise ValueError(
                    f'field {name} already exists. use overwrite=True if you '
                    f'intend to replace the existing field.'
                )
            del cls.source_2_field[name]
            if old_field.name in cls.nullable_fields:
                del cls.nullable_fields[name]
            if old_field.name in cls.scalar_fields:
                del cls.scalar_fields[name]
            if old_field.name in cls.required_fields:
                del cls.required_fields[name]
            elif old_field.name in cls.optional_fields:
                del cls.optional_fields[name]
            if isinstance(old_field, Schema):
                cls.children.remove(old_field)

        cls.source_2_field[new_field.source] = new_field
        if isinstance(new_field, Schema):
            cls.children.add(new_field)
        if new_field.nullable:
            cls.nullable_fields[name] = new_field
        if new_field.scalar:
            cls.scalar_fields[name] = new_field
        if new_field.required:
            cls.required_fields[name] = new_field
        else:
            cls.optional_fields[name] = new_field

    def on_generate(self, fields: Set[Text] = None, **kwargs) -> Dict:
        return {
            k: self.fields[k].generate()
            for k in (fields or self.fields)
        }

    @classmethod
    def infer(
        cls,
        target: Dict,
        name: Text = None,
        predicate: Callable = None,
        depth: int = 0,
    ) -> Type['Schema']:
        """
        Return a new Schema class that mirrors the structure of the input target
        object, as best as possible.
        """
        acc = {}
        depth -= 1

        if not name:
            faker = Faker()
            name = f'{faker.color_name()}Schema'

        if predicate is None:
            predicate = lambda k, v: not k.startswith('_')

        py_type_2_field_type = {
            str: fields.String,
            int: fields.Int,
            float: fields.Float,
            bool: fields.Bool,
            bytes: fields.Bytes,
            UUID: fields.Uuid,
            datetime: fields.DateTime,
            date: fields.DateTime,
        }

        def build_nested_field(seq):
            contained_py_types = {type(x) for x in seq}
            if len(contained_py_types) == 1:
                sub_target = list(seq)[0]
                py_type = list(contained_py_types)[0]
                if py_type in py_type_2_field_type:
                    field_type = py_type_2_field_type[py_type]
                    return field_type(example=sub_target)
                elif py_type in (list, tuple, set):
                    nested = build_nested_field(sub_target)
                    return fields.List(nested)
                elif py_type is dict:
                    return cls.infer(
                        target=sub_target,
                        predicate=predicate,
                        depth=(depth - 1)
                    )()
            return fields.Field()


        for k, v in  target.items():
            if not predicate(k, v):
                continue

            if isinstance(v, dict):
                if depth != 0:
                    sub_schema_type = cls.infer(
                        target=v,
                        name=StringUtils.camel(f'{k}Schema'),
                        predicate=predicate,
                        depth=(depth - 1)
                    )
                    acc[k] = fields.Nested(
                        sub_schema_type, name=k, source=k, example=v
                    )
                else:
                    acc[k] = fields.Dict(name=k, source=k, example=v)

            else:
                scalar_field_type = py_type_2_field_type.get(type(v))
                if scalar_field_type:
                    if scalar_field_type is fields.String:
                        # TODO resolve String to more specific field type if possible
                        acc[k] = scalar_field_type(
                            name=k, source=k, example=v
                        )
                    else:
                        acc[k] = scalar_field_type(
                            name=k, source=k, example=v
                        )
                elif isinstance(v, (list, set, tuple)):
                    nested = build_nested_field(v)
                    nested.name = k
                    nested.source = k
                    if isinstance(nested, Schema):
                        type(nested).__name__ = StringUtils.camel(
                            f'{StringUtils.singular(k)}Schema', lower=False
                        )
                    acc[k] = fields.List(
                        nested=nested, name=k, source=k, example=v
                    )
                else:
                    acc[k] = fields.Field(
                        name=k, source=k, example=v
                    )

        return type(name, (cls, ), acc)
