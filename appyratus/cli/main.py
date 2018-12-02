import sys

from IPython.core import ultratb


def safe_main(main_callable, debug_level: int=None):
    """
    Call
    """
    try:
        main_callable()
    except Exception as exc:
        show_exception(exc, level=debug_level)


def show_exception(exception, level: int=None):
    if not level:
        print('!!! An error occured, {}'.format(exception))
        return
    elif level == 1:
        sys.excepthook = ultratb.ColorTB()
    elif level == 2:
        sys.excepthook = ultratb.VerboseTB()
    raise exception
