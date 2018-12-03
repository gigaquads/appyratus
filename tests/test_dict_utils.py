from appyratus.test import mark, BaseTests
from appyratus.utils import DictUtils

from collections import namedtuple


@mark.unit
class TestDictUtils(BaseTests):
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
    # integer keys will be converted to dict keys, and not a list
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
        diff_result = self.klass.diff(expected, result)
        assert not diff_result

    @mark.params(
        'actual, expected, whatever',
        [
    # a basic nested dictionary
            ({
                'a': {
                    'b': 'z'
                }
            }, {
                'a.b': 'z'
            }, {}),
    # a dictionary that has a value that is a list, containing multiple dictionaries
            (
                {
                    'a': [{
                        'b': 'z',
                    }, {
                        'b': 'y',
                        'c': {
                            'd': 'x'
                        },
                    }]
                }, {
                    'a[0].b': 'z',
                    'a[1].b': 'y',
                    'a[1].c.d': 'x',
                }, {}
            ),
    # a dict that has a value that is a list containing scalar values
            ({
                'a': '1',
                'b': ['z']
            }, {
                'a': '1',
                'b[0]': 'z'
            }, {}),

    # integers as strings for dict keys do not act as any sort of list
            ({
                'a': {
                    '1': 'z',
                    '2': 'y',
                }
            }, {
                'a.1': 'z',
                'a.2': 'y'
            }, {}),
    # dicts with integers as keys are still dict keys
            ({
                'a': {
                    1: 'z',
                    3: 'x'
                }
            }, {
                'a.1': 'z',
                'a.3': 'x'
            }, {})
        ]
    )
    def test__flatten_keys(self, actual, expected, whatever):
        result = self.klass.flatten_keys(actual)
        diff_res = self.klass.diff(expected, result)
        assert not diff_res

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
        'data, other, is_changed',
        [
    # list in a dict key is comparable
            ({
                'hmm': ['heh']
            }, {
                'hmm': ['heh']
            }, False),
            ({
                'hmm': ['heh', 'huh']
            }, {
                'hmm': ['heh']
            }, True),
    # blah
            ({
                'a': {
                    'b': 0
                }
            }, {
                'a': {
                    'b': 0
                }
            }, False),
    # flat keys
            ({
                'a': 0
            }, {
                'a': 1
            }, True),
    # unchanged data
            ({
                'a': 0
            }, {
                'a': 0
            }, False),
    # nested will be recursively compared
            ({
                'a': {
                    'b': 0
                }
            }, {
                'a': {
                    'c': 1
                }
            }, True),
    # blah
            ({
                'a': {
                    'b': 0
                }
            }, {
                'a': {
                    'b': 1
                }
            }, True),
        ]
    )
    def test__diff(self, data, other, is_changed):
        result = self.klass.diff(data=data, other=other)
        has_no_change = (not result)
        assert has_no_change is not is_changed

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
            }),
        ]
    )
    def test__remove_keys(self, data, expected):
        keys = ['blah', 'hmph']
        values = [None]
        res = self.klass.remove_keys(data, keys, values)
        #print("\n", expected, res)
