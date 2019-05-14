import re
from appyratus.files import File
from appyratus.utils import DictObject
from typing import Text, List, Dict

from .ast_parser import AstParser


class BaseNode(object):
    def __init__(self, ast=None, *args, **kwargs):
        self._ast = ast

    @property
    def repr_values(self):
        return []

    def __repr__(self):
        if self.repr_values:
            values = ','.join(self.repr_values)
        else:
            values = ''
        return f'<{self.__class__.__name__}({values})>'

    def resolve_objects(self, klass: 'BaseNode', data: List, key: Text = None):
        if not key:
            key = 'name'
        if not data:
            return []

        return DictObject.from_list(key, [klass(**d) for d in data])


class NamedNode(BaseNode):
    def __init__(self, name: Text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name

    @property
    def repr_values(self):
        return [f'"{self.name}"']

    @property
    def name(self):
        return self._name


class PythonModule(NamedNode):
    """
    # Module

    # Fields
    file
    classes
    functions
    imports
    """

    def __init__(
        self,
        path: Text,
        classes: List['PythonClass'] = None,
        functions: List['PythonFunction'] = None,
        imports: List['PythonImport'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._path = path
        self._classes = self.resolve_objects(PythonClass, classes)
        self._functions = self.resolve_objects(PythonFunction, functions)
        self._imports = self.resolve_objects(
            PythonImport, imports, key='_module'
        )

    @property
    def classes(self):
        return self._classes

    @property
    def functions(self):
        return self._functions

    @property
    def imports(self):
        return self._imports

    @classmethod
    def from_filepath(cls, filepath: Text):
        source = File.from_file(filepath)
        ast = AstParser().parse_module(filepath)
        module = cls(
            name=ast['module'],
            path=ast['file'],
            classes=ast['classes'],
            functions=ast['functions'],
            imports=ast['imports'],
            ast=ast,
        )
        return module

    @classmethod
    def from_package(cls, package: Text):
        modules = []
        ast_modules = AstParser().parse_package(package)
        for ast in ast_modules:
            mod = cls(
                name=ast['module'],
                path=ast['file'],
                classes=ast['classes'],
                functions=ast['functions'],
                imports=ast['imports'],
                ast=ast,
            )
            modules.append(mod)
        return modules


class PythonClass(NamedNode):
    """
    # Class

    ## Fields
     docstring
     bases [{type: str, data:}]
     - name
     - attr
     - call
     methods []
     classes []
    """

    def __init__(
        self,
        docstring: Text = None,
        bases: List['PythonBase'] = None,
        methods: List['PythonFunction'] = None,
        classes: List['PythonClass'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._docstring = docstring
        self._bases = bases
        self._methods = self.resolve_objects(PythonMethod, methods)
        self._classes = self.resolve_objects(PythonClass, classes)

    @property
    def docstring(self):
        return self._docstring

    @property
    def bases(self):
        return self._bases

    @property
    def methods(self):
        return self._methods

    @property
    def classes(self):
        return self._classes


class PythonFunction(NamedNode):
    """
    # Function

    ## Fields
    - docstring str
    - args []
    - kwargs {k: v}
    - decorators []
    """

    def __init__(
        self,
        docstring: Text = None,
        pargs: List['PythonArgument'] = None,
        pkwargs: List['PythonKeywordArgument'] = None,
        decorators: List['PythonDecorator'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._docstring = docstring
        self._args = self.resolve_objects(PythonArgument, pargs)
        self._kwargs = self.resolve_objects(PythonKeywordArgument, pkwargs)
        self._decorators = self.resolve_objects(PythonDecorator, decorators)
        self._is_staticmethod = False
        self._is_classmethod = False
        self._is_property = False
        self._is_property_setter = False
        if self._decorators:
            for d in self._decorators.data.values():
                if d.name == 'staticmethod':
                    self._is_staticmethod = True
                elif d.name == 'classmethod':
                    self._is_classmethod = True
                elif d.name == 'property':
                    self._is_property = True
                elif re.match(r'\w+\.setter', d.name):
                    self._is_property_setter = True

    @property
    def docstring(self):
        return self._docstring
    
    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def decorators(self):
        return self._decorators

    @property
    def is_classmethod(self):
        return self._is_classmethod
    
    @property
    def is_staticmethod(self):
        return self._is_staticmethod

    @property
    def is_property(self):
        return self._is_property

    @property
    def is_property_setter(self):
        return self._is_property_setter



class PythonMethod(PythonFunction):
    pass


class PythonImport(BaseNode):
    """
    # Import
    type = import

    ## Fields
    # module
    # alias
    """

    def __init__(
        self,
        type: Text,
        module: Text,
        alias: Text = None,
        objects: List[Dict] = None
    ):
        self._type = type
        self._module = module
        self._alias = alias
        self._objects = objects


class PythonImportFrom(BaseNode):
    """
    # Import From
    type = from

    ## Fields
    - module
    - name
    - alias
    - targets [{name, alias}]
    """

    def __init__(self, type: Text, module: Text, targets: List[Dict]):
        self._module = module
        self._targets = targets


class PythonDecorator(NamedNode):
    """
    # Decorator

    ## Fields
    - args
    - kwargs
    """

    def __init__(
        self,
        fargs: List['PythonArgument'] = None,
        fkwargs: List['PythonKeywordArgument'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._args = fargs
        self._kwargs = fkwargs


class PythonCall(NamedNode):
    """
    # Call

    ## Fields
    - decorators
    - args
    - kwargs
    """

    def __init__(
        self,
        decorators: List['PythonDecorator'] = None,
        pargs: List['PythonArgument'] = None,
        pkwargs: List['PythonKeywordArgument'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._decorators = self.resolve_objects(PythonDecorator, decorators)
        self._args = self.resolve_objects(PythonArgument, pargs)
        self._kwargs = self.resovle_objects(PythonKeywordArgument, pkwargs)


class PythonAttribute(NamedNode):
    """
    # Attribute

    ## Fields
    - value
    - attr
    """

    def __init__(self, value: Text):
        self._value = value


class PythonArgument(NamedNode):
    """
    # Argument

    ## Fields
    - value
    """
    pass


class PythonKeywordArgument(BaseNode):
    """
    # Keyword Argument

    ## Fields
    - key
    - value
    """

    def __init__(self, key: Text, value=None):
        self._key = key
        self._value = value
