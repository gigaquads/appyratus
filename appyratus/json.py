from __future__ import absolute_import

from datetime import (
    date,
    datetime,
)
from typing import Dict
from uuid import UUID

import rapidjson

from appyratus.utils.time_utils import TimeUtils
from appyratus.utils.dict_utils import DictObject


class JsonEncoder(object):
    """
    # Json Encoder
    Backed by rapidjson 
    """

    def __init__(self, defaults: Dict = None):
        self.defaults = {
            datetime: lambda x: TimeUtils.to_timestamp(x),
            date: lambda x: TimeUtils.to_timestamp(x),
            UUID: lambda x: x.hex,
            set: lambda x: list(x),
            DictObject: lambda x: x.to_dict(),
        }
        self.defaults.update(defaults or {})

    @classmethod
    def get_instance(cls):
        """
        # Get Instance
        Get an instance of the Json Encoder class
        """
        # TODO make this a singleton
        return cls()

    def default(self, target, **kwargs):
        func = self.defaults.get(target.__class__)
        if func is None:
            return str(target)
        return func(target)

    def encode(self, target, **kwargs):
        """
        # Encode
        https://github.com/python-rapidjson/python-rapidjson/blob/master/docs/dumps.rst
        """
        return rapidjson.dumps(target, default=self.default, **kwargs)

    @staticmethod
    def decode(*args, **kwargs):
        """
        # Decode
        https://github.com/python-rapidjson/python-rapidjson/blob/master/docs/loads.rst
        """
        if args[0] is None:
            return None
        else:
            return rapidjson.loads(*args, **kwargs)
