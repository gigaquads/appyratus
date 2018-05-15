import re
import codecs

AN_EMPTY_STRING = ''
""" The least amount of text the transform normalizer will return """


class TextTransform(object):
    """
    Transform Text in various ways
    """

    @classmethod
    def normalize(cls, value):
        """
        Normalize a value a word-only character string with spaces
        - Split up possible class names
        - Replace all non-word characters with spaces
        - Reduce spacing
        """
        if not value:
            return AN_EMPTY_STRING
        # attempt to convert it to a string when it is not one
        if not isinstance(value, str):
            value = str(value)
        value = cls.split_class_name(value)
        value = cls.non_word_to_space(value)
        value = cls.reduce_spacing(value)
        return value

    @classmethod
    def split_class_name(cls, value):
        """
        Split a class name into readable parts
        - Replace all cases of "Az" with " Az"
        - Replace all cases of "aZ" with "a Z"
        - Strip the remaining space

        With an example provided, it has the following transformations:
        "SaveAPlant" -> " SaveA Plant" -> " Save A Plant" -> "Save A Plant"

        This will additionally preserve constants
        """
        value = re.sub(r'([A-Z][a-z])', r' \1', value)
        value = re.sub(r'([a-z])([A-Z])', r'\1 \2', value)
        return value.strip()

    @classmethod
    def non_word_to_space(cls, value):
        return re.sub(r'[\W_]', ' ', value)

    @classmethod
    def reduce_spacing(cls, value):
        return re.sub(r'\s+', ' ', value).strip()

    @classmethod
    def snake(cls, value):
        """
        Snake case `such_as_this`
        """
        return re.sub(r'\s', r'_', cls.normalize(value)).lower()

    @classmethod
    def title(cls, value):
        """
        Title `Such As This`
        """
        return str.title(cls.normalize(value))

    @classmethod
    def dash(cls, value):
        """
        Dash case `such-as-this`
        """
        return re.sub(r'\s', r'-', cls.normalize(value)).lower()

    @classmethod
    def camel(cls, value):
        """
        Camel case, `SuchAsThis`
        """
        return re.sub(r'\s', '', cls.title(value))

    @classmethod
    def dot(cls, value):
        """
        Dot notation, `such.as.this`
        """
        return cls.separator(value=cls.normalize(value), separator='.')

    @classmethod
    def unbound(cls, value):
        """
        Unbound, void of all separation, `suchasthis`
        """
        return cls.separator(value=cls.normalize(value), separator='')

    @classmethod
    def reverse(cls, value):
        """
        Reversed, `siht sa hcus`
        """
        return value[::-1]

    @classmethod
    def hex(cls, value):
        """
        Hex, `b'737563682061732074686973'`
        """
        return codecs.encode(value.encode('ascii'), 'hex')

    @classmethod
    def words(cls, value, separator=None) -> list:
        """
        Words, `['such', 'as', 'this']`
        """
        if not separator:
            separator = ' '
        return value.split(separator)

    @classmethod
    def separator(cls, value, separator=None):
        if separator is None:
            return
        return re.sub(r'\s', r"{}".format(separator), value)