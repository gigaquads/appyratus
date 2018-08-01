"""
Argz
Things to adopt for command line python usage
Concepts:
- CliProgram
- Subparser
- Arg
"""

from .cli_program import CliProgram
from .subparser import Subparser
from .arg import Arg, PositionalArg, OptionalArg
from .parser import Parser
from .main import safe_main
#from .crud import crud_subparser
#from .console import console_subparser
