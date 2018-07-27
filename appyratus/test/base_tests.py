from abc import abstractmethod
from mock import patch, MagicMock
from contextlib import contextmanager
import inspect


class BaseTests(object):
    """
    # Base Tests
    Provides common test functionality for testing
    """

    @property
    @abstractmethod
    def klass(self):
        """
        Class associated to this test
        """
        return

    def instance(self, *args, **kwargs):
        """
        Build an object from defined class
        """
        return self.klass(*args, **kwargs)

    @property
    def module_path(self):
        """
        Path to the target class's module
        """
        return inspect.getmodule(self.klass).__name__

    @property
    def klass_path(self):
        """
        Path to the target class
        """
        return "{}.{}".format(self.module_path, self.klass.__name__)

    @contextmanager
    def mock(
        self,
        path: str=None,
        method: str=None,
        prop: str=None,
        raw: bool=False,
        **kwargs
    ):
        """
        # Mock
        Establish a mock object relative to the target module.

        # Args
        - `path`: Additional path, relative to the module path
        - `method`: an optional method to mock on the module class
        - `prop`: mock a property on a module class
        - `raw`: do not attempt to restrict the path to the target module
        - `kwargs`: additional key word args to be passed into the pytest patch method

        # Usage
        ```
        with self.mock('
        """
        if not raw:
            if not path:
                path = self.klass.__name__
            if method:
                path = "{}.{}".format(path, method)
            if prop:
                path = "{}.{}".format(path, prop)
            path = "{}.{}".format(self.module_path, path)
        with patch(path, **kwargs) as mock_obj:
            if prop:
                mock_obj.__get__ = MagicMock(**kwargs)
                yield mock_obj
            else:
                yield mock_obj
