from __future__ import absolute_import

import io
import csv

from typing port Text

from .base import BaseFile


class Csv(BaseFile):
    @classmethod
    def from_file(cls, file_path: Text, delimiter: Text = None):
        file_data = cls.load_file(file_path=file_path, delimiter=delimiter)
        return file_data

    @classmethod
    def load_file(cls, file_path: Text, delimiter: Text = None):
        file_data = File.read(file_path=file_path)
        csv_data = cls.data_from_blob(blob=file_data, delimiter=delimiter)
        return csv_data

    @classmethod
    def blob_from_data(cls, data):
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
    def data_from_blob(cls, blob: Text, delimiter: Text = None):
        """
        Convert a csv blob into a list of dicts
        """
        buff = io.StringIO(blob)
        if not delimiter:
            delimiter = ','
        reader = csv.DictReader(buff, delimiter=delimiter)
        return [row for row in reader]
