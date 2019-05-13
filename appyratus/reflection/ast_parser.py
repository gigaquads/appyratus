from typing import Text
import os
import importlib
import traceback
import ast

from typing import List, Dict


class AstParser(object):
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
        }
        try:
            root = self._load_ast_from_source(file_path)
            if root is not None:
                data.update(self._parse_node_Module(root))
            return data
        except:
            traceback.print_exc()
            return None

    def _load_ast_from_source(self, filepath):
        with open(filepath) as fin:
            source = fin.read()
            try:
                return ast.parse(source)
            except:
                pass    # log this?

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

        raise ValueError(str(node))

    def _parse_node_Module(self, module_node):
        results = {
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
                bases.append(
                    {
                        'type': 'call',
                        'data': self._parse_node_Call(x)
                    }
                )
            else:
                raise ValueError()

        return {
            'name': class_def.name,
            'docstring': ast.get_docstring(class_def),
            'bases': bases,
            'methods': [
                self._parse_node_FunctionDef(x) for x in class_def.body
                if isinstance(x, ast.FunctionDef)
            ],
            'classes': [
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
                        'module': x.name,
                        'alias': x.asname,
                    }
                )
            else:
                raise ValueError(str(x))

        return items

    def _parse_node_ImportFrom(self, node):
        return {
            'type': 'from',
            'module': node.module,
            'objects': [
                {
                    'name': alias.name,
                    'alias': alias.asname,
                } for alias in node.names
            ]
        }

    def _parse_node_Call(self, node):
        return {
            'name': node.name if hasattr(node, 'name') else node.func.id,
            'decorators': (
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
                'args': [],
                'kwargs': [],
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
                item['args'] = [
                    self._extract_string_value(arg) for arg in x.args
                ]
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
        results = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'args': self._parse_args(node.args),
            'kwargs': self._parse_kwargs(node.args),
            'decorators': decorators,
        }
        return results

    def _parse_args(self, arguments):
        return [arg.arg for arg in arguments.args]

    def _parse_kwargs(self, arguments):
        return [
            {
                'key': arg.arg,
                'value': self._extract_string_value(val)
            } for arg, val in zip(arguments.kwonlyargs, arguments.kw_defaults)
        ]

    @staticmethod
    def _get_python_filepaths(pkg_name: str) -> List[str]:
        pkg = importlib.import_module(pkg_name)
        pkg_filepath = os.path.dirname(pkg.__file__)
        file_paths = {}

        for dir_path, subdir_names, file_names in os.walk(pkg_filepath):
            for k in file_names:
                if k.endswith('.py'):
                    file_path = os.path.join(dir_path, k)
                    module_path = (pkg_name + file_path[len(pkg_filepath):]
                                   ).replace('/', '.')[:-3]
                    file_paths[file_path] = module_path

        return file_paths
