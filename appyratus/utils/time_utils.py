import pytz

from datetime import datetime


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
    def to_timestamp(cls, datetime_obj) -> int:
        """
        From datetime object to UTC integer timestamp (seconds)
        """
        if datetime_obj is None:
            return None
        timezone = pytz.utc
        if isinstance(datetime_obj, datetime):
            if datetime_obj.tzinfo is None:
                datetime_obj = datetime_obj.replace(tzinfo=timezone)
        elif isinstance(datetime_obj, date):
            datetime_obj = datetime\
                .strptime(str(datetime_obj), "%Y-%m-%d")\
                .replace(tzinfo=timezone)

        epoch = datetime.fromtimestamp(0, timezone)
        return int((datetime_obj - epoch).total_seconds())

    @classmethod
    def from_timestamp(cls, timestamp, timezone=None) -> datetime:
        """
        Return the timestamp int as a UTC datetime object.
        """
        timezone = pytz.utc
        return datetime.fromtimestamp(timestamp, tz=timezone)
