from appyratus.test import mark, BaseTests
from appyratus.util import DictUtils

from collections import namedtuple


@mark.unit
class TestDictUtilsUnit(BaseTests):
    @property
    def klass(self):
        return DictUtils

    @mark.params(
        'actual, expected',
        [
    # no depth
            ({
                'data': 'android'
            }, {
                'data': 'android'
            }),
    # wat
            (
                {
                    'jean.luc.picard': 'captain'
                }, {
                    'jean': {
                        'luc': {
                            'picard': 'captain'
                        }
                    }
                }
            )
        ]
    )
    def test__unflatten_keys(self, actual, expected):
        result = self.klass.unflatten_keys(actual)
        assert result == expected

    @mark.params(
        'data, other, expected',
        [
    # wat
            (
                {
                    'worf': 'klingon'
                }, {
                    'honor': True
                }, {
                    'worf': 'klingon',
                    'honor': True
                }
            ),
    # nested
            (
                {
                    'geordi': 'engineer'
                }, {
                    'visor': True
                }, {
                    'geordi': 'engineer',
                    'visor': True
                }
            ),
        ]
    )
    def test__merge(self, data, other, expected):
        result = self.klass.merge(data=data, other=other)
        diff_result = self.klass.diff(data=result, other=expected)
        assert not diff_result

    @mark.params(
        'data, other, changed', [
            (dict(a=0), dict(a=1), True),
            (dict(a=0), dict(a=0), False),
            (dict(a=dict(b=0)), dict(a=dict(c=1)), True),
            (dict(a=dict(b=0)), dict(a=dict(b=1)), True),
            (dict(a=dict(b=0)), dict(a=dict(b=0)), False),
        ]
    )
    def test__diff(self, data, other, changed):
        result = self.klass.diff(data=data, other=other)
        assert isinstance(result, dict)
        has_no_change = (not result)
        assert has_no_change is not changed

    #@mark.bparams([(1, 1), (2, 1), (3, 3)])
