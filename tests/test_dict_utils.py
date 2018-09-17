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
    # hey
            (
                {
                    'tanagra[0].name': 'darmok',
                    'tanagra[1].name': 'jalad',
                    'tanagra[1].weird': 'culture',
                }, {
                    'tanagra': [
                        {
                            'name': 'darmok',
                        }, {
                            'name': 'jalad',
                            'weird': 'culture',
                        }
                    ]
                }
            ),
    # keys without separators will not be affected
            ({
                'data': 'android'
            }, {
                'data': 'android'
            }),
    # keys with special characters will not be split apart incorrectly
            (
                {
                    'deanna-troi.mpath': 'counselor'
                }, {
                    'deanna-troi': {
                        'mpath': 'counselor'
                    }
                }
            ),
    # keys with multiple separators will be transformed into a nested dictionary
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
            ),
    # keys with trailing separator will create an empty dict key (not good)
            ({
                'tasha.': 'romulan'
            }, {
                'tasha': {
                    '': 'romulan'
                }
            }),
    # keys with leading separator will create an empty dict key (not good)
            (
                {
                    '.will.riker': 'cavalier'
                }, {
                    '': {
                        'will': {
                            'riker': 'cavalier'
                        }
                    }
                }
            ),
    # integer keys will be converted to a list
            (
                {
                    'tanagra.0.darmok': 'weird',
                    'tanagra.1.jalad': 'culture',
                }, {
                    'tanagra': {
                        '0': {
                            'darmok': 'weird'
                        },
                        '1': {
                            'jalad': 'culture',
                        }
                    }
                }
            ),
        ]
    )
    def test__unflatten_keys(self, actual, expected):
        result = self.klass.unflatten_keys(actual)
        from pprint import pprint
        print()
        pprint('===============')
        pprint(result)
        #diff_result = self.klass.diff(data=result, other=expected)
        #assert not diff_result

    @mark.params(
        'actual, expected',
        [
    # hey
            (
                {
                    'tanagra': [
                        {
                            'name': 'darmok',
                        }, {
                            'name': 'jalad',
                            'weird': 'culture',
                        }
                    ]
                }, {
                    'tanagra[0].name': 'darmok',
                    'tanagra[1].name': 'jalad',
                    'tanagra[1].weird': 'culture',
                }
            ),
        ]
    )
    def test__flatten(self, actual, expected):
        result = self.klass.flatten(actual)
        from pprint import pprint
        print()
        print('===============')
        pprint(result)

    @mark.params(
        'data, other, expected',
        [
    # unique keys are merged
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
    # nested keys are merged
            (
                {
                    'geordi': {
                        'engineer': True,
                        'visor': False
                    }
                }, {
                    'geordi': {
                        'visor': True
                    }
                }, {
                    'geordi': {
                        'engineer': True,
                        'visor': True
                    }
                }
            ),
        ]
    )
    def test__merge(self, data, other, expected):
        result = self.klass.merge(data=data, other=other)
        diff_result = self.klass.diff(data=result, other=expected)
        assert not diff_result

    @mark.params(
        'data, other, changed',
        [
    # flat keys will be compared
            (dict(a=0), dict(a=1), True),
            (dict(a=0), dict(a=0), False),
    # nested will be recursively compared
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

    @mark.params(
        'data, expected',
        [
    #wat
            ({
                'blah': 'blah!'
            }, {}),
    #wat
            ({
                'meh': {
                    'blah': 'blah!'
                }
            }, {
                'meh': {}
            }),
    #wat
            ({
                'meh': None
            }, {}),
    #wat
            ({
                'meh': {
                    'meh': None
                }
            }, {
                'meh': {}
            }),
    #wat
            ({
                'meh': 'meh!'
            }, {
                'meh': 'meh!'
            })
        ]
    )
    def test__remove_keys(self, data, expected):
        keys = ['blah', 'hmph']
        values = [None]
        res = self.klass.remove_keys(data, keys, values)
        #print("\n", expected, res)
