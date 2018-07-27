from appyratus.test import mark, BaseTests
from appyratus.cli import Parser, CliProgram, Subparser, Arg

from collections import namedtuple


@mark.unit
class TestParserUnit(BaseTests):
    @property
    def klass(self):
        return Parser

    def parser_with_arg(self):
        return self.instance(
            **{'args': [Arg(name='My Name', flags=('-n', '--name'))]}
        )

    def test__will_initialize(self):
        parser = self.parser_with_arg()
        assert isinstance(parser, self.klass)
        assert isinstance(parser._args, list)
        assert isinstance(parser._subparsers, list)

    def test__will_build(self):
        with self.mock(method='build_parser') as build_parser, self.mock(
            method='build_subparser'
        ) as build_subparser, self.mock(
            method='build_subparsers'
        ) as build_subparsers, self.mock(
            method='parse_cli_args', return_value=({}, [])
        ) as parse_cli_args, self.mock(method='build_args') as build_args:
            parser = self.parser_with_arg()
            parser.build()
            build_parser.assert_called()
            build_subparser.assert_called()
            build_subparsers.assert_called()
            parse_cli_args.assert_called()
            build_args.assert_called()

    def test__will_build_args(self):
        parser = self.parser_with_arg()
        with self.mock('appyratus.cli.Arg.build', raw=True) as arg_build:
            parser.build_args()
            arg_build.assert_called()
