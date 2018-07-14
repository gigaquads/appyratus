import ipdb

from .subparser import Subparser

console_subparser = Subparser(
    name='console',
    help='invoke the interactive console',
    defaults={'action': 'console'}
)


class ConsoleProgMixin(object):
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
            'print("{}")'.format(self.tagline
                                 ),    #globals=dict(app=self.app())
        )

    def display_console_welcome(self):
        """
        Display a welcome message
        """
        print('Welcome to {} console'.format(self.__class__.__name__))
