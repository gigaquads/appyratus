from appyratus.test import mark, BaseTests
from appyratus.utils import ListUtils

from collections import namedtuple


@mark.unit
class TestListUtils(BaseTests):

    @property
    def klass(self):
        return ListUtils

    @mark.params(
        'data, expected',
        [
    # single list item zero depth
            (['a'], ['a']),
    # multiple list items zero depth
            (['a', 'b'], ['a', 'b']),
    # depth-1 list items
            (['a', 'b', ['c']], ['a', 'b', 'c']),
    # depth-2 list items
            (['a', 'b', ['c', ['d']]], ['a', 'b', 'c', 'd']),
    # depth-2 numbers too
            ([1, [2, [3]]], [1, 2, 3]),
    # only list types are iterated on, no set, tuple
            ([1, (2, 3)], [1, (2, 3)])
        ]
    )
    def test_flatten(self, data, expected):
        res = self.klass.flatten(data)
        assert res == expected

    @mark.params(
        'data, size, expected',
        [
    # single list item zero depth
            (['a'], 1, [['a']]),
    # multiple list items zero depth
            (['a', 'c'], 2, [['a'], ['c']]),
    # multiple list items zero depth
            (['a', 'b'], 1, [['a', 'b']]),
    # loose ends
            (['a', 'b', 'c'], 2, [['a', 'b'], ['c']]),
    # if it cannot split into equal chunks then it will create empty items
            (['a'], 3, [['a'], [], []]),
        ]
    )
    def test_chunk(self, data, size, expected):
        res = self.klass.chunk(data, size)
        assert res == expected
