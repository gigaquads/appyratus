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

    def test__read(self):
        source = "print('hi')\n"
        source_path = '/tmp/wat.py'
        source_file = PythonModule.write(
            source_path, PythonModule.load_string(source)
        )
        res = self.klass.read(source_path)
        new_source = self.klass.dump(res)
        assert new_source == source

    def test__load(self):
        file_path = "print('hi')"
        res = self.klass.load(file_path)
        assert isinstance(res, ast.Module)
