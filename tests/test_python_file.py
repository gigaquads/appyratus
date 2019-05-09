import ast
from collections import namedtuple

from appyratus.test import mark, BaseTests
from appyratus.files import Python




@mark.unit
class TestPythonFile(BaseTests):
    @property
    def klass(self):
        return Python

    @mark.params('actual, expected', [(1, 2)])
    def test__from_file(self, actual, expected):
        from io import StringIO
        file_path = StringIO("print('hi')")
        res = self.klass.from_file(file_path)
        import ipdb
        ipdb.set_trace()
        print('=' * 100)

    @mark.params('actual, expected', [(1, 2)])
    def test__from_string(self, actual, expected):
        from io import StringIO
        file_path = "print('hi')"
        res = self.klass.from_string(file_path)
        assert isinstance(res, ast.Module)
