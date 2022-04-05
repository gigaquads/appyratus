from collections import namedtuple

from appyratus.reflection import python_ast
from appyratus.reflection.ast_parser import AstParser
from appyratus.reflection.python_ast import (
    PythonArgument,
    PythonAttribute,
    PythonCall,
    PythonClass,
    PythonDecorator,
    PythonFunction,
    PythonImport,
    PythonImportFrom,
    PythonKeywordArgument,
    PythonModule,
)
from appyratus.test import BaseTests, mark
from appyratus.utils.dict_utils import DictUtils


@mark.unit
@mark.skip(reason='needs work')
class TestAstParser(BaseTests):

    @property
    def klass(self):
        return AstParser

    def test__parse_package(self):
        package = self.klass().parse_package('appyratus.reflection.ast_parser')
        assert isinstance(package, list)
        assert package[0]['classes'][0]['name'] == self.klass.__name__


@mark.unit
@mark.skip(reason='needs work')
class TestPythonModule(BaseTests):

    @property
    def klass(self):
        return PythonModule

    def test__from_filepath(self):
        mymodule = self.klass.from_filepath(python_ast.__file__)
        assert isinstance(mymodule, self.klass)
