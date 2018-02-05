import os


class File(object):
    @classmethod
    def read(cls, file_path: str):
        if not os.path.exists(file_path):
            return
        with open(file_path) as contents:
            return contents.read()

    @classmethod
    def write(cls, file_path: str, contents=None):
        with open(file_path, 'wb') as write_bytes:
            write_bytes.write(contents.encode())
