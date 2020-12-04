from itertools import (
    accumulate,
    chain,
    repeat,
    tee,
)
from typing import List


class ListUtils(object):
    """
    List Utils
    """

    @classmethod
    def flatten(cls, value: List) -> List:
        """
        Flatten a list recursively
        """
        if value is None:
            return
        res = []
        for k in chain(value):
            if isinstance(k, list):
                res.extend(cls.flatten(k))
            else:
                res.append(k)
        return res

    @classmethod
    def chunk(cls, value: List, size: int):
        """
        Break a list apart into chunks
        """
        xs = value
        n = size
        assert n > 0
        L = len(xs)
        s, r = divmod(L, n)
        widths = chain(repeat(s + 1, r), repeat(s, n - r))
        offsets = accumulate(chain((0, ), widths))
        b, e = tee(offsets)
        next(e)
        return [xs[s] for s in map(slice, b, e)]
