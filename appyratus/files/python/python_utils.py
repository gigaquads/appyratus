from appyratus.constants import STYLE_CONFIG

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from yapf.yapflib.yapf_api import FormatCode


class PythonUtils(object):

    @classmethod
    def to_html(cls, value):
        """
        # Python to Html
        """
        if value is None:
            return
        res = highlight(value, PythonLexer(), HtmlFormatter())
        return res

    @classmethod
    def format_python(cls, value):
        """
        Format python code
        """
        try:
            res = FormatCode(value, style_config=STYLE_CONFIG)
            res = res[0]
            if isinstance(res, tuple):
                res = res[0]
        except Exception as exc:
            from appyratus.logging import logger
            logger.error(exc)
            res = ""
        return res
