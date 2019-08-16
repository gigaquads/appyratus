from typing import Text
import os
import importlib
import traceback
import ast

from typing import List, Dict


class AstParser(object):
    def parse_string(self, value: str) -> List[Dict]:
        module_ast = self._load_ast_from_source(value)
        return self._parse_node_Module(module_ast)

    def parse_package(self, pkg: str) -> List[Dict]:
        paths = self._get_python_filepaths(pkg)
        results = []
        for file_path, module_path in paths.items():
            data = self.parse_module(file_path, module_path)
            if data is not None:
                results.append(data)
        return results

    def parse_module(self, file_path, module_path: Text = None) -> Dict:
        if not module_path:
            module_path = os.path.splitext(os.path.basename(file_path))[0]
        data = {
            'module': module_path,
            'file': file_path,
            'classes': [],
            'functions': [],
            'imports': [],
            'ast': None,
        }
        try:
            root = self._load_ast_from_source(file_path)
            if root is not None:
                data.update(self._parse_node_Module(root))
            data['ast'] = root
            return data
        except:
            traceback.print_exc()
            return None

    def _load_ast_from_source(self, source):
        try:
            return ast.parse(source)
        except:
            traceback.print_exc()    # log this?

    def _load_ast_from_filepath(self, filepath):
        with open(filepath) as fin:
            source = fin.read()
            return self._load_ast_from_source(source)
        return None

    def _extract_string_value(self, node):
        if isinstance(node, str):
            return node
        if isinstance(node, ast.Attribute):
            return self._extract_string_value(node.value)
        if isinstance(node, ast.Str):
            return node.s
        if isinstance(node, ast.NameConstant):
            return str(node.value)
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.arg):
            return node.arg
        if isinstance(node, ast.keyword):
            return node.arg
        if isinstance(node, (ast.List, ast.Tuple)):
            return [self._extract_string_value(x) for x in node.elts]
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Invert):
            # There are no known attributes that will return the tilde
            return '~'
        if isinstance(node, ast.UnaryOp):
            # There are other types of Unary op, such as Not, UAdd, and USub, but
            # they have not occurred yet
            if isinstance(node.op, ast.Invert):
                return (
                    self._extract_string_value(node.op),
                    self._extract_string_value(node.operand)
                )

        raise ValueError(str(node))

    def _parse_node_Module(self, module_node):
        results = {
            'ast': module_node,
            'classes': [],
            'functions': [],
            'imports': [],
        }
        for node in module_node.body:
            if isinstance(node, ast.ClassDef):
                results['classes'].append(self._parse_node_ClassDef(node))
            elif isinstance(node, ast.FunctionDef):
                results['functions'].append(self._parse_node_FunctionDef(node))
            elif isinstance(node, ast.ImportFrom):
                results['imports'].append(self._parse_node_ImportFrom(node))
            elif isinstance(node, ast.Import):
                results['imports'].extend(self._parse_node_Import(node))

        return results

    def _parse_node_ClassDef(self, class_def):
        bases = []
        for x in class_def.bases:
            if isinstance(x, ast.Name):
                bases.append({'type': 'name', 'data': {'name': x.id}})
            elif isinstance(x, ast.Attribute):
                bases.append(
                    {
                        'type': 'attribute',
                        'data': self._parse_node_Attribute(x),
                    }
                )
            elif isinstance(x, ast.Call):
                bases.append({'type': 'call', 'data': self._parse_node_Call(x)})
            else:
                raise ValueError()

        return {
            'ast': class_def,
            'lineno': class_def.lineno,
            'name': class_def.name,
            'docstring': ast.get_docstring(class_def),
            'bases': bases,
            'methods':
                [
                    self._parse_node_FunctionDef(x) for x in class_def.body
                    if isinstance(x, ast.FunctionDef)
                ],
            'classes':
                [
                    self._parse_node_ClassDef(x) for x in class_def.body
                    if isinstance(x, ast.ClassDef)
                ]
        }

    def _parse_node_Import(self, node):
        items = []

        for x in node.names:
            if isinstance(x, ast.alias):
                items.append(
                    {
                        'type': 'import',
                        'lineno': node.lineno,
                        'module': x.name,
                        'alias': x.asname,
                        'ast': x,
                    }
                )
            else:
                raise ValueError(str(x))

        return items

    def _parse_node_ImportFrom(self, node):
        return {
            'ast': node,
            'type': 'from',
            'lineno': node.lineno,
            'module': node.module,
            'objects':
                [{
                    'name': alias.name,
                    'alias': alias.asname,
                } for alias in node.names],
        }

    def _parse_node_Call(self, node):
        return {
            'name': node.name if hasattr(node, 'name') else node.func.id,
            'lineno': node.lineno,
            'decorators':
                (
                    self._parse_decorator_list(node.decorator_list)
                    if hasattr(node, 'decorator_list') else []
                ),
            'args': self._parse_args(node.args),
            'kwargs': self._parse_kwargs(node.args),
        }

    def _parse_node_Attribute(self, node):
        return {
            'object': self._extract_string_value(node.value),
            'attr': self._extract_string_value(node.attr)
        }

    def _parse_decorator_list(self, decorator_list):
        decorators = []

        for x in decorator_list:
            item = {
                'name': None,
                'lineno': x.lineno,
                'args': [],
                'kwargs': [],
                'ast': x,
            }
            decorators.append(item)

            if isinstance(x, ast.Attribute):
                # like "@my_property.setter"
                data = self._parse_node_Attribute(x)
                item['name'] = '{}.{}'.format(data['object'], data['attr'])
            elif isinstance(x, ast.Call):
                # like "@my_func(arg1, arg2)"
                if isinstance(x.func, (ast.Name, ast.Call)):
                    name = x.func.id
                elif isinstance(x.func, ast.Attribute):
                    data = self._parse_node_Attribute(x.func)
                    name = '{}.{}'.format(data['object'], data['attr'])
                item['name'] = name
                item['args'] = [self._extract_string_value(arg) for arg in x.args]
                item['kwargs'] = [
                    {
                        'key': self._extract_string_value(arg.arg),
                        'value': self._extract_string_value(arg.value)
                    } for arg in x.keywords
                ]
            else:
                item['name'] = x.id

        return decorators

    def _parse_node_FunctionDef(self, node):
        decorators = self._parse_decorator_list(node.decorator_list)
        args = self._parse_args(node.args)
        results = {
            'name': node.name,
            'lineno': node.lineno,
            'docstring': ast.get_docstring(node),
            'args': args,
            'kwargs': self._parse_kwargs(node.args, len(args)),
            'decorators': decorators,
            'ast': node,
        }
        return results

    def _parse_args(self, arguments):
        return [
            {
                'key': arg.arg,
                'index': idx,
            } for idx, arg in enumerate(arguments.args)
        ]

    def _parse_kwargs(self, arguments, index):
        kwarg_count = len(arguments.defaults)
        return [
            {
                'key': arg.arg,
                'value': self._extract_string_value(val),
                'index': index + 1 + idx,
            } for idx, (arg, val) in
            enumerate(zip(arguments.args[-kwarg_count:], arguments.kw_defaults))
        ]

    @staticmethod
    def _get_python_filepaths(pkg_name: str) -> List[str]:
        pkg = importlib.import_module(pkg_name)
        pkg_filepath = os.path.dirname(pkg.__file__)
        file_paths = {}

        # if pkg_name is actually the name of a module, not contained in a
        # package, just return a single filepath for the module file. do not
        # recurse on its parent directory.
        if '__init__.py' not in os.listdir(pkg_filepath):
            return {pkg.__file__: pkg_name}

        for dir_path, subdir_names, file_names in os.walk(pkg_filepath):
            for k in file_names:
                if k.endswith('.py'):
                    file_path = os.path.join(dir_path, k)
                    module_path = (pkg_name +
                                   file_path[len(pkg_filepath):]).replace('/', '.')[:-3]
                    file_paths[file_path] = module_path

        return file_paths
