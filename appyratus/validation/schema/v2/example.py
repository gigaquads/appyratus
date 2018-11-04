import json

from typing import Type
from copy import deepcopy
from pprint import pprint

from .fields import *
from .schema import Schema


class UserSchema(Schema):

    class AccountSchema(Schema):
        name = String()

    age = Int(source='age_int')
    gender = String()
    name = String(required=True)
    t = Timestamp()
    account = AccountSchema()
    accounts = List(AccountSchema())
    numbers = List(Int())
    more_numbers = List(Int())
    composite = FormatString(default='{age}:{personality}')
    personality = String(required=True, default=lambda: 'INTP')
    my_things = Nested({'a': String(), 'b': Int()})


schema = UserSchema()
data, errors = schema.process({
    'age_int': 1,
    'gender': 'M',
    't': '124',
    'account': {'name': 'foo'},
    'accounts': [{'name': 'foo'}],
    'numbers': [1, 2, 'a'],
    'more_numbers': {1, 2},
    'my_things': {'a': 'a', 'b': 1},
})


print('\n# Processed Data:')
print('-' * 50)
print(json.dumps(data, indent=2))
print('\n# Errors:')
print('-' * 50)
print(json.dumps(errors, indent=2))
