from typing import Text

from appyratus.test import (
    BaseTests,
    mark,
)
from appyratus.utils.color_utils import ColorUtils

HEX_COLORS = []
RGB_COLORS = []
XY_COLORS = []
WEB_COLORS = []


@mark.unit
class TestColorUtils(BaseTests):

    @classmethod
    def __klass__(cls):
        return ColorUtils

    @mark.parametrize(
        'color, closest_name', [
            ('ffffff', 'white'),
            ('fefefe', 'white'),
            ('000000', 'black'),
            ('000001', 'black'),
            ('fcfcfc', 'snow'),
            ('fffafa', 'snow'),
        ]
    )
    def test_closest_name(self, color, closest_name):
        assert closest_name == self.klass.closest_name(color)

    @mark.skip('needs work')
    @mark.parametrize('color, name', [
        ('ffcc00', 'orange'),
    ])
    def test_get_name(self, color, name):
        assert name == self.klass.get_name(color)

    @mark.skip('needs work')
    @mark.parametrize('color, hex_color', [
        ((1, 1, 1), 'ffffcc'),
    ])
    def test_to_hex(self, color, hex_color):
        assert hex_color == self.klass.to_hex(color)

    @mark.parametrize(
        'color, rgb_color', [
            ('ffffff', (255, 255, 255)),
            ('#000000', (0, 0, 0)),
            ('bed', (190, 219, 237)),
            ('df', (223, 223, 223)),
        ]
    )
    def test_hex2rgb(self, color, rgb_color):
        assert rgb_color == self.klass.hex2rgb(color)

    @mark.parametrize(
        'color, hex_color, with_hash', [
            ('ffffff', 'ffffff', None),
            ('#000000', '#000000', None),
            ('bed', 'bedbed', None),
            ('df', 'dfdfdf', None),
            ('#d', 'dddddd', False),
            (123, '#123123', True),
            ('#b33f', '#b33fb3', None),
        ]
    )
    def test_detect_hex(self, color: Text, hex_color, with_hash: bool):
        assert hex_color == self.klass.detect_hex(color, with_hash=with_hash)

    @mark.parametrize('color, hex_color', [
        ('bLaCk', '000000'),
        ('Red', 'ff0000'),
        ('orange', 'ffa500'),
    ])
    def test_name2hex(self, color: Text, hex_color: Text):
        assert hex_color == self.klass.name2hex(color)

    @mark.parametrize(
        'color, xy_color', [
            ([0, 0, 0], [0.0, 0.0]),
            ((255, 255, 255), [0.3127116346585353, 0.3290082765355151]),
        ]
    )
    def test_detect_xy(self, color, xy_color):
        assert xy_color == self.klass.detect_xy(color)

    @mark.parametrize(
        'xy_color, rgb_color', [
            ([0.0, 0.0], (0, 0, 0)),
            ([0.0, 0], (0, 0, 0)),
            ([.13, .37], (0, 0, 0)),
            ([1, 2], (0, 0, 0)),
        ]
    )
    def test_xy2rgb(self, xy_color, rgb_color):
        assert rgb_color == self.klass.xy2rgb(xy_color)

    def test_random_hex(self):
        max_samples = 10
        raw_samples = [self.klass.random_hex() for i in range(0, max_samples - 1)]
        unique_samples = set(raw_samples)
        assert len(unique_samples) > max_samples / 2
