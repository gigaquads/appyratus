from appyratus.cli import CliProgram, FlagArg, PositionalArg, OptionalArg


class LameProgram(CliProgram):
    def perform(self, program):
        print(program.cli_args.data)

    def args(self):
        return [
            PositionalArg('lame'),
            FlagArg('iAmLame', default=False),
            FlagArg('youAreLame'),
            OptionalArg('weAreLame'),
        ]


lame_program = LameProgram()
lame_program.run()
