import copy

import pytz
import dateutil.parser
import venusian

from typing import Text, Dict
from uuid import UUID, uuid4
from datetime import datetime, date
from abc import ABCMeta, abstractmethod

from Crypto import Random

from appyratus.exc import AppyratusError
from appyratus.time import to_timestamp


## Fields.py
import re

from uuid import UUID, uuid4


class Field(object):
    def __init__(
        self,
        name=None,
        load_from=None,
        required=False,
        allow_none=True,
        default=None,
        transform=None,
    ):
        self.name = name
        self.load_from = load_from
        self.required = required
        self.allow_none = allow_none
        self.default = default
        self.transform = transform

    def process(self, value):
        return (value, None)


class Object(Field):
    def __init__(self, nested, *args, **kwargs):
        """
        # Args:
            - nested: either a Schema instance or a dict, containing field
              names mapped to field objects.
        """
        super().__init__(*args, **kwargs)

        if isinstance(nested, dict):
            # create a new schema class and instatiate it
            from appyratus.validation.schema.v2.schema import Schema
            schema_class = type('Anonymouschema', (Schema, ), nested)
            self.nested = schema_class()
        else:
            self.nested = nested

    def process(self, value):
        return self.nested.process(value)


class Str(Field):
    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        else:
            return (None, 'not a string')


class Int(Field):
    def __init__(self, signed=False, **kwargs):
        super().__init__(**kwargs)
        self.signed = signed

    def process(self, value):
        if isinstance(value, str):
            if not value.isdigit():
                return (None, 'expected a digit string')
            else:
                value = int(value)
        if isinstance(value, int):
            if self.signed and value < 0:
                return (None, 'expected signed int')
            else:
                return (value, None)
        else:
            return (None, 'not an int')


class Uint32(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)


class Uint64(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=False, **kwargs)


class Sint32(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)


class Sint64(Int):
    def __init__(self, **kwargs):
        super().__init__(signed=True, **kwargs)


class Str(Field):
    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        else:
            return (None, 'not a string')


class Float(Field):
    re_float = re.compile(r'^\d*(\.\d*)?$')

    def process(self, value):
        if isinstance(value, float):
            return return (value, None)
        elif isinstance(value, int):
            return (float(value), None)
        elif isinstance(value, str):
            if not self.re_float.match(value):
                return (None, 'expected a float')
            else:
                return (float(value), None)
        else:
            return (None, 'expected a float')


class Email(String):
    re_email = re.compile(r'^[a-f]\w*(\.\w+)?@\w+\.\w+$', re.I)

    def process(self, value):
        dest, error = super().process(value)
        if not error:
            return (dest, error)
        elif not self.re_email.match(value):
            return (None, 'not a valid e-mail address')
        else:
            return (value.lower(), None)


class Uuid(Field):
    re_uuid = re.compile(r'^[a-f0-9]{32}$')

    def process(self, value):
        if isinstance(value, UUID):
            return (value, None)
        elif isinstance(value, str):
            value = value.replace('-', '').lower()
            if not self.re_uuid.match(value):
                return (None, 'invalid UUID')
            else:
                return (UUID(value), None)
        elif isinstance(value, int):
            hex_str = hex(value)[2:]
            uuid_hex = '0' * (32 - len(hex_str))) + hex_str)
            return (UUID(uuid_hex), None)
        else:
            return (None, 'expected a UUID')


class Bool(Field):
    truthy = {'T', 't', 'True', 'true', 1}
    falsey = {'F', 'f', 'False', 'false', 0}

    def process(self, value):
        if isinstance(value, bool):
            return (value, None)
        elif value in self.TRUTHY:
            return (True, None)
        elif value in self.FALSEY:
            return (False, None)
        else:
            return (None, 'expected bool')


class DateTime(Field):
    def __init__(self, format_spec: str = None, **kwargs):
        super().__init__(**kwargs)
        self.format_spec = format_spec

    def process(self, value):
        raise NotImplementedError()

## schema.py
from copy import deepcopy

class schema_type(type):
    def __init__(cls, name, bases, dict_):
        type.__init__(cls, name, bases, dict_)
        fields = {}
        for k, v in dict_.items():
            if isinstance(v, Field):
                delattr(cls, k)
                fields[k] = v
                if v.name is None:
                    v.name = k
                if v.load_from is None:
                    v.load_from = v.name
        cls.fields = fields


class Schema(metaclass=schema_type):
    def process(self, source: Dict, strict=False):
        dest = {}
        errors = {}
        for field in self.fields.values():
            source_val = source.get(field.load_from)
            if field.required and field.load_from not in source:
                if field.default is not None:
                    if callable(field.default):
                        source_val = field.default()
                    else:
                        source_val = deepcopy(field.default)
                else:
                    errors[field.name] = 'required'
                    continue
            if (source_val is None) and (not field.allow_none):
                if field.default is not None:
                    if callable(field.default):
                        source_val = field.default()
                    else:
                        source_val = deepcopy(field.default)
                if source_val is None:
                    errors[field.name] = 'must not be null'
                    continue

            dest_val, field_err = field.process(source_val)

            if field_err is None:
                if field.transform:
                    dest_val = field.transform(self, field, dest_val)
                    if (dest_val is None) and (not field.allow_none):
                        errors[field.name] = 'must not be null'
                        continue
                dest[field.name] = dest_val
            else:
                errors[field.name] = field_err

        if errors and strict:
            raise ValidationError(self, errors)

        return (dest, errors)


class ValidationError(Exception):
    def __init__(self, schema, errors):
        super().__init__()
        self.schema = schema
        self.errors = errors


if __name__ == '__main__':

    class User(Schema):
        age = Int(load_from='age_int')
        gender = Str()
        name = Str(required=True)
        personality = Str(required=True, default=lambda: 'INTP')

    user = User()

    print(user.fields)
    print(user.process({'age_int': 1, 'gender': 'M'}))
