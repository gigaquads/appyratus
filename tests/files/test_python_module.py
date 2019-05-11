import ast
from io import StringIO
from collections import namedtuple

from appyratus.test import mark, BaseTests
from appyratus.files import PythonModule


@mark.unit
class TestPythonModuleFile(BaseTests):
    @property
    def klass(self):
        return PythonModule

    def test__from_file(self):
        source = "print('hi')\n"
        source_path = '/tmp/wat.py'
        source_file = PythonModule.to_file(
            source_path, PythonModule.load_string(source)
        )
        res = self.klass.from_file(source_path)
        new_source = self.klass.to_source(res)
        assert new_source == source

    def test__from_string(self):
        file_path = "print('hi')"
        res = self.klass.from_string(file_path)
        assert isinstance(res, ast.Module)
