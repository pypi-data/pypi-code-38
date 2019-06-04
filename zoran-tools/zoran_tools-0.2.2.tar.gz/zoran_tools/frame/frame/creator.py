import re
import csv
import sqlite3

from .sql import FakeFrame, Row


class FakeFrameCreator(object):
    @staticmethod
    def createFakeFrameByCSV(file, mode='r', encoding='utf8', fields=None, delimiter=',', quotechar='"'):
        with open(file, mode=mode, encoding=encoding) as f:
            f_csv = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
            collection = [Row(fields=FakeFrameCreator.genFields(fields, row), row=row) for row in f_csv]
        return FakeFrameCreator.createFakeFrameByCollection(collection=collection)

    @staticmethod
    def createFakeFrameByContent(content, fields):
        collection = [Row(fields=FakeFrameCreator.genFields(fields, row), row=row) for row in content]
        return FakeFrameCreator.createFakeFrameByCollection(collection=collection)

    @staticmethod
    def createFakeFrameByCollection(collection):
        fakeframe = FakeFrame()
        fakeframe._content = collection
        return fakeframe

    @staticmethod
    def createFakeFrameBySQLite(SQLiteDB, table):
        conn = sqlite3.connect(database=SQLiteDB)
        cur = conn.cursor()
        pass

    @staticmethod
    def genFields(fields, row):
        if isinstance(fields, list):
            if len(fields) == len(row):
                return fields
        else:
            return ['_{}'.format(i) for i, e in enumerate(row, 1)]
    pass


frame_from_csv = FakeFrameCreator.createFakeFrameByCSV
frame_from_content = FakeFrameCreator.createFakeFrameByContent
frame_from_collection = FakeFrameCreator.createFakeFrameByCollection
