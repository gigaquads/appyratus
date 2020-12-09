from __future__ import absolute_import

import io
import csv

from typing import Text

from .file import File


class Csv(File):
    """
    # CSV File Type
    """

    @classmethod
    def extensions(cls):
        return {'csv'}

    @classmethod
    def read(cls, path: Text, delimiter: Text = None):
        file_data = super().read(path=path)
        csv_data = cls.load(file_data, delimiter=delimiter)
        return csv_data

    @classmethod
    def write(cls, path: Text, data=None, delimiter: Text = None, **kwargs):
        file_data = cls.dump(data)
        super().write(path=path, data=file_data, **kwargs)

    @classmethod
    def dump(cls, data):
        """
        Convert a list of dicts into a blob
        """
        # only interested in lists
        if not isinstance(data, list):
            return
        # and only if the first item is a dict
        if not isinstance(data[0], dict):
            return
        # store CSV data in memory
        output = io.StringIO('')
        # write header from dictionary keys
        fieldnames = data[0].keys()
        writer = csv.DictWriter(
            output, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC
        )
        writer.writeheader()
        # write row data
        for row in data:
            writer.writerow(row)
        csv_blob = output.getvalue()
        return csv_blob

    @classmethod
    def load(cls, blob: Text, delimiter: Text = None):
        """
        Convert a csv blob into a list of dicts
        """
        buff = io.StringIO(blob)
        if not delimiter:
            delimiter = ','
        reader = csv.DictReader(buff, delimiter=delimiter)
        return [row for row in reader]
