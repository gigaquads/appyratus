import re


OP_LOAD = 'load'
OP_DUMP = 'dump'
RECOGNIZED_OPS = {
    OP_LOAD, OP_DUMP
}

RE_EMAIL = re.compile(r'^[a-f]\w*(\.\w+)?@\w+\.\w+$', re.I)
RE_FLOAT = re.compile(r'^\d*(\.\d*)?$')
RE_UUID = re.compile(r'^[a-f0-9]{32}$')
