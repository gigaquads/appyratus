from __future__ import absolute_import

import rapidjson

from typing import Dict
from uuid import UUID
from datetime import datetime, date

from appyratus.utils import TimeUtils


class JsonEncoder(object):
    def __init__(self, defaults: Dict = None):
        self.defaults = {
            datetime: lambda x: TimeUtils.to_timestamp(x),
            date: lambda x: TimeUtils.to_timestamp(x),
            UUID: lambda x: x.hex,
            set: lambda x: list(x),
        }
        self.defaults.update(defaults or {})

    def encode(self, target):
        return rapidjson.dumps(target, default=self.default)

    def default(self, target):
        func = self.defaults.get(target.__class__)
        if func is None:
            raise ValueError('cannot JSON encode {}'.format(target))
        return func(target)
