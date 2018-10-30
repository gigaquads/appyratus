import copy
import time

import pytz
import dateutil.parser
import venusian

from typing import Text, Type
from uuid import UUID, uuid4
from datetime import datetime, date
from abc import ABCMeta, abstractmethod

from Crypto import Random

from appyratus.exc import AppyratusError
from appyratus.time import to_timestamp, from_timestamp


## Fields.py
import re

from uuid import UUID, uuid4
from datetime import datetime, date


class Field(object):
    def __init__(
        self,
        name=None,
        load_from=None,
        required=False,
        allow_none=True,
        default=None,
        callback=None,
    ):
        self.name = name
        self.load_from = load_from
        self.required = required
        self.allow_none = allow_none
        self.default = default
        self.callback = callback

    def __repr__(self):
        if self.load_from != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{})'.format(
            self.__class__.__name__,
            self.load_from,
            load_to
        )

    def process(self, value):
        return (value, None)

    def callback(self, value, data):
        """
        This method is *intentionally* shadowed by the ctor keyword argument
        with the same name. This stub is just for declaring the expected
        interface.
        """
        return (value, None)


class String(Field):
    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        else:
            return (None, 'unrecognized')


class String(Field):
    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        else:
            return (None, 'unrecognized')


class Int(Field):
    def __init__(self, signed=False, **kwargs):
        super().__init__(**kwargs)
        self.signed = signed

    def process(self, value):
        if isinstance(value, str):
            if not value.isdigit():
                return (None, 'invalid')
            else:
                value = int(value)
        if isinstance(value, int):
            if self.signed and value < 0:
                return (None, 'invalid')
            else:
                return (value, None)
        else:
            return (None, 'unrecognized')


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


class String(Field):
    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        else:
            return (None, 'unrecognized')


class Float(Field):
    re_float = re.compile(r'^\d*(\.\d*)?$')

    def process(self, value):
        if isinstance(value, float):
            return (value, None)
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
                return (None, 'invalid')
            else:
                return (UUID(value), None)
        elif isinstance(value, int):
            hex_str = hex(value)[2:]
            uuid_hex = ('0' * (32 - len(hex_str))) + hex_str
            return (UUID(uuid_hex), None)
        else:
            return (None, 'unrecognized')


class UuidString(Field):
    re_uuid = re.compile(r'^[a-f0-9]{32}$')

    def process(self, value):
        if isinstance(value, UUID):
            return (value.hex, None)
        elif isinstance(value, str):
            value = value.replace('-', '').lower()
            if self.re_uuid.match(value):
                return (value, None)
            else:
                return (None, 'invalid')
        elif isinstance(value, int):
            hex_str = hex(value)[2:]
            uuid_hex = ('0' * (32 - len(hex_str))) + hex_str
            return (uuid_hex, None)
        else:
            return (None, 'unrecognized')


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
            return (None, 'unrecognized')


class DateTime(Field):
    def process(self, value):
        if isinstance(value, datetime):
            return (value.replace(tzinfo=pytz.utc), None)
        elif isinstance(value, (int, float)):
            try:
                return (from_timestamp(value), None)
            except ValueError:
                return (None, 'invalid')
        elif isinstance(value, date):
            return (datetime.combine(value, datetime.min.time()), None)
        elif isinstance(value, str):
            try:
                return (dateutil.parser.parse(value), None)
            except:
                return (None, 'invalid')
        else:
            return (None, 'unrecognized')


class DateTimeString(Field):
    def __init__(self, format_spec=None, **kwargs):
        super().__init__(**kwargs)
        self.format_spec = format_spec

    def process(self, value):
        if isinstance(value, str):
            try:
                dt = dateutil.parser.parse(value)
            except:
                return (None, 'invalid')
        elif isinstance(value, (int, float)):
            dt = from_timestamp(value)
        elif isinstance(value, datetime):
            dt = value.replace(tzinfo=pytz.utc)
        elif isinstance(value, date):
            dt = datetime.combine(value, datetime.min.time())
        else:
            return (None, 'unrecognized')

        if self.format_spec:
            dt_str = datetime.strftime(dt, self.format_spec)
        else:
            dt_str = dt.isoformat()

        return (dt_str, None)


class Timestamp(Field):
    def process(self, value):
        if isinstance(value, (int, float)):
            return (value, None)
        elif isinstance(value, datetime):
            return (to_timestamp(value), None)
        elif isinstance(value, date):
            return (time.mktime(value.timetuple()), None)
        else:
            return (None, 'unrecognized')


class List(Field):
    def __init__(self, nested: Field, **kwargs):
        super().__init__(**kwargs)
        self.nested = nested

    def __repr__(self):
        if self.load_from != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{}, {})'.format(
            self.__class__.__name__,
            self.load_from,
            load_to,
            self.nested.__class__.__name__,
        )

    def process(self, sequence):
        dest_sequence = []
        idx2error = {}
        if isinstance(sequence, set):
            sequence = sorted(sequence)
        for idx, value in enumerate(sequence):
            dest_val, err = self.nested.process(value)
            if not err:
                dest_sequence.append(dest_val)
            else:
                idx2error[idx] = err

        if not idx2error:
            return (dest_sequence, None)
        else:
            return (None, idx2error)


class Nested(Field):
    def __init__(self, fields: dict, **kwargs):
        super().__init__(**kwargs)
        self.fields = fields
        self.schema = None  # is set by owning Schema

    def __repr__(self):
        if self.load_from != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{})'.format(
            self.schema.__class__.__name__, self.load_from, load_to
        )

    def process(self, value):
        return self.schema.process(value)


class Dict(Field):
    def process(self, value):
        if isinstance(value, dict):
            return (value, None)
        else:
            return (None, 'unrecognized')


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
                if isinstance(v, Nested):
                    name = k.replace('_', ' ').title().replace(' ', '')
                    v.schema = cls.factory(name + 'Schema', v.fields)()
        cls.fields = fields


class Schema(Field, metaclass=schema_type):

    @classmethod
    def factory(cls, type_name, fields: dict) -> Type['Schema']:
        return type(type_name, (cls, ), fields)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process(self, source: dict, strict=False):
        """
        Marshal each value in the "source" dict into a new "dest" dict.
        """
        dest = {}
        errors = {}

        callback_fields = []

        for field in self.fields.values():
            # is key simply present in source?
            exists_key = field.load_from in source

            # do we ultimately call field.process?
            skip_field = not exists_key

            # get source value, None is handled below
            source_val = source.get(field.load_from)

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

            if (source_val is None) and (not field.allow_none):
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

            if field.callback is not None:
                callback_fields.append(field)

        for field in callback_fields:
            dest_val = dest.pop(field.name)
            field_val, field_err = field.callback(dest_val, dest)
            if (dest_val is None) and (not field.allow_none):
                errors[field.name] = 'null'
            elif not field_err:
                dest[field.name] = field_val
            else:
                errors[field.name] = field_err

        # "strict" means we raise an exception
        if errors and strict:
            raise ValidationError(self, errors)

        return (dest, errors)


class ValidationError(Exception):
    def __init__(self, schema, errors):
        super().__init__()
        self.schema = schema
        self.errors = errors


if __name__ == '__main__':
    from pprint import pprint

    class AccountSchema(Schema):
        name = String()

    class UserSchema(Schema):
        age = Int(load_from='age_int')
        gender = String()
        composite = String(
            default='{age}:{personality}',
            callback=lambda fstr, data: (fstr.format(**data), None)
        )
        name = String(required=True)
        personality = String(required=True, default=lambda: 'INTP')
        t = Timestamp()
        account = AccountSchema()
        accounts = List(AccountSchema())
        numbers = List(Int())
        more_numbers = List(Int())
        my_things = Nested({
            'a': String(),
            'b': Int(),
        })

    schema = UserSchema()

    data, errors = schema.process({
        'age_int': 1,
        'gender': 'M',
        't': '124',
        'account': {'name': 'foo'},
        'accounts': [{'name': 'foo'}],
        'numbers': [1, 2, 'a'],
        'more_numbers': {1, 2},
        'my_things': {'a': 'a', 'b': 1},
    })

    pprint(schema.fields)
    pprint(data)
    pprint(errors)
