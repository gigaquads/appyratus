import os
import subprocess
import sys

from typing import Text

from IPython.core import ultratb


class SysUtils(object):

    @staticmethod
    def sys_exec(command: Text, capture=None) -> Text:
        """
        Run a command in a subproces, output goes to STDOUT
        Or run a command and capture it's output
        """
        if not capture:
            return subprocess.call(command.split())
        else:
            return os.popen(command).read().rstrip()

    @staticmethod
    def safe_main(main_callable, debug_level: int=None) -> object:
        """
        Call
        """
        try:
            return main_callable()
        except Exception as exc:
            SysUtils.raise_exception(exc, level=debug_level)

    @staticmethod
    def raise_exception(exception, level: int=None):
        if not level:
            print('!!! An error occured, {}'.format(exception))
        else:
            if level == 1:
                sys.excepthook = ultratb.ColorTB()
            elif level == 2:
                sys.excepthook = ultratb.VerboseTB()
            raise exception

    @staticmethod
    def resolve_bin(bin_file: Text):
        """
        Resolve bin path
        """
        return sys_exec('/usr/bin/env which {}'.format(bin_file), capture=True)
