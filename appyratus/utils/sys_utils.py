import os
import subprocess
import sys

from typing import Text

from IPython.core import ultratb


class SysUtils(object):

    @classmethod
    def sys_exec(cls, command: Text, capture=None) -> Text:
        """
        Run a command in a subproces, output goes to STDOUT
        Or run a command and capture it's output
        """
        if not capture:
            return subprocess.call(command.split())
        else:
            return os.popen(command).read().rstrip()

    @classmethod
    def safe_main(cls, main_callable, debug_level: int=None) -> object:
        """
        Call
        """
        try:
            return main_callable()
        except Exception as exc:
            SysUtils.raise_exception(exc, level=debug_level)

    @classmethod
    def raise_exception(cls, exception, level: int=None):
        if not level:
            print('!!! An error occured, {}'.format(exception))
        else:
            if level == 1:
                sys.excepthook = ultratb.ColorTB()
            elif level == 2:
                sys.excepthook = ultratb.VerboseTB()
            raise exception

    @classmethod
    def resolve_bin(cls, bin_file: Text):
        """
        Resolve bin path
        """
        return SysUtils.sys_exec('/usr/bin/env which {}'.format(bin_file), capture=True)
