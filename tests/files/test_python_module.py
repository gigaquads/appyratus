import ast

from appyratus.files import PythonModule
from appyratus.test import (
    FileTypeTests,
    mark,
)


def pytest_generate_tests(metafunc):
    TestPythonModuleFileType.parameterize(metafunc)


class TestPythonModuleFileType(FileTypeTests):

    @classmethod
    def __klass__(cls):
        return PythonModule

    @staticmethod
    def sample_data_is_equal(source_data, dest_data):
        """
        Python ast Modules cannot be directly compared, so we will dump and compare
        """
        return ast.dump(source_data) == ast.dump(dest_data)

