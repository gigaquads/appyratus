import ipdb

from .subparser import Subparser


class ConsoleSubparser(Subparser):
    """
    Console Subparser
    """
    name = 'console'
    help = 'invoke the interactive console'
    defaults = dict(action='console')


class ConsoleProgMixin(object):

    console_subparser = ConsoleSubparser()
    """
    Console subparser
    """

    def console(self):
        """
        Console action
        """
        self.enter_console()

    def enter_console(self):
        """
        Enter a simple console, for interactive access to your applications
        code, provided by ipdb
        """
        self.display_console_welcome()
        ipdb.run(
            'print("{}")'.format(self.tagline), globals=dict(app=self.app())
        )

    def display_console_welcome(self):
        """
        Display a welcome message
        """
        print('Welcome to {} console'.format(self.__class__.__name__))
