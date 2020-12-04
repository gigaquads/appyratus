from typing import Text

from appyratus.test import (
    BaseTests,
    mark,
)
from appyratus.utils import TemplateUtils


@mark.unit
class TestTemplateUtils(BaseTests):

    @property
    def klass(self):
        return TemplateUtils

    def test_get_environment(self):
        env = self.klass.get_environment()()
        assert env is not None
        env2 = self.klass.get_environment()()
        assert env != env2

    @mark.params(
        'path, file_name', [
            ('{{ a }} {{ b }}', {'a', 'b'}),
            ('{% for w in wat %}{{ w }}{% endfor %}', {'wat'}),
        ]
    )
    def test_get_template_variables(self, path: Text, file_name: Text):
        assert file_name == self.klass.get_template_variables(path)
