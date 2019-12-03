from typing import Text

from appyratus.test import (
    BaseTests,
    mark,
)
from appyratus.utils import PathUtils


@mark.unit
class TestPathUtils(BaseTests):

    @property
    def klass(self):
        return PathUtils

    @mark.params('path, file_name', [
        ('', ''),
    ])
    def test_get_file_name(self, path: Text, file_name: Text):
        pass

    @mark.params('path, name', [
        ('/path/to/l33t', 'l33t'),
        ('/path/to/l33t.3p0', 'l33t'),
        ('/path/to/.l33t', '.l33t'),
        ('', ''),
        ('', ''),
        ('', ''),
    ])
    def test_get_name(self, path: Text, name: Text):
        assert name == self.klass.get_name(path) 

    @mark.params('path, extension', [
        ('/l33t', ''),
        ('/l33t.3p0', '3p0'),
        ('/.3p0', ''),
        ('', ''),
    ])
    def test_get_extension(self, path: Text, extension: Text):
        assert extension == self.klass.get_extension(path)

    @mark.params('path, dir_name', [
        ('/l33t/path', 'l33t'),
        ('/l33t/path/', 'l33t'),
    ])
    def test_get_dir_name(self, path: Text, dir_name: Text):
        assert dir_name == self.klass.get_dir_name(path)

    @mark.params('path, dir_path', [
        ('/my/l33t/path', '/my/l33t/path'),
        ('/my/l33t/path/', '/my/l33t/path/'),
    ])
    def test_get_dir_path(self, path: Text, dir_path: Text):
        assert dir_path == self.klass.get_dir_path(path)

    @mark.params('path, extension, new_path', [
        ('/my/l33t.txt', 'jpg', '/my/l33t.jpg'),
    ])
    def test_replace_extension(self, path: Text, extension: Text, new_path: Text):
        assert new_path == self.klass.replace_extension(path, extension)

    @mark.params('path, exists', [
        ('', ''),
    ])
    def test_exists(self, path: Text, exists: bool):
        pass

    @mark.params('path, paths', [
        ('', ''),
    ])
    def test_join(self, path: Text, paths):
        pass

    @mark.params('path, depth, file_ext', [
        ('', '', ''),
    ])
    def test_get_nodes(self, path: Text, depth: int, file_ext: Text):
        pass
