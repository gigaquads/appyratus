from appyratus.reflection.ast_parser import AstParser
from appyratus.reflection import python_ast
from appyratus.reflection.python_ast import (
    PythonModule,
    PythonClass,
    PythonFunction,
    PythonImport,
    PythonImportFrom,
    PythonDecorator,
    PythonCall,
    PythonAttribute,
    PythonArgument,
    PythonKeywordArgument,
)
from appyratus.test import mark, BaseTests
from appyratus.utils import DictUtils

from collections import namedtuple


@mark.unit
class TestAstParser(BaseTests):
    @property
    def klass(self):
        return AstParser

    def test__parse_package(self):
        package = self.klass().parse_package('appyratus.reflection.ast_parser')
        assert isinstance(package, list)
        assert package[0]['classes'][0]['name'] == self.klass.__name__


@mark.unit
class TestPythonModule(BaseTests):
    @property
    def klass(self):
        return PythonModule

    def test__from_filepath(self):
        mymodule = self.klass.from_filepath(python_ast.__file__)
