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
                    'tanagra':
                        [{
                            'name': 'darmok',
                        }, {
                            'name': 'jalad',
                            'weird': 'culture',
                        }]
                }
            ),
    # lists at the trailing end are taken into consideration
            ({
                'data.feel[0]': 'plenty'
            }, {
                'data': {
                    'feel': ['plenty']
                }
            }),
    # keys without separators will not be affected
            ({
                'data': 'android'
            }, {
                'data': 'android'
            }),
    # keys with special characters will not be split apart incorrectly
            ({
                'deanna-troi.mpath': 'counselor'
            }, {
                'deanna-troi': {
                    'mpath': 'counselor'
                }
            }),
    # keys with multiple separators will be transformed into a nested dictionary
            ({
                'jean.luc.picard': 'captain'
            }, {
                'jean': {
                    'luc': {
                        'picard': 'captain'
                    }
                }
            }),
    # keys with trailing separator will create an empty dict key (not good)
            ({
                'tasha.': 'romulan'
            }, {
                'tasha': {
                    '': 'romulan'
                }
            }),
    # keys with leading separator will create an empty dict key (not good)
            ({
                '.will.riker': 'cavalier'
            }, {
                '': {
                    'will': {
                        'riker': 'cavalier'
                    }
                }
            }),
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
        print("\n")
        print(actual)
        print(expected)
        print(result)
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
            }, {}),
    # an empty dict returns an empty dict
            ({}, {}, {}),
    # nothing returns nothing
            (None, None, {})
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
            ({
                'worf': 'klingon'
            }, {
                'honor': True
            }, {
                'worf': 'klingon',
                'honor': True
            }),
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
        'data, keys, values, empty_values, expected',
        [
    # remove a key by name
            ({
                'a': 1,
                'b': 2
            }, ('a', ), None, None, {
                'b': 2
            }),
    # skip a key by name
            ({
                'a': 1,
            }, ('z', ), None, None, {
                'a': 1
            }),

    # remove multiple keys by name
            ({
                'a': 1,
                'b': 2
            }, ('a', 'b'), None, None, {}),
    # remove a key by value
            ({
                'a': 1,
                'b': 2
            }, None, (1, ), None, {
                'b': 2
            }),
    # remove multiple keys by value
            ({
                'a': 1,
                'b': {
                    'z': None
                }
            }, None, (1, None), None, {
                'b': {}
            }),
    # remove a key by empty value type
            ({
                'a': [],
            }, None, None, (list, ), {}),
    # ignore a key by empty value type
            ({
                'a': [],
            }, None, None, (dict, ), {
                'a': []
            }),
    # remove multiple keys by value type
            (
                {
                    'a': [],
                    'b': '',
                    'c': {},
                    'd': None,
                }, None, None, (list, str, dict, type(None)), {}
            ),
    # non-set operations can be provided
            ({
                'a': [],
                'b': '',
                'c': {},
            }, 'a', '', dict, {}),
        ]
    )
    def test__remove_keys(self, data, keys, values, empty_values, expected):
        result = self.klass.remove_keys(data, keys, values, empty_values)
        assert result == expected

    @mark.params(
        'data, keys, expected',
        [
    # providing a key will return the entire value
            (
                {
                    'a': [1, 2]
                },
                ['a'],
                {
                    'a': [1, 2]
                },
            ),
    # providing a key with an index will return the index of the key value's
    # list
            (
                {
                    'a': [1, 2, 3],
                    'b': 4,
                    'c': None,
                },
                ['a[2]', 'b'],
                {
                    'a': [3],
                    'b': 4,
                },
            ),
    # more something
            (
                {
                    'a': [{
                        'b': 1
                    }, {
                        'c': 2
                    }]
                },
                ['a[0].c'],
                {
                    'a': [{'c': 2}]
                },
            ),
        ]
    )
    def test__pluck(self, data, keys, expected):
        result = self.klass.pluck(data, keys)
        print("\n")
        print(data)
        print(keys)
        print(expected, '==', result)
