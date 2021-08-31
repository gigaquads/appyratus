import pytest
import inspect
from typing import (
    List,
    Text,
)

from appyratus.files import File
from appyratus.test import BaseTests
from appyratus.utils.path_utils import PathUtils
from appyratus.utils.string_utils import StringUtils


class FileTypeTests(BaseTests):
    """
    # File Type Tests
    Testing functionality around file types
    """

    @staticmethod
    def parameterize(metafunc):
        """
        # Parameterize
        To be called by each module that has inherited FileTypeTests class.
        Any test method in this class must include the `sample_path` argument
        in order for this parameterization to take effect on it.  Additionally,
        if the module has multiple test classes prepared, then it will look for
        the `get_samples` method to ensure that the argument has been applied
        to a class that should support it.  And if there are no samples
        available, then the test will be skipped.

        It should be defined as:
        ```
        def pytest_generate_tests(metafunc):
            TestJsonFileType.parameterize(metafunc)
        ```
        """
        spec = inspect.getfullargspec(metafunc.function)

        def apply_arg(sample_type, sample_path_arg):
            idlist = []
            argnames = []
            argvalues = []
            for sample in metafunc.cls.get_samples(sample_type):
                idlist.append(PathUtils.get_name(sample))
                items = [sample]
                argnames = [sample_path_arg]
                argvalues.append(items)
            metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")

        if hasattr(metafunc.cls, 'get_samples'):
            sample_types = ['valid', 'invalid']
            for sample_type in sample_types:
                sample_path_arg = f'{sample_type}_sample_path'
                if sample_path_arg in spec.args:
                    apply_arg(sample_type, sample_path_arg)

    @classmethod
    def get_samples_path(cls, sample_type: Text = None):
        """
        # Get Samples Path
        Get the path containing all samples for a particular file type
        """

        return PathUtils.join(
            PathUtils.get_dir_path(__file__), 'sample', StringUtils.dash(cls.get_klass().__name__),
            sample_type if sample_type is not None else 'valid'
        )

    @classmethod
    def get_samples(cls, sample_type: Text = None) -> List[Text]:
        """
        # Get Samples
        Get all available samples from filesystem from the configured sample path
        """
        _, files = PathUtils.get_nodes(cls.get_samples_path(sample_type))
        return files

    def read_sample_data(cls, path: Text, raw: bool = False) -> Text:
        """
        # Read Sample Data
        Read sample data with provided path using the assigned file type class
        """
        source_class = File if raw else cls.get_klass()
        source_data = source_class.read(path)
        return source_data

    def test_sample_is_valid(self, valid_sample_path):
        """
        # Test Sample Is Valid
        Run a series of file type sample sets through several file type methods
        and ensure that they can be processed.

        These file type methods include:
        - `read` file type data from FS 
        - `load` file type data into python data structure
        - `dump` python data structure back to file type format 
        - `write` file type data to FS
        """
        # read the source data
        source_data = self.read_sample_data(valid_sample_path)
        # now write the data back to disk
        # XXX better way to use a temp file?
        dest_path = f'/tmp/test_{self.klass.__name__}'
        self.klass.write(dest_path, source_data)
        # read the temp contents again
        dest_data = self.klass.read(dest_path)
        # assert that data is as what it was after roundtrip
        assert self.sample_data_is_equal(source_data, dest_data)

    @staticmethod
    def sample_data_is_equal(source_data, dest_data):
        """
        # Sample Data Is Equal
        Comparison of two data sets to determine if they are the same
        """
        return source_data == dest_data

    def test_sample_is_invalid(self, invalid_sample_path):
        """
        # Test Sample Is Invalid
        As much as a sample can be valid, it can also be invalid, like a syntax
        error or passing in the wrong file type
        """
        with pytest.raises(Exception) as wat:
            self.klass.read(invalid_sample_path)
