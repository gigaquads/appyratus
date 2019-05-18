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

    def build_nodes(
        self, node_class: 'BaseNode', data: List, key: Text = None
    ):
        if not key:
            key = 'name'
        if not data:
            return []
        sorted_data = sorted(data, key=lambda x: (x.get(key) or ''))
        return DictObject.from_list(key, [node_class(**d) for d in sorted_data])


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


class PythonPackage(NamedNode):
    """
    # Python Package
    """

    def __init__(self, modules: List['PythonModule'] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        modules = sorted(modules, key=lambda x: x['module'])
        self._modules = {
            m['module']: PythonModule(name=m['module'], **m)
            for m in modules
        }

    @property
    def modules(self):
        return self._modules

    @classmethod
    def from_dotted_path(cls, package: Text):
        modules = []
        module_data = AstParser().parse_package(package)
        return cls(name=package, modules=module_data)


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
        path: Text = None,
        classes: List['PythonClass'] = None,
        functions: List['PythonFunction'] = None,
        imports: List['PythonImport'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._path = path
        self._classes = self.build_nodes(PythonClass, classes)
        self._functions = self.build_nodes(PythonFunction, functions)
        self._imports = self.build_nodes(PythonImport, imports, key='module')

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
        self._methods = self.build_nodes(PythonMethod, methods)
        self._classes = self.build_nodes(PythonClass, classes)

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
        py_args: List['PythonArgument'] = None,
        py_kwargs: List['PythonKeywordArgument'] = None,
        decorators: List['PythonDecorator'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._docstring = docstring
        self._args = self.build_nodes(PythonArgument, py_args)
        self._kwargs = self.build_nodes(PythonKeywordArgument, py_kwargs)
        self._decorators = self.build_nodes(PythonDecorator, decorators)
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
    """
    # Python Method
    This is just a Python Function
    """
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

    @property
    def module(self):
        return self._module

    @property
    def repr_values(self):
        return [f'"{self._module}"']


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
        py_args: List['PythonArgument'] = None,
        py_kwargs: List['PythonKeywordArgument'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._decorators = self.build_nodes(PythonDecorator, decorators)
        self._args = self.build_nodes(PythonArgument, py_args)
        self._kwargs = self.build_nodes(PythonKeywordArgument, py_kwargs)


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
