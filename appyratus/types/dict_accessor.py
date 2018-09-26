from typing import Dict


class DictAccessor(object):
    def __init__(self, data: Dict, default=None):
        for k, v in (data or {}).items():
            setattr(self, k, v)
        self.default = default

    def __getattr__(self, key):
        return self.default

    def get(self, key, default):
        return getattr(self, key, default)
