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

        if isinstance(datetime_obj, datetime):
            if datetime_obj.tzinfo is None:
                datetime_obj = datetime_obj.replace(tzinfo=pytz.utc)
        elif isinstance(datetime_obj, date):
            datetime_obj = datetime\
                .strptime(str(datetime_obj), "%Y-%m-%d")\
                .replace(tzinfo=pytz.utc)

        epoch = datetime.fromtimestamp(0, pytz.utc)
        return int((datetime_obj - epoch).total_seconds())

    @classmethod
    def from_timestamp(cls, timestamp) -> datetime:
        """
        Return the timestamp int as a UTC datetime object.
        """
        return datetime.fromtimestamp(timestamp, tz=pytz.utc)
