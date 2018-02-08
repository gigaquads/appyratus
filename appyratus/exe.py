import os
import subprocess


def sys_exec(command, capture=None):
    """
    Run a command in a subproces, output goes to STDOUT
    Or run a command and capture it's output
    """
    if not capture:
        return subprocess.call(command.split())
    else:
        return os.popen(command).read().rstrip()


def safe_sys_exec(command, stdout=None):
    print("Executing: {}".format(command))
    pass


def resolve_bin(bin_file):
    """
    Resolve bin path
    """
    return sys_exec('/usr/bin/env which {}'.format(bin_file), capture=True)
