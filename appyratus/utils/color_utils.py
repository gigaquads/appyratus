import re
import webcolors
# webcolors is apparently dated.
# only 138 colors listed but says 140 on
# https://www.w3schools.com/colors/colors_names.asp
from typing import Text

from colormath.color_objects import sRGBColor, xyYColor
from colormath.color_conversions import convert_color





class ColorUtils(object):
    """
    # Color Utils
    Utility for manipulating colors

    ## Reading Material
    https://en.wikipedia.org/wiki/CIE_1931_color_space#CIE_xy_chromaticity_diagram_and_the_CIE_xyY_color_space
    https://python-colormath.readthedocs.io/en/latest/conversions.html
    https://python-colormath.readthedocs.io/en/latest/color_objects.html#xyycolor
    """

    @classmethod
    def closest_color(cls, value):
        min_colors = {}
        for key, name in webcolors.css3_hex_to_names.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - value[0])**2
            gd = (g_c - value[1])**2
            bd = (b_c - value[2])**2
            min_colors[(rd + gd + bd)] = name
        return min_colors[min(min_colors.keys())]

    @classmethod
    def get_color_name(cls, value):
        try:
            closest_name = actual_name = webcolors.rgb_to_name(value)
        except ValueError:
            closest_name = cls.closest_color(value)
            actual_name = None
        return actual_name, closest_name

    @classmethod
    def to_hex(cls, value):
        return sRGBColor.get_rgb_hex(value)

    @classmethod
    def hex2rgb(cls, value):
        return sRGBColor.new_from_rgb_hex(value)

    @classmethod
    def parse_hex(cls, value: Text):
        """
        # Parse Hex
        Parse a value for presence of a hex code
        """
        hex_format = r'^\#?([A-Fa-f0-9]{1,6})$'
        hex_regex = re.compile(hex_format)
        result = hex_regex.match(value)
        if not result:
            return
        hex_value = str(result[0])
        hex_len = len(hex_value)
        if hex_len == 2:
            hex_value = hex_value * 3
        elif hex_len == 3:
            hex_value = hex_value * 2
        else:
            pass
        return hex_value

    @classmethod
    def name2hex(cls, value: Text):
        """
        # Name2hex
        Take a color by name and attempt to convert it into hex
        """
        value = value.replace(' ', '')    # names here must not contain any spacing
        result = webcolors.name_to_hex(value)
        if not result:
            return
        return result[1:]    # remove the '#'

    @classmethod
    def detect_xy(cls, value):
        rgb = None
        xy = None
        if isinstance(value, list):
            if len(value) == 3:
                rgb = sRGBColor(*value)
            elif len(value) == 2:
                xy = value
        elif isinstance(value, str):
            # value string is one of two things here: a hex value, or a color
            # name which will be translated into hex
            hex_value = cls.parse_hex(value)
            if not hex_value:
                hex_value = cls.name2hex(value)
            if hex_value:
                rgb = cls.hex2rgb(hex_value)

        if rgb:
            xyy = convert_color(rgb, xyYColor)
            xy = [xyy.xyy_x, xyy.xyy_y]
        return xy

    @classmethod
    def random_hex(cls, value):
        return hex(random.randrange(1 << 32))[4:]


class Color(object):

    def __init__(self, value):
        self._value = value
        self._hex = None
        self._rgb = None
        self._xy = None

    @classmethod
    def detect_color(cls, value):
        """
        Possible formats
        - name, web name, (CornflowerBlue)
        - hex, hexadecimal (#AABBCC)
        - rgb, tuple (R,G,B)
        - xy, list pair [x, y]
        """
        pass

    @property
    def xy(self):
        if not self._xy:
            self._xy = self.detect_xy(self._value)
        return self._xy
