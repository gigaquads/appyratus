import os
import traceback

from appyratus.files import Json
from appyratus.memoize import memoized_property


class BaseError(Exception):
    """
    # Base Error
    """
    error_code = 'error'
    error_message = 'An error has occurred'
    error_data = {}
    error_help = None

    def __init__(self, code: str = None, message: str = None, data: dict = None):
        """ 
        # Args
        `code`, shorthand code to additionally identify with this error
        `message`, detailed information regarding the error
        `data`, Additional structured data to provide with the error
        """
        if code:
            self.error_code = code
        if message:
            self.error_message = message
        if data:
            self.error_data = data

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

        error_message = self.error_message.format(**self.error_data)
        error_help = ', ' + self.error_help if self.error_help else ''
        return "{message} [{code}]{help}".format(
            code=self.error_code, message=error_message, help=error_help
        )

    def __str__(self):
        return self.to_str()

    def to_str(self):
        """ 
        String representation of the error 
        """
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
        return Json.dump(self.to_dict())
