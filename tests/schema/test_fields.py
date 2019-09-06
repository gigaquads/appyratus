from appyratus.test import mark, BaseTests
from appyratus.schema import fields, Schema


@mark.unit
class TestStringField(BaseTests):
    @property
    def klass(self):
        return fields.String

    @mark.params(
        'value, expected, kwargs', [
            ('klingon', 'klingon', {}),
            ('', '', {}),
            (None, None, {}),
        ]
    )
    def test__wat(self, value, expected, kwargs):
        res, err = self.klass(**kwargs).process(value)
        assert res == expected


@mark.unit
class TestNestedField(BaseTests):
    @property
    def klass(self):
        return fields.Nested

    def test__flatten(self):
        class MySchema(Schema):
            ferengi = fields.Nested({
                'lobes': fields.String(),
            })
            rules = fields.List(fields.Nested({'number': fields.String()}))

        res = MySchema().process(
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
