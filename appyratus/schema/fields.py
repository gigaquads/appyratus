import time
import typing
import re

import pytz
import dateutil.parser

from datetime import datetime, date
from os.path import abspath, expanduser
from typing import Type
from uuid import UUID, uuid4

from appyratus.utils import TimeUtils


class Field(object):
    def __init__(
        self,
        source: typing.Text=None,
        name: typing.Text=None,
        required: bool=False,
        nullable: bool=True,
        default: object=None,
        meta: typing.Dict=None,
        on_create: object=None,
        post_process: object=None,
        **kwargs,
    ):
        """
        # Kwargs
        - `source`: key in source data if different from declared field name.
        - `name`: name of the field as declared on the host Schema class.
        - `required`: key must exist in source data if set.
        - `nullable`: if key exists, it can be None/null if this is set.
        - `default`: a constant or callable the returns a default value.
        - `on_create`: generic method to run upon init of host schema class.
        - `post_process`: generic method to run after fields are processed.
        - `meta`: additional data storage
        """
        self.name = name
        self.source = source or name
        self.required = required
        self.nullable = nullable
        self.default = default
        self.on_create = on_create
        self.post_process = post_process
        self.meta = meta or {}
        self.meta.update(kwargs)

    def __repr__(self):
        if self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{})'.format(
            self.__class__.__name__,
            self.source,
            load_to
        )

    def process(self, value):
        return (value, None)

    def pre_process(self, value, source: dict, context: dict = None):
        """
        This method is *intentionally* shadowed by the ctor keyword argument
        with the same name. This stub is just for declaring the expected
        interface.
        """
        return (value, None)

    def post_process(self, dest: dict, value, context=None):
        """
        This method is *intentionally* shadowed by the ctor keyword argument
        with the same name. This stub is just for declaring the expected
        interface.
        """
        return (value, None)


class Enum(Field):
    def __init__(self, nested: Field, values, **kwargs):
        self.nested = nested
        self.values = set(values)
        super().__init__(**kwargs)

    def process(self, value):
        nested_value, error = self.nested.process(value)
        if error:
            return (None, error)
        elif nested_value not in self.values:
            return (None, 'unrecognized')
        else:
            return (nested_value, None)


class String(Field):
    def process(self, value):
        if isinstance(value, str):
            return (value, None)
        else:
            return (None, 'unrecognized')


class FormatString(String):
    def __init__(self, **kwargs):
        super().__init__(
            post_process=self.do_format,
            **kwargs
        )

    def do_format(self, fstr, data, context=None):
        value = fstr.format(**data)
        return (value, None)


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
        if error:
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


class UuidString(String):
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
        elif value in self.truthy:
            return (True, None)
        elif value in self.falsey:
            return (False, None)
        else:
            return (None, 'unrecognized')


class DateTime(Field):
    def process(self, value):
        if isinstance(value, datetime):
            return (value.replace(tzinfo=pytz.utc), None)
        elif isinstance(value, (int, float)):
            try:
                return (TimeUtils.from_timestamp(value), None)
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


class DateTimeString(String):
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
            dt = TimeUtils.from_timestamp(value)
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
            return (TimeUtils.to_timestamp(value), None)
        elif isinstance(value, date):
            return (time.mktime(value.timetuple()), None)
        else:
            return (None, 'unrecognized')


class List(Field):
    def __init__(self, nested: Field = None, **kwargs):
        super().__init__(**kwargs)
        self.nested = nested or Field()

    def __repr__(self):
        if self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{}, {})'.format(
            self.__class__.__name__,
            self.source,
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
    """
    # Example:
    ```python
        my_fields = Nested({
            'field_1': Str(),
            'field_2': Int(),
        })
    ```
    """

    def __init__(self, fields: dict, **kwargs):
        def on_create(schema_type: Type['Schema']):
            name = self.name.replace('_', ' ').title().replace(' ', '')
            self.schema_type = schema_type.factory(name + 'Schema', fields)
            self.schema = self.schema_type()

        super().__init__(on_create=on_create, **kwargs)
        self.schema = None

    def __repr__(self):
        if self.source != self.name:
            load_to = ' -> ' + self.name
        else:
            load_to = ''
        return '{}({}{})'.format(
            self.schema.__class__.__name__, self.source, load_to
        )

    def process(self, value):
        return self.schema.process(value)


class Dict(Field):
    def process(self, value):
        if isinstance(value, dict):
            return (value, None)
        else:
            return (None, 'unrecognized')


class FilePath(String):
    """
    # FilePath
    Coerce a filepath into it's absolutized form.  This includes expanding the
    userpath if specified.
    """

    def process(self, value):
        if isinstance(value, str):
            value = abspath(expanduser(value))
            return (value, None)
        else:
            return (None, 'unrecognized')


class Set(Field):
    """
    """
    dict_keys_type = type({}.keys())
    dict_vals_type = type({}.values())

    def process(self, value):
        if isinstance(value, (list, tuple, set, dict_keys_type, dict_values)):
            return (set(value), None)
        else:
            return (None, 'unrecognized')
