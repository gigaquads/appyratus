from .consts import RECOGNIZED_OPS
from .exc import ValidationError


class SchemaResult(object):


    def __init__(self, op, data: dict, errors: dict):
        assert op in RECOGNIZED_OPS
        self.op = op
        self.data = data or {}
        self.errors = errors or {}

    def __repr__(self):
        return '<SchemaResult("{}", has_errors={})>'.format(
            self.op, True if self.errors else False)

    def raise_validation_error(self):
        raise ValidationError(reasons=self.errors)


class FieldResult(object):
    def __init__(self, value=None, error: str=None):
        self.value = value
        self.error = error

    def __repr__(self):
        return '<FieldResult(has_error={})>'.format(
            True if self.error else False
        )
