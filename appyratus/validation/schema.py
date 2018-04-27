import copy

import pytz
import dateutil.parser
import venusian

from uuid import UUID, uuid4
from datetime import datetime, date
from abc import ABCMeta, abstractmethod

from Crypto import Random

from appyratus.exc import AppyratusError
from appyratus.time import to_timestamp

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
        for k in dir(cls):
            v = getattr(cls, k)
            if isinstance(v, Field):
                v.name = k
                if v.load_from is not None:
                    cls.load_from_fields[v.load_from] = v
                cls.fields[k] = v
                if v.required:
                    cls.required_fields[OP_DUMP][k] = v
                    cls.required_fields[OP_LOAD][k] = v
                elif v.dump_required:
                    cls.required_fields[OP_DUMP][k] = v
                elif v.load_required:
                    cls.required_fields[OP_LOAD][k] = v

        # collect the schema class in a global set
        # through a venusian callback:
        def callback(scanner, name, schema_class):
            scanner.schema_classes[name] = schema_class

        venusian.attach(cls, callback, category='schema')


class AbstractSchema(object):
    def __init__(self, strict=False, allow_additional=True):
        """
        Kwargs:
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

    def load(self, data, strict=None):
        return self._apply_op(OP_LOAD, data, strict)

    def dump(self, data, strict=None):
        return self._apply_op(OP_DUMP, data, strict)

    def _apply_op(self, op, data, strict):
        """
        Apply operations to data
        And be sure to make a copy of data before hand
        """
        data = copy.deepcopy(data)
        strict = strict if strict is not None else self.strict
        result = SchemaResult(op, {}, {})

        if op == OP_LOAD:
            for k, field in self.fields.items():
                if data.get(k) is None and field.has_default_value:
                    data[k] = field.default_value

        for k, v in data.items():
            field = self.fields.get(k)

            if field is None:
                field = self.load_from_fields.get(k)
                if field is None:
                    if not self.allow_additional:
                        result.errors[k] = 'unrecognized field'
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

        # post-dump operations only
        if op == OP_DUMP:
            # transform fields allow data to be mutated into specified shapes
            transform_fields = [
                field for k, field in self.fields.items()
                if getattr(field, 'dump_transform')
            ]
            for field in transform_fields:
                value = result.data.get(field.name)
                value = field.dump_transform(value)
                result.data[field.load_key] = value

            # process composite fields only upon dump, and after everything has
            # been prepared
            composite_fields = [
                field for k, field in self.fields.items()
                if hasattr(field, 'composite')
            ]
            for field in composite_fields:
                value = result.data.get(field.name)
                result.data[field.load_key] = value.format(**result.data)

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

        if strict and result.errors:
            result.raise_validation_error()

        return result


class Schema(AbstractSchema, metaclass=SchemaMeta):
    @classmethod
    def load_keys(cls, keys) -> list:
        loaded_keys = []
        for key in keys:
            if key in cls.load_from_fields:
                loaded_key = cls.load_from_fields(key).name
            else:
                loaded_key = key
            loaded_keys.append(loaded_key)
        return loaded_keys
