from appyratus.test import mark, BaseTests
from appyratus.cli import Parser, CliProgram, Subparser, Arg

from collections import namedtuple


@mark.unit
class TestParserUnit(BaseTests):
    @property
    def klass(self):
        return Parser

    @property
    def fixtures(self):
        return {
            'arg': {
                'args': [Arg(name='My Name', flags=('-n', '--name'))]
            },
            'args': {
                'args': [
                    Arg(name='My Name', flags=('-m', '--my-name')),
                    Arg(name='Your Name', flags=('-y', '--your-name'))
                ]
            }
        }

    def test__will_initialize(self):
        parser = self.instance(fixture='arg')
        assert isinstance(parser, self.klass)
        assert isinstance(parser._args, list)
        assert len(parser._args) == 1
        assert isinstance(parser._subparsers, list)
        assert len(parser._subparsers) == 0

    def test__will_build(self):
        with self.mock(method='build_parser') as build_parser, self.mock(
            method='build_subparser'
        ) as build_subparser, self.mock(
            method='build_subparsers'
        ) as build_subparsers, self.mock(
            method='parse_cli_args', return_value=({}, [])
        ) as parse_cli_args, self.mock(method='build_args') as build_args:
            parser = self.instance(fixture='arg')
            parser.build()
            build_parser.assert_called()
            build_subparser.assert_called()
            build_subparsers.assert_called()
            parse_cli_args.assert_called()
            build_args.assert_called()

    def test__will_build_args(self):
        parser = self.instance(fixture='args')
        with self.mock('appyratus.cli.Arg.build', raw=True) as arg_build:
            parser.build_args()
            arg_build.assert_called()


class TestCliProgramUnit(BaseTests):
    pass
