import time
import os
import shlex
import subprocess
import sys

from threading import current_thread
from datetime import timedelta
from typing import Text, Union

from appyratus.files import File
from appyratus.utils.path_utils import PathUtils
from appyratus.utils.time_utils import TimeUtils


class SysUtils(object):
    sequence = 0

    @classmethod
    def sys_exec(
        cls,
        command: Text,
        capture=None,
        merge_streams=False,
        write_command=False
    ) -> Text:
        """
        Run a command in a subprocess output goes to STDOUT

        - capture, capture STDOUT of the command and return
        - merge_streams, merge the STDERR stream into the STDOUT stream
        - write_command, write the command to a shell script and call that
          script instead.  useful when dealing with a command you want to call
          without parsing it through shlex
        """
        if write_command:
            command = cls.write_command(command)

        command_args = shlex.split(command, comments=True)
        if capture:
            if merge_streams:
                exec_kwargs = {'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT}
            else:
                exec_kwargs = {'capture_output': True}
            res = subprocess.run(command_args, **exec_kwargs)
            value = res.stdout.decode('utf-8').rstrip()
            return value
        else:
            res = subprocess.call(command_args)
            return res

    @classmethod
    def safe_main(cls, main_callable, debug_level: int = None) -> object:
        """
        Call
        """
        try:
            return main_callable()
        except Exception as exc:
            SysUtils.raise_exception(exc, level=debug_level)

    @classmethod
    def raise_exception(cls, exception, level: int = 1):
        # NOTE: ultratb is imported locally to avoid cyclic imports with, say,
        # ipdb or anything else that has an IPython dependency.
        from IPython.core import ultratb 

        if level == 1:
            sys.excepthook = ultratb.ColorTB(tb_offset=-5)
        if level == 2:
            sys.excepthook = ultratb.ColorTB()
        elif level == 3:
            sys.excepthook = ultratb.VerboseTB()
        raise exception

    @classmethod
    def resolve_bin(cls, bin_file: Text):
        """
        Resolve bin path
        """
        return SysUtils.sys_exec('/usr/bin/env which {}'.format(bin_file), capture=True)

    @classmethod
    def write_command(cls, command, path: Text = None):
        path = path if path else '/tmp'
        timestamp = TimeUtils.utc_timestamp()
        cls.sequence += 1
        tmp_file = f'appyratus-sys-exec-{timestamp}-{cls.sequence}.sh'
        file_path = PathUtils.join(path, tmp_file)
        File.write(file_path, f"#!/usr/bin/env bash\n{command}")
        PathUtils.make_executable(file_path, user=True)
        return file_path

    @classmethod
    def sleep(cls, interval: Union[float, timedelta]):
        if isinstance(interval, timedelta):
            time.sleep(interval.total_seconds())
        else:
            time.sleep(interval)

    @classmethod
    def set_thread_name(cls, name: Text):
        current_thread().name = name