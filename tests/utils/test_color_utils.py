from appyratus.test import mark, BaseTests
from appyratus.utils import ColorUtils

HEX_COLORS = []
RGB_COLORS = []
XY_COLORS = []
WEB_COLORS = []



@mark.unit
class TestColorUtils(BaseTests):
    @property
    def klass(self):
        return ColorUtils

    @mark.params(
        'value, expected', [
        ]
    )
    def test__flatten(self, value, expected):
        res = self.klass.flatten(data)
        assert res == expected
