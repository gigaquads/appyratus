import re
from appyratus.files import File
from appyratus.utils import DictObject
from typing import Text, List, Dict

from .ast_parser import AstParser


class BaseNode(object):
    @property
    def repr_values(self):
        return []

    def __repr__(self):
        if self.repr_values:
            values = ','.join(self.repr_values)
        else:
            values = ''
        return f'<{self.__class__.__name__}(values)>'


class NamedNode(BaseNode):
    def __init__(self, name: Text, *args, **kwargs):
        self._name = name

    def repr_values(self):
        return ['"{self.name}"']

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
        classes: List['Class'] = None,
        functions: List['Function'] = None,
        imports: List['Import'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._path = path
        self._classes = DictObject.from_list(
            'name', [PythonClass(**c) for c in classes]
        )

        self._functions = DictObject.from_list(
            'name', [PythonFunction(**f) for f in functions]
        )
        self._imports = imports or []

    @classmethod
    def from_filepath(cls, filepath: Text):
        source = File.from_file(filepath)
        ast = AstParser().parse_module(filepath)
        mod = cls(
            name=ast['module'],
            path=ast['file'],
            classes=ast['classes'],
            functions=ast['functions'],
            imports=ast['imports']
        )
        return mod


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
        bases: List['Base'] = None,
        methods: List['Function'] = None,
        classes: List['Class'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._docstring = docstring
        self._bases = bases
        self._methods = DictObject.from_list(
            'name', [PythonMethod(**m) for m in methods]
        )
        self._classes = DictObject.from_list(
            'name', [PythonClass(**c) for c in classes]
        )


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
        fargs: List['Argument'] = None,
        fkwargs: List['KeywordArgument'] = None,
        decorators: List['Decorator'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._docstring = docstring
        self._args = fargs
        self._kwargs = fkwargs
        self._decorators = DictObject.from_list(
            'name', [PythonDecorator(**d) for d in decorators]
        )
        self._is_staticmethod = False
        self._is_classmethod = False
        self._is_property = False
        self._is_property_setter = False
        for d in self._decorators.data.values():
            if d.name == 'staticmethod':
                self._is_staticmethod = True
            elif d.name == 'classmethod':
                self._is_classmethod = True
            elif d.name == 'property':
                self._is_property = True
            elif re.match(r'\w+\.setter', d.name):
                self._is_property_setter = True


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

    def __init__(self, module: Text, alias: Text):
        self._module = module
        self._alias = alias


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

    def __init__(self, module: Text, targets: List[Dict]):
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
        fargs: List['Argument'] = None,
        fkwargs: List['KeywordArgument'] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._args = fargs
        self._kwargs = fkwargs


class PythonCall(BaseNode):
    """
    # Call

    ## Fields
    - function
    - decorators
    - args
    - kwargs
    """

    def __init__(
        self,
        function: Text,
        decorators: List['Decorator'] = None,
        args: List['Argument'] = None,
        kwargs: List['KeywordArgument'] = None
    ):
        self._function = function
        self._decorators = decorators
        self._args = args
        self._kwargs = kwargs


class PythonAttribute(BaseNode):
    """
    # Attribute

    ## Fields
    - value
    - attr
    """

    def __init__(self, name: Text, value: Text):
        self._name = name
        self._value = value


class PythonArgument(BaseNode):
    """
    # Argument

    ## Fields
    - value
    """

    def __init__(self, value: Text):
        self._value = value


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
