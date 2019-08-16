from itertools import chain
from typing import List


class ListUtils(object):
    @classmethod
    def flatten(cls, value: List) -> List:
        if value is None:
            return
        res = []
        for k in chain(value):
            if isinstance(k, list):
                res.extend(cls.flatten(k))
            else:
                res.append(k)
        return res
