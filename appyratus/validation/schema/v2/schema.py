import venusian

from typing import Type
from copy import deepcopy

from .fields import Field
from .exc import ValidationError


class schema_type(type):
    def __init__(cls, name, bases, dict_):
        type.__init__(cls, name, bases, dict_)
        fields = {}  # aggregator for all fields declared on the class
        on_create_fields = []  # fields with on_create callbacks

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
                if v.on_create is not None:
                    # collect fields with on_create callbacks
                    on_create_fields.append(v)

        # set aggregated fields dict as attr on the new class
        cls.fields = fields

        # call any non-null on_create methods
        for field in on_create_fields:
            field.on_create(cls)


class Schema(Field, metaclass=schema_type):

    @classmethod
    def factory(cls, name: str, fields: dict) -> Type['Schema']:
        """
        Convenience method for building new Schema classes from a dict of Field
        objects, using the given name as the name of the class object.
        """
        return type(name, (cls, ), fields)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process(self, source: dict, strict=False):
        """
        Marshal each value in the "source" dict into a new "dest" dict.
        """
        dest = {}
        errors = {}

        post_process_fields = []

        for field in self.fields.values():
            # is key simply present in source?
            exists_key = field.source in source

            # do we ultimately call field.process?
            skip_field = not exists_key

            # get source value, None is handled below
            source_val = source.get(field.source)

            if not exists_key:
                # source key not present but required
                # try to generate default value if possible
                # or error.
                if field.default is not None:
                    # generate default val from either
                    # the supplied constant or callable.
                    skip_field = False
                    if callable(field.default):
                        source_val = field.default()
                    else:
                        source_val = deepcopy(field.default)
                elif field.required:
                    errors[field.name] = 'missing'
                    continue

            if (source_val is None) and (not field.nullable):
                # source value is None, but None not allowed.
                errors[field.name] = 'null'
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
            field_val, field_err = field.post_process(dest_val, dest)
            # now recheck nullity of the post-processed field value
            if (dest_val is None) and (not field.nullable):
                errors[field.name] = 'null'
            elif not field_err:
                dest[field.name] = field_val
            else:
                errors[field.name] = field_err

        # "strict" means we raise an exception
        if errors and strict:
            raise ValidationError(self, errors)

        return (dest, errors)
