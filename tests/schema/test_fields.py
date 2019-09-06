from appyratus.test import mark, BaseTests
from appyratus.schema import Schema
from appyratus.schema.fields import fields

# TODO
# Bytes
# FormatString
# Uint32
# Uint64
# Sint32
# Sint64
# Float
# Email
# Uuid
# UuidString
# Bool
# DateTime
# DateTimeString
# Timestamp
# Set
# Dict
# FilePath
# IpAddress
# DomainName
# Url


@mark.unit
class TestStringField(BaseTests):

    @property
    def klass(self):
        return fields.String

    @mark.params(
        'value, kwargs, result, error',
        [
    # 'klingon' is a valid string
            ('klingon', {}, 'klingon', None),
    # empty string is a valid string
            ('', {}, '', None),
    # 1337 integer will be cast as a string
            (1337, {}, '1337', None),
    # None is an unrecognized string
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

    @mark.params(
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
class TestListField(BaseTests):

    @property
    def klass(self):
        return fields.List

    def test_list_of_string(self):

        class ListOfStringSchema(Schema):
            rules = self.klass(fields.String())

        res = ListOfStringSchema().process({'rules': ['do good', 'be good']})
        print(res)

    def test_list_of_nested(self):

        class ListOfNestedSchema(Schema):
            ferengi = fields.Nested({
                'lobes': fields.String(),
            })
            rules = fields.List(fields.Nested({'number': fields.String()}))

        res = ListOfNestedSchema().process(
            {
                'ferengi': {
                    'lobes': 'yes'
                },
                'rules': [{
                    'number': '1'
                }, {
                    'number': '2'
                }]
            }
        )

        print(res)


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
