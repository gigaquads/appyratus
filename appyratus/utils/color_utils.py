import math
import random
import re
# webcolors is apparently dated.
# only 138 colors listed but says 140 on
# https://www.w3schools.com/colors/colors_names.asp
from typing import Text

import webcolors

from colormath.color_conversions import convert_color
from colormath.color_objects import (
    sRGBColor,
    xyYColor,
)


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
    def closest_name(cls, value):
        """
        # Closest Color
        Using the provided color, get the closest web color name
        """
        value = cls.detect_rgb(value)
        min_colors = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - value[0])**2
            gd = (g_c - value[1])**2
            bd = (b_c - value[2])**2
            min_colors[(rd + gd + bd)] = name
        return min_colors[min(min_colors.keys())]

    @classmethod
    def get_name(cls, value):
        try:
            closest_name = actual_name = webcolors.rgb_to_name(value)
        except ValueError:
            closest_name = cls.closest_color(value)
            actual_name = None
        return actual_name, closest_name

    @classmethod
    def to_hex(cls, value):
        return sRGBColor(10, 0, 0).get_rgb_hex()

    @classmethod
    def hex2rgb(cls, value):
        hex_value = cls.detect_hex(value)
        return sRGBColor.new_from_rgb_hex(hex_value).get_upscaled_value_tuple()

    @classmethod
    def detect_hex(cls, value: Text, with_hash: bool = None):
        """
        # Parse Hex
        Parse a value for presence of a hex code
        """
        hex_format = r'^(\#?)([A-Fa-f0-9]{1,6})'
        hex_regex = re.compile(hex_format)
        value = str(value)
        result = hex_regex.match(value)
        if not result:
            return
        hex_hash, hex_value = result.groups()
        hex_len = len(hex_value)
        if with_hash is not None:
            if not with_hash:
                hex_hash = ''
            elif with_hash and not hex_hash:
                hex_hash = '#'
        if hex_len != 6:
            hex_value = (hex_value * math.ceil(6 / hex_len))[0:6]
        return hex_hash + hex_value

    @classmethod
    def detect_rgb(cls, value):
        """
        # Detect RGB
        Detect an RGB color type by the given value 
        - a list with the length of 3, then it is considered RGB
        - a list with the length of 2, then it is considered XY
        - a string then it is considered hex
        - a string that is not hex is considered a webcolor
        """
        rgb = None
        if isinstance(value, (list, tuple)):
            if len(value) == 3:
                rgb = value
            if len(value) == 2:
                xy = cls.detect_xy(value)
                rgb = cls.xy2rgb(xy)
        elif isinstance(value, str):
            hex_value = cls.detect_hex(value)
            if not hex_value:
                hex_value = cls.name2hex(value)
            if hex_value:
                rgb = cls.hex2rgb(hex_value)

        return rgb

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
    def xy2rgb(cls, value):
        rgb = None
        if isinstance(value, (list, tuple)):
            if len(value) == 3:
                rgb = value
            elif len(value) == 2:
                xy = xyYColor(*value, 0)
                srgb = convert_color(xy, sRGBColor)
                rgb = srgb.get_upscaled_value_tuple()
        return rgb

    @classmethod
    def detect_xy(cls, value):
        rgb = None
        xy = None
        if isinstance(value, (list, tuple)):
            if len(value) == 3:
                rgb = sRGBColor(*value)
            elif len(value) == 2:
                xy = value
        elif isinstance(value, str):
            # value string is one of two things here: a hex value, or a color
            # name which will be translated into hex
            hex_value = cls.detect_hex(value)
            if not hex_value:
                hex_value = cls.name2hex(value)
            if hex_value:
                rgb = cls.hex2rgb(hex_value)

        if rgb:
            if isinstance(rgb, sRGBColor):
                pass
            else:
                rgb = sRGBColor(*rgb)
            xyy = convert_color(rgb, xyYColor)
            xy = [xyy.xyy_x, xyy.xyy_y]
        return xy

    @classmethod
    def random_hex(cls):
        return cls.detect_hex(hex(random.randrange(1 << 32))[2:])


class Color(object):

    def __init__(self, value):
        self._value = value
        self._hex = None
        self._rgb = None
        self._xy = None

    @classmethod
    def detect(cls, value):
        """
        Possible formats
        - name, web name, (CornflowerBlue)
        - hex, hexadecimal (#AABBCC)
        - rgb, tuple (R,G,B)
        - xy, list pair [x, y]
        """
        pass

    @property
    def hex(self):
        if not self._hex:
            self._hex = ColorUtils.detect_hex(self._value)
        return self._hex

    @property
    def rgb(self):
        if not self._rgb:
            self._rgb = ColorUtils.detect_rgb(self._value)
        return self._rgb

    @property
    def xy(self):
        if not self._xy:
            self._xy = ColorUtils.detect_xy(self._value)
        return self._xy


class ColorType(object):
    pass


class RgbColor(ColorType):
    pass


class HexColor(ColorType):
    pass


class XyColor(ColorType):
    pass


class WebNameColor(ColorType):
    pass
