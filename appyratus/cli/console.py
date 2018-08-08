import ipdb

from appyratus.util import TextTransform

from .subparser import Subparser


class ConsoleSubparser(Subparser):
    def perform(self, program):
        """
        Console action
        """
        self.program_name = TextTransform.title(program.name)
        self.exit_message = program.tagline
        self.display_console_welcome()
        self.enter_console()

    def enter_console(self):
        """
        Enter a simple console, for interactive access to your applications
        code, provided by ipdb
        """
        ipdb.run(
            'print("{}")'.format(self.exit_message
                                 ),    #globals=dict(app=self.app())
        )

    def display_console_welcome(self):
        """
        Display a welcome message
        """
        print('Welcome to the {} console'.format(self.program_name))


console_subparser = ConsoleSubparser(
    name='console',
    usage='invoke the interactive console',
    defaults={'action': 'console'}
)
