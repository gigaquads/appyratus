import pytz

from datetime import datetime


class TimeUtils(object):

    @staticmethod
    def utc_now() -> datetime:
        """
        Return a datetime in UTC timezone.
        """
        return datetime.now(pytz.utc)

    @staticmethod
    def to_timestamp(datetime_obj) -> int:
        """
        From datetime object to UTC integer timestamp (seconds)
        """
        if datetime_obj is None:
            return None

        if isinstance(datetime_obj, datetime):
            if datetime_obj.tzinfo is None:
                raise ValueError('datetime object has no timezone')
        elif isinstance(datetime_obj, date):
            datetime_obj = datetime\
                .strptime(str(datetime_obj), "%Y-%m-%d")\
                .replace(tzinfo=pytz.utc)

        epoch = datetime.fromtimestamp(0, pytz.utc)
        return int((datetime_obj - epoch).total_seconds())

    @staticmethod
    def from_timestamp(timestamp) -> datetime:
        """
        Return the timestamp int as a UTC datetime object.
        """
        return datetime.fromtimestamp(timestamp, tz=pytz.utc)
