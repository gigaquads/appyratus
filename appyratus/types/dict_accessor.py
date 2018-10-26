from typing import Dict


class DictAccessor(object):
    def __init__(self, data: Dict, default=None):
        keys = []
        for k, v in (data or {}).items():
            setattr(self, k, v)
            keys.append(k)
        self.default = default
        self.keys = tuple(keys)

    def __getattr__(self, key):
        return self.default

    def get(self, key, default):
        return getattr(self, key, default)

    def to_dict(self):
        return {k: getattr(self, k) for k in self.keys}
