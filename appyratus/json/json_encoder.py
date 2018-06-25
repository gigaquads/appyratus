import re
import json
import uuid
import decimal
import numpy as np

from datetime import datetime, date

from appyratus.time import to_timestamp


class JsonEncoder(json.JSONEncoder):
    RE_TYPE = re.compile('').__class__

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return to_timestamp(obj)
        elif isinstance(obj, uuid.UUID):
            return obj.hex
        elif isinstance(obj, self.RE_TYPE):
            return obj.pattern
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, np.ndarray):
            return str(list(obj))
        else:
            return repr(obj)
