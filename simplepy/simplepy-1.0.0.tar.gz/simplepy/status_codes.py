# -*- coding: utf-8 -*-
from enum import IntEnum


class StringStatus(IntEnum):
    MUST_IS_DIGIT = 201
    MUST_IS_STRING = 202
    STRING_OR_DIGIT = 203


class FileStatus(IntEnum):
    FILE_OPEN_FAIL = 300
    FILE_WRITE_FAIL = 301


class ConvertStatus(IntEnum):
    MUST_IS_DICT = 400
    MUST_IS_XML = 401


class DateStatus(IntEnum):
    MUST_FORMAT= 500
