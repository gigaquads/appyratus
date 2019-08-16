from appyratus.test import mark, BaseTests
from appyratus.utils import ListUtils

from collections import namedtuple


@mark.unit
class TestListUtils(BaseTests):
    @property
    def klass(self):
        return ListUtils

    @mark.params(
        'data, expected', [
            (['a'], ['a']),
            (['a', 'b'], ['a', 'b']),
            (['a', 'b', ['c']], ['a', 'b', 'c']),
            (['a', 'b', ['c', ['d']]], ['a', 'b', 'c', 'd']),
            ([1, [2, [3]]], [1, 2, 3]),
        ]
    )
    def test__flatten(self, data, expected):
        res = self.klass.flatten(data)
        assert res == expected
