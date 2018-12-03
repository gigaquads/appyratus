from __future__ import absolute_import

import re
import json
import uuid
import decimal
import numpy as np

from datetime import datetime, date

from appyratus.utils import TimeUtils


class JsonEncoder(json.JSONEncoder):
    RegularExpression = re.compile('').__class__

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return TimeUtils.to_timestamp(obj)
        elif isinstance(obj, uuid.UUID):
            return obj.hex
        elif isinstance(obj, self.RegularExpression):
            return obj.pattern
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, np.ndarray):
            return str(list(obj))
        else:
            return super().default(obj)
