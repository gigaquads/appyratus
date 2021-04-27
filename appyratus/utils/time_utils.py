from typing import Callable, Tuple, List, Union, Optional, Text
from datetime import datetime, timedelta, date

import pytz

from dateutil.parser import parse

class TimeUtils(object):

    @classmethod
    def utc_now(cls) -> datetime:
        """
        Return a datetime in UTC timezone.
        """
        return datetime.now(pytz.utc)

    @classmethod
    def utc_timestamp(cls) -> int:
        """
        Return a datetime in UTC timezone.
        """
        return cls.to_timestamp(datetime.now(pytz.utc))

    @classmethod
    def to_timestamp(cls, obj: Union[datetime, date, str]) -> float:
        """
        From datetime object to UTC timestamp (seconds)
        """
        if obj is None:
            return None

        timezone = pytz.utc

        if isinstance(obj, datetime):
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=timezone)
        elif isinstance(obj, date):
            obj = datetime\
                .strptime(str(obj), "%Y-%m-%d")\
                .replace(tzinfo=timezone)
        else:
            obj = cls.from_object(obj)

        epoch = datetime.fromtimestamp(0, timezone)
        return (obj - epoch).total_seconds()

    @classmethod
    def from_object(cls, obj, timezone=pytz.utc) -> datetime:
        """
        Convert the input object into a datetime object with a specified
        timezone.
        """
        # convert obj to datetime
        if isinstance(obj, datetime):
            dt = obj
        elif isinstance(obj, str):
            dt = parse(obj)
        elif isinstance(obj, (int, float)):
            dt = cls.from_timestamp(obj)
        else:
            raise ValueError(f'unrecognized datetime object: {obj}')

        # set the timezone on the new datetime
        return dt.replace(tzinfo=timezone)

    @classmethod
    def from_timestamp(cls, timestamp: int, timezone=pytz.utc) -> datetime:
        """
        Return the timestamp int as a UTC datetime object.
        """
        return datetime.fromtimestamp(timestamp, tz=timezone)

    @classmethod
    def parse_datetime(
        cls, obj: Union[Text, datetime, date]
    ) -> Optional[datetime]:
        return cls.from_object(obj)

    @classmethod
    def pprint_timedelta(cls, delta) -> str:
        delta = cls.parse_timedelta(delta)
        s_total = round(delta.total_seconds())
        h, remainder = divmod(s_total, 3600)
        m, s = divmod(remainder, 60)
        chunks = []
        if h:
            chunks.append(f'{h}h')
        if m:
            chunks.append(f'{m}m')
        if s:
            chunks.append(f'{s}s')
        return ', '.join(chunks)

    @staticmethod
    def parse_timedelta(
        obj: Union[Text, timedelta]
    ) -> Optional[timedelta]:
        """
        Normalize an object of some type to a datetime.timedelta object.
        """
        if isinstance(obj, timedelta):
            return obj
        elif isinstance(obj, str):
            h, m, s = obj.split(':')
            return timedelta(
                hours=int(h), minutes=int(m), seconds=int(s)
            )
        return

    @classmethod
    def set_timezone(cls, time: datetime, tz='utc') -> datetime:
        return time.replace(tzinfo=getattr(pytz, tz))

    @classmethod
    def timed(cls, func: Callable) -> Tuple[object, timedelta]:
        start = cls.utc_now()
        result = func()
        end = cls.utc_now()
        return (result, (end - start))

    @classmethod
    def datetime_range(
        cls, start: datetime, stop: datetime, step: timedelta
    ) -> List[datetime]:
        """
        Create an array of equally spaced datetime objects that include the
        start time but exclude the stop time.
        """
        return [start + (i * step) for i in range((stop - start) // step)]
