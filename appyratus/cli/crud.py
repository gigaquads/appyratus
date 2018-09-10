from .subparser import Subparser

from .arg import Arg


class CrudSubparser(Subparser):
    @staticmethod
    def subparsers():
        return [Subparser(name='create', args=[Arg(flags=('-n', 'name'))])]
