from appyratus.files import Json
from appyratus.test import (
    FileTypeTests,
    mark,
)


def pytest_generate_tests(metafunc):
    TestJsonFileType.parameterize(metafunc)


class TestJsonFileType(FileTypeTests):

    @classmethod
    def __klass__(cls):
        return Json
