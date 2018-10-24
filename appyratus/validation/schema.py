import copy

import pytz
import dateutil.parser
import venusian

from typing import Text
from uuid import UUID, uuid4
from datetime import datetime, date
from abc import ABCMeta, abstractmethod

from Crypto import Random

from appyratus.exc import AppyratusError
from appyratus.time import to_timestamp

from . import fields
from .exc import ValidationError
from .fields import Field
from .results import SchemaResult
from .consts import (
    OP_LOAD,
    OP_DUMP,
)


class SchemaMeta(type):
    def __init__(cls, name, bases, dict_):
        type.__init__(cls, name, bases, dict_)

        cls.fields = {}
        cls.required_fields = {OP_DUMP: {}, OP_LOAD: {}}
        cls.load_from_fields = {}
        cls.transform_fields = {}
        cls.composite_fields = {}

        cls.pre_loaded_keys = set()
        cls.post_dumped_keys = set()

        # collect the schema Field class attributes into various data
        # structures used internally...
        for k in dir(cls):
            v = getattr(cls, k)
            if not isinstance(v, Field):
                continue

            v.name = k
            cls.fields[k] = v

            # collect names of fields resulting from dump
            if not v.load_only:
                cls.post_dumped_keys.add(v.dump_to or k)

            # collect names of fields expected by load
            cls.pre_loaded_keys.add(v.load_from or k)

            # collect fields that have load_from kwarg
            if v.load_from is not None:
                cls.load_from_fields[v.load_from] = v

            # collect required fields for load/dump
            if v.required:
                cls.required_fields[OP_DUMP][k] = v
                cls.required_fields[OP_LOAD][k] = v
            elif v.dump_required:
                cls.required_fields[OP_DUMP][k] = v
            elif v.load_required:
                cls.required_fields[OP_LOAD][k] = v

            # collect composite fields
            if hasattr(v, 'composite'):
                cls.composite_fields[k] = v

            # collect fields with transform
            if hasattr(v, 'transform'):
                cls.transform_fields[k] = v

        # pedantically make this set constant
        cls.post_dumped_keys = frozenset(cls.post_dumped_keys)
        cls.pre_loaded_keys = frozenset(cls.pre_loaded_keys)

        # collect the schema class in a global set
        # through a venusian callback:
        def callback(scanner, name, schema_class):
            scanner.schema_classes[name] = schema_class

        venusian.attach(cls, callback, category='schema')


class AbstractSchema(object):
    def __init__(
        self,
        strict=False,
        allow_additional=False,
    ):
        """
        # Kwargs:
            - strict: if True, then a ValidationException will be thrown if any
              errors are encountered during load (or dump).
            - allow_additional: if True, additional key-value pairs will be
              allowed to exist in the data loaded by this schema; however,
              these additional keys-value will not exist in the data returned
              by load or dump.
        """
        self.strict = strict
        self.allow_additional = allow_additional

    def __repr__(self):
        return '<Schema({})>'.format(self.__class__.__name__)

    def load(self, data, fields=None, strict=None):
        return self._apply_op(OP_LOAD, data, fields, strict)

    def dump(self, data, fields=None, strict=None):
        return self._apply_op(OP_DUMP, data, fields, strict)

    def _apply_op(self, op: str, data: dict, projection: set, strict: bool):
        """
        Apply operations to data, and be sure to make a copy of data before
        hand.
        """
        data = copy.deepcopy(data)
        strict = strict if strict is not None else self.strict
        result = SchemaResult(op, {}, {})

        # The `projection`
        if not projection:
            if op == OP_LOAD:
                projection = self.pre_loaded_keys
            else:
                projection = self.fields.keys()
        elif not isinstance(projection, set):
            projection = set(projection)

        if op == OP_LOAD:
            # assign default values before continuing with loading
            for k, field in self.fields.items():
                if data.get(k) is None and field.has_default_value:
                    data[k] = field.default_value

        for k, v in data.items():
            # ignore any field whose name not in projection
            if k not in projection and not self.allow_additional:
                continue

            field = self.fields.get(k)

            if field is None:
                field = self.load_from_fields.get(k)
                if field is None:
                    if not self.allow_additional:
                        result.errors[k] = 'unrecognized field'
                    else:
                        result.data[k] = v
                    continue

            if v is None:
                if not field.allow_none:
                    result.errors[k] = 'must not be null'
                    continue
                elif op == OP_DUMP:
                    if not field.load_only:
                        result.data[field.dump_to or k] = None
                else:
                    result.data[k] = v
            else:
                field_result = getattr(field, op)(v)
                if field_result.error:
                    result.errors[k] = field_result.error
                elif op == OP_DUMP:
                    if field.load_only:
                        continue
                    result.data[field.dump_key] = field_result.value
                else:
                    result.data[field.name] = field_result.value

        for k, field in self.required_fields[op].items():
            if k in result.errors:
                continue
            if op == OP_DUMP:
                k_to = field.dump_to or k
                if k_to not in result.data and (not field.load_only):
                    result.errors[k] = 'missing'
            elif op == OP_LOAD:
                k_from = field.load_from or k
                if k not in result.data:
                    result.errors[k_from] = 'missing'

        # transform fields are rendered upon load
        if op == OP_LOAD:
            for field in self.fields.values():
                if field.transform:
                    value = result.data.get(field.load_key)
                    result.data[field.load_key] = field.transform(value)
        # composite fields are rendered upon dump
        else:
            for k, field in self.composite_fields.items():
                value = data.get(field.load_key)
                result.data[field.load_key] = value.format(**result.data)

        if strict and result.errors:
            result.raise_validation_error()

        return result


class Schema(AbstractSchema, metaclass=SchemaMeta):
    @classmethod
    def load_keys(cls, keys: list) -> list:
        """
        The `keys` list is expected to be a subset of the field names defined
        by the schema prior to the load operation being performed. The return
        value will be a list containing the result of "loading" just the field
        names, taking into account any field's load_from kwarg.
        """
        loaded_keys = []
        for key in keys:
            if key in cls.load_from_fields:
                loaded_key = cls.load_from_fields[key].name
            else:
                loaded_key = key
            loaded_keys.append(loaded_key)
        return loaded_keys

    def get_nested_schemas(self, max_depth=None):
        def accumulate(schema, acc, depth, max_depth):
            acc.add(schema)
            if (max_depth is not None) and depth == max_depth:
                return set()
            for field in schema.fields.values():
                if isinstance(field, fields.Object):
                    accumulate(field.nested, acc, depth+1, max_depth)
            return acc

        schemas = accumulate(self, set(), 0, max_depth)
        schemas.discard(self)

        return schemas
