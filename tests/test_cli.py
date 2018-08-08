from appyratus.test import mark, BaseTests
from appyratus.cli import Parser, CliProgram, Subparser, Arg

from collections import namedtuple


@mark.unit
class TestParser(BaseTests):
    @property
    def klass(self):
        return Parser

    @property
    def fixtures(self):
        return {
            'arg': {
                'args': [Arg(name='Name', flags=('-n', '--name'))]
            },
            'args': {
                'args': [
                    Arg(name='My Name', flags=('-m', '--my-name')),
                    Arg(name='Your Name', flags=('-y', '--your-name'))
                ]
            },
            'subparser': {
                'subparsers': [Subparser(name='My Subparser')]
            },
            'subparsers': {
                'subparsers': [
                    Subparser(name='My Subparser'),
                    Subparser(name='My Other Subparser'),
                ]
            },
            'subparser_with_args': {
                'subparsers': [
                    Subparser(
                        name='This Subparser',
                        args=[
                            Arg(name='this_arg', flags=(
                                '-t',
                                '-this-arg',
                            ))
                        ]
                    )
                ]
            }
        }

    def test__will_initialize(self):
        parser = self.instance(fixture='arg')
        assert isinstance(parser, self.klass)
        assert isinstance(parser._args, list)
        assert isinstance(parser._subparsers, list)

    def test__will_build(self):
        with self.mock(method='build_parser') as build_parser, self.mock(
            method='build_subparser'
        ) as build_subparser, self.mock(
            method='build_subparsers'
        ) as build_subparsers, self.mock(method='build_args') as build_args:
            parser = self.instance(fixture='subparser_with_args')
            parser.build()
            build_parser.assert_called()
            build_subparser.assert_called()
            build_subparsers.assert_called()
            build_args.assert_called()

    def test__will_build_args(self):
        parser = self.instance(fixture='args')
        with self.mock('appyratus.cli.Arg.build', raw=True) as arg_build:
            parser.build_args()
            assert arg_build.call_count == len(parser._args)

    def test__will_build_subparsers(self):
        parser = self.instance(fixture='subparser')
        with self.mock(
            'appyratus.cli.Subparser.build', raw=True
        ) as subparser_build:
            parser.build_subparsers()
            assert subparser_build.call_count == len(parser._subparsers)


@mark.unit
class TestCliProgram(BaseTests):
    @property
    def klass(self):
        return CliProgram

    def test__will_parse_cli_args(self):
        with self.mock(
            method='parse_cli_args', return_value=({}, [])
        ) as parse_cli_args:
            program = self.instance()
            program.run()
            parse_cli_args.assert_called()


class TestSubparser(BaseTests):
    @property
    def klass(self):
        return Subparser
