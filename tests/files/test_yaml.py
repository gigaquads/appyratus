from appyratus.files import Yaml
from appyratus.test import (
    FileTypeTests,
    mark,
)


def pytest_generate_tests(metafunc):
    TestYamlFile.parameterize(metafunc)


class TestYamlFile(FileTypeTests):

    @classmethod
    def __klass__(cls):
        return Yaml
