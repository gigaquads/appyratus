import os
import traceback

from appyratus.memoize import memoized_property
from appyratus.json import JsonEncoder


class BaseError(Exception):
    """
    # Base Error
    """

    @memoized_property
    def encoder(self):
        """
        # Encoder
        Using the JSON Encoder
        """
        return JsonEncoder()

    def __init__(
        self, code: str = None, message: str = None, data: dict = None
    ):
        """ 
        # Args
        `code`, shorthand code to additionally identify with this error
        `message`, detailed information regarding the error
        `data`, Additional structured data to provide with the error
        """
        self.error_code = code or 'error'
        self.error_message = message or 'An error has occurred'
        self.error_data = data or {}

    def _set_error_data(self, code=None, message=None, data=None):
        """ 
            Set error data """
        if code:
            self.error_code = code
        if message:
            self.error_message = message
        if data:
            self.error_data = data

        if self.error_data is None:
            self.error_data = {}
        if self.is_dev_environment:
            self.error_data['traceback'] = traceback.format_exc().split('\n')

    def _build_error_data(self):
        """ 
        # Build error data dictionary 
        """
        return {
            'code': self.error_code,
            'message': self.error_message,
            'data': self.error_data
        }

    def _error_str(self):
        """
        # String representation of the error
        """
        return "{message} ({code})".format(
            code=self.error_code, message=self.error_message
        )

    def __str__(self):
        return self.to_str()

    def to_str(self):
        """ String representation of the error """
        return self._error_str()

    def to_dict(self):
        """ 
        # Returns a dictionary of the error
        """
        return self._build_error_data()

    @property
    def is_dev_environment(self):
        return os.environ.get('SERVICE_ENV', '').lower() == 'dev'

    def to_json(self):
        """
        Returns JSON representation of the error

        This was customized as the Falcon Base errors return JSON pretty printed
        """
        return self.encoder.encode(self.to_dict())
