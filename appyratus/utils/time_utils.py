import pytz

from datetime import datetime

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

        # set the timezone on the new datetime
        dt.replace(tzinfo=timezone)

        return dt

    @classmethod
    def from_timestamp(cls, timestamp, timezone=pytz.utc) -> datetime:
        """
        Return the timestamp int as a UTC datetime object.
        """
        return datetime.fromtimestamp(timestamp, tz=timezone)
