from typing import Text

from appyratus.test import (
    BaseTests,
    mark,
)
from appyratus.utils.path_utils import PathUtils


@mark.unit
class TestPathUtils(BaseTests):

    @property
    def klass(self):
        return PathUtils

    @mark.parametrize(
        'path, file_name', [
            ('/too/l33t', 'l33t'),
            ('/too/l33t.3p0', 'l33t.3p0'),
            ('/path/to/.l33t', '.l33t'),
            ('/l33t.tar.gz', 'l33t.tar.gz'),
        ]
    )
    def test_get_file_name(self, path: Text, file_name: Text):
        assert file_name == self.klass.get_file_name(path)

    @mark.parametrize(
        'path, name', [
            ('/path/to/l33t', 'l33t'),
            ('/path/to/l33t.3p0', 'l33t'),
            ('/path/to/.l33t', '.l33t'),
            ('/l33t.tar.gz', 'l33t.tar'),
        ]
    )
    def test_get_name(self, path: Text, name: Text):
        assert name == self.klass.get_name(path)

    @mark.parametrize('path, extension', [
        ('/l33t', ''),
        ('/l33t.3p0', '3p0'),
        ('/.3p0', ''),
        ('r00.de.m00', 'm00'),
    ])
    def test_get_extension(self, path: Text, extension: Text):
        assert extension == self.klass.get_extension(path)

    @mark.parametrize('path, dir_name', [
        ('/path/to/l33t', 'to'),
        ('/path/to/l33t/', 'l33t'),
    ])
    def test_get_dir_name(self, path: Text, dir_name: Text):
        assert dir_name == self.klass.get_dir_name(path)

    @mark.parametrize('path, dir_path', [
        ('/my/l33t/path', '/my/l33t'),
        ('/my/l33t/path/', '/my/l33t/path'),
    ])
    def test_get_dir_path(self, path: Text, dir_path: Text):
        assert dir_path == self.klass.get_dir_path(path)

    @mark.parametrize(
        'path, extension, new_path', [
            ('/my/l33t.txt', 'jpg', '/my/l33t.jpg'),
            ('/l33t.txt', 'rar', '/l33t.rar'),
            ('r33t.bmp', 'tar.gz', 'r33t.tar.gz'),
            ('b33p.tar.bzip2', 'zip', 'b33p.tar.zip'),
        ]
    )
    def test_replace_extension(self, path: Text, extension: Text, new_path: Text):
        assert new_path == self.klass.replace_extension(path, extension)

    @mark.skip('need fs')
    @mark.parametrize('path, exists', [
        ('', ''),
    ])
    def test_exists(self, path: Text, exists: bool):
        pass

    @mark.parametrize(
        'path, paths, join_path', [
            ('/r00t', 't00t', '/r00t/t00t'),
            ('b00t', 'sc00t', 'b00t/sc00t'),
            ('/b00p', '/m00t', '/m00t'),
            ('/p00t', './d00t', '/p00t/./d00t'),
        ]
    )
    def test_join(self, path: Text, paths, join_path: Text):
        assert join_path == self.klass.join(path, paths)

    @mark.parametrize(
        'path, split_path, separator', [
            ('/r00t/d0g', ['r00t', 'd0g'], None),
            ('/r00t/d0g/j34h', ['r00t', 'd0g', 'j34h'], None),
            ('r00t/d0g', ['r00t', 'd0g'], None),
            (':r00t:d0g:', ['r00t', 'd0g', ''], ':'),
            (':r00t:d0g:', [':r00t:d0g:'], '-'),
        ]
    )
    def test_split(self, path: Text, split_path: Text, separator):
        assert split_path == self.klass.split(path, separator)

    @mark.parametrize(
        'path, expanded_path', [
            ('~/hello', '/home/jeff/hello'),
            ('/home/jeff/goodbye', '/home/jeff/goodbye'),
        ]
    )
    def test_expand_path(self, path: Text, expanded_path: Text):
        assert self.klass.expand_path(path) == expanded_path

    @mark.skip('need fs')
    @mark.parametrize('path, depth, file_ext', [
        ('', '', ''),
    ])
    def test_get_nodes(self, path: Text, depth: int, file_ext: Text):
        pass
