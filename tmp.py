from argparse import ArgumentParser
from mock import Mock

m = Mock()

parser = ArgumentParser()
subparsers = parser.add_subparsers()

agroup = subparsers.add_parser('a')

command = subparsers.add_parser('b')
command.set_defaults(func=m.b)

subparsers = agroup.add_subparsers()
command = subparsers.add_parser('aa')
command.set_defaults(func=m.a.a)

command = subparsers.add_parser('ab')
command.set_defaults(func=m.a.b)

options = parser.parse_args()

print('PARSER {}'.format(parser))
print('OPTIONS {}'.format(options))
#print(options.func)
#options.func(options)
print(m.method_calls)
