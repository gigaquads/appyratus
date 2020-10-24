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
    def test__flatten(self, data, expected):
        res = self.klass.flatten(data)
        assert res == expected
