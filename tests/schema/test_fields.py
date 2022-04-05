from uuid import UUID
from pytest import mark

from appyratus.test import mark, BaseTests
from appyratus.schema import Schema
from appyratus.schema.fields import fields
from appyratus.utils.time_utils import TimeUtils

# TODO
# Bytes
# FormatString
# Uint32
# Uint64
# Sint32
# Sint64
# Email
# DateTimeString
# Timestamp
# Set
# Dict
# FilePath
# IpAddress
# DomainName
# Url


@mark.unit
class TestEnumField(BaseTests):

    @property
    def klass(self):
        return fields.Enum

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # Value exists in enum
            ('klingon', {
                'nested': fields.String(),
                'values': {'klingon'}
            }, 'klingon', None),
    # None value is an unrecognized value
            (None, {
                'nested': fields.String(),
                'values': {None}
            }, None, fields.UNRECOGNIZED_VALUE),
    # Value is invalid when enum is not nullable
            (None, {
                'nested': fields.String(),
                'nullable': False,
                'values': {None}
            }, None, fields.UNRECOGNIZED_VALUE),
    # Enum respects nested field type and will error on invalid values
            ([], {
                'nested': fields.String(),
                'values': {None}
            }, None, fields.UNRECOGNIZED_VALUE),
    # Value is invalid does not exist in enum
            ('ferengi', {
                'nested': fields.String(),
                'values': {'klingon'}
            }, None, fields.UNRECOGNIZED_VALUE)
        ]
    )
    def test_process(self, value, kwargs, result, error):
        res, err = self.klass(**kwargs).process(value)
        assert res == result
        assert err == error


@mark.unit
class TestStringField(BaseTests):

    @property
    def klass(self):
        return fields.String

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # Valid strings
    ## 'klingon' is a valid string
            ('klingon', {}, 'klingon', None),
    ## empty string is a valid string
            ('', {}, '', None),
    ## 1337 integer will be cast as a string
            (1337, {}, '1337', None),
            ([], {}, '[]', None),
            (set(), {}, 'set()', None),
            ({}, {}, '{}', None),
    # Unrecognized
    ## None is an unrecognized string
            (None, {}, None, fields.UNRECOGNIZED_VALUE),
        ]
    )
    def test_process(self, value, kwargs, result, error):
        res, err = self.klass(**kwargs).process(value)
        assert res == result
        assert err == error


@mark.unit
class TestIntField(BaseTests):

    @property
    def klass(self):
        return fields.Int

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # 0 is an valid unsigned integer
            (0, {}, 0, None),
    # -1 is a valid unsigned integer
            (-1, {}, -1, None),
    # 1 as a string is a valid unsigned integer
            ('1', {}, 1, None),
    # 0 is a valid signed integer
            (0, {
                'signed': True
            }, 0, None),
    # 1 is a valid signed integer
            (1, {
                'signed': True
            }, 1, None),
    # -1 is an invalid signed integer
            (-1, {
                'signed': True
            }, None, fields.INVALID_VALUE),
    # klingon is an invalid integer
            ('klingon', {}, None, fields.INVALID_VALUE),
    # None is an unrecognized integer
            (None, {}, None, fields.UNRECOGNIZED_VALUE),
        ]
    )
    def test_process(self, value, kwargs, result, error):
        res, err = self.klass(**kwargs).process(value)
        assert res == result
        assert err == error


@mark.unit
class TestFloatField(BaseTests):

    @property
    def klass(self):
        return fields.Float

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # Valid floats
            (0, {}, 0.0, None),
            (-1, {}, -1.0, None),
            (13.37, {}, 13.37, None),
            ('1', {}, 1.0, None),
            ('-13.37', {}, -13.37, None),
    # Invalid floats
            ('klingon', {}, None, fields.INVALID_VALUE),
            ('kling.on', {}, None, fields.INVALID_VALUE),
    # Unrecognized floats
            (None, {}, None, fields.UNRECOGNIZED_VALUE),
            ([], {}, None, fields.UNRECOGNIZED_VALUE),
            (set(), {}, None, fields.UNRECOGNIZED_VALUE),
            ({}, {}, None, fields.UNRECOGNIZED_VALUE),
        ]
    )
    def test_process(self, value, kwargs, result, error):
        res, err = self.klass(**kwargs).process(value)
        assert res == result
        assert err == error


@mark.unit
class TestUuidField(BaseTests):
    """
    """

    @property
    def klass(self):
        return fields.Uuid

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # Valid UUIDs
    ## A dash separated uuid string is valid
            ('deadbeef-dead-beef-dead-beef-deadbeef', {}, UUID('deadbeef-dead-beef-dead-beef-deadbeef'), None),
    ## A non-separated uuid string is valid
            ('deadbeefdeadbeefdeadbeefdeadbeef', {}, UUID('deadbeef-dead-beef-dead-beef-deadbeef'), None),
    ## A uuid string of numbers is valid
            ('12345678901234567890123456789012', {}, UUID('12345678901234567890123456789012'), None),
    ## A uuid object is valid
            (UUID('deadbeef-dead-beef-dead-beef-deadbeef'), {}, UUID('deadbeef-dead-beef-dead-beef-deadbeef'), None),
    ## An integer is a valid uuid
            (295990755083049101712519384020072382191, {}, UUID('deadbeef-dead-beef-dead-beef-deadbeef'), None),
    # Invalid UUIDs
    ## Characters outside the UUID range A-F are invalid
            ('deadtarg-dead-targ-dead-targ-deadtarg', {}, None, fields.INVALID_VALUE),
    # Unrecognized UUIDs
            (None, {}, None, fields.UNRECOGNIZED_VALUE),
            ([], {}, None, fields.UNRECOGNIZED_VALUE),
            (set(), {}, None, fields.UNRECOGNIZED_VALUE),
            ({}, {}, None, fields.UNRECOGNIZED_VALUE),
        ]
    )
    def test_process(self, value, kwargs, result, error):
        res, err = self.klass(**kwargs).process(value)
        assert res == result
        assert err == error


@mark.unit
class TestUuidStringField(BaseTests):
    """
    """

    @property
    def klass(self):
        return fields.UuidString

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # Valid UUIDs
    ## A dash separated uuid string is valid
            ('deadbeef-dead-beef-dead-beef-deadbeef', {}, 'deadbeefdeadbeefdeadbeefdeadbeef', None),
    ## A non-separated uuid string is valid
            ('deadbeefdeadbeefdeadbeefdeadbeef', {}, 'deadbeefdeadbeefdeadbeefdeadbeef', None),
    ## A uuid string of numbers is valid
            ('12345678901234567890123456789012', {}, '12345678901234567890123456789012', None),
    ## A uuid object is valid
            (UUID('deadbeef-dead-beef-dead-beef-deadbeef'), {}, 'deadbeefdeadbeefdeadbeefdeadbeef', None),
    ## An integer is a valid uuid
            (295990755083049101712519384020072382191, {}, 'deadbeefdeadbeefdeadbeefdeadbeef', None),
    # Invalid UUIDs
    ## Characters outside the UUID range A-F are invalid
            ('deadtarg-dead-targ-dead-targ-deadtarg', {}, None, fields.INVALID_VALUE),
    # Unrecognized UUIDs
            (None, {}, None, fields.UNRECOGNIZED_VALUE),
            ([], {}, None, fields.UNRECOGNIZED_VALUE),
            (set(), {}, None, fields.UNRECOGNIZED_VALUE),
            ({}, {}, None, fields.UNRECOGNIZED_VALUE),
        ]
    )
    def test_process(self, value, kwargs, result, error):
        res, err = self.klass(**kwargs).process(value)
        assert res == result
        assert err == error


@mark.unit
class TestBoolField(BaseTests):

    @property
    def klass(self):
        return fields.Bool

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # Truthy
            ('T', {}, True, None),
            ('t', {}, True, None),
            ('TRUE', {}, True, None),
            ('True', {}, True, None),
            ('true', {}, True, None),
            ('TrUe', {}, True, None),
            ('1', {}, True, None),
            (1, {}, True, None),
            (True, {}, True, None),
    # Falsey
            ('F', {}, False, None),
            ('f', {}, False, None),
            ('FALSE', {}, False, None),
            ('False', {}, False, None),
            ('false', {}, False, None),
            ('FaLsE', {}, False, None),
            ('0', {}, False, None),
            (0, {}, False, None),
            (False, {}, False, None),
    # Partial True/False are invalid
            ('Tru', {}, None, fields.INVALID_VALUE),
            ('Fals', {}, None, fields.INVALID_VALUE),
    # Integers beyond 0/1 are invalid
            (1337, {}, None, fields.INVALID_VALUE),
    # Unrecognized types
            (None, {}, None, fields.UNRECOGNIZED_VALUE),
            ([], {}, None, fields.UNRECOGNIZED_VALUE),
            ({}, {}, None, fields.UNRECOGNIZED_VALUE),
        ]
    )
    def test_process(self, value, kwargs, result, error):
        res, err = self.klass(**kwargs).process(value)
        assert res == result
        assert err == error


@mark.unit
class TestDateTimeField(BaseTests):
    """
    """

    @property
    def klass(self):
        return fields.DateTime

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # Valid datetimes
    ## A datetime object
            (
                TimeUtils.from_timestamp(6027478417),
                {},
                TimeUtils.from_timestamp(6027478417),
                None,
            ),
    ## A unix timestamp will be cast as a datetime
            (
                6027478417,
                {},
                TimeUtils.from_timestamp(6027478417),
                None,
            ),
    ## Date objects will have the minimum time applied
            (
                TimeUtils.from_timestamp(6027436800).date(),
                {},
                TimeUtils.from_timestamp(6027436800),
                None,
            ),
    ## Datetime strings are valid
            (
                '2161-01-01 11:33:37UTC',
                {},
                TimeUtils.from_timestamp(6027478417),
                None,
            ),
    # Invalid datetimes
    ## A timestamp string is invalid XXX should it be?
            (
                '6027478417',
                {},
                None,
                fields.INVALID_VALUE,
            ),
    # Unrecognized datetimes
            (
                None,
                {},
                None,
                fields.UNRECOGNIZED_VALUE,
            ),
            (
                [],
                {},
                None,
                fields.UNRECOGNIZED_VALUE,
            ),
            (
                set(),
                {},
                None,
                fields.UNRECOGNIZED_VALUE,
            ),
            (
                {},
                {},
                None,
                fields.UNRECOGNIZED_VALUE,
            ),
        ]
    )
    def test_process(self, value, kwargs, result, error):
        res, err = self.klass(**kwargs).process(value)
        assert res == result
        assert err == error


@mark.unit
class TestSetField(BaseTests):

    @property
    def klass(self):
        return fields.Set

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # Valid sets
            (None, {
                'nullable': True
            }, None, {}),
    ##
            (['klingon'], {
                'nested': fields.String()
            }, {'klingon'}, {}),
    ##
            ({'klingon'}, {
                'nested': fields.String()
            }, {'klingon'}, {}),
    ##
            ({}, {}, [], {}),

    # Unrecognized sets
        ]
    )
    def test_process(self, value, kwargs, result, error):

        class MySchema(Schema):
            warriors = self.klass(**kwargs)

        res, err = MySchema().process({'warriors': value})
        assert res['warriors'] == result
        assert err == error


@mark.unit
class TestListField(BaseTests):

    @property
    def klass(self):
        return fields.List

    @mark.parametrize(
        'value, kwargs, result, error',
        [
    # Valid lists
            (None, {
                'nullable': True
            }, None, {}),
    ## providing a list will produce a list
            (['klingon'], {
                'nested': fields.String()
            }, ['klingon'], {}),
    ## providing a set will produce a list
            ({'klingon'}, {
                'nested': fields.String()
            }, ['klingon'], {}),
    ## providing an empty list will produce a list
            ([], {}, [], {}),

    # Unrecognized lists
    #(None, {}, None, {}),
        ]
    )
    def test_process(self, value, kwargs, result, error):

        class MySchema(Schema):
            warriors = self.klass(**kwargs)

        res, err = MySchema().process({'warriors': value})
        assert res['warriors'] == result
        assert err == error

    def test_list_of_nested(self):

        class ListOfNestedSchema(Schema):
            ferengi = fields.Nested({
                'lobes': fields.String(),
            })
            rules = fields.List(fields.Nested({'number': fields.String()}))

        res = ListOfNestedSchema().process({'ferengi': {'lobes': 'yes'}, 'rules': [{'number': '1'}, {'number': '2'}]})
        assert res.data['rules'][0] != {}


@mark.unit
class TestNestedField(BaseTests):

    @property
    def klass(self):
        return fields.Nested

    def test_nested_fields(self):

        class NestedFieldsSchema(Schema):
            stuff = fields.Nested({
                'string': fields.String(),
                'int': fields.Int(),
            })

        res = NestedFieldsSchema().process({'stuff': {'string': 'klingon', 'int': 1337}})
        print(res)
