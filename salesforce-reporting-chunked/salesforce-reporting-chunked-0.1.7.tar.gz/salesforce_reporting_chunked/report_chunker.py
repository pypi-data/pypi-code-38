# -*- coding: utf-8 -*-
"""
report_chunker
--------------

Contains wrapper function `chunk_report_by_date`. Allows one to get report data with > 2000 rows.
"""
from collections import OrderedDict
from salesforce_reporting_chunked import Chunky, ReportParser


def chunk_report_by_date(
    config, report_id, fieldnames, date_fieldname, start_date, end_date, day_increment=1
):
    """
    Args:
        config (dict):  Dictonary containing username, password, security_token and api_version.
        report_id (str):    Salesforce report id.
        fieldnames (list):  Columns from Salesforce report.
        date_fieldname (str):   Name of sortable date fieldname used to get incremental chunks of report.
        start_date (str):   iso-formatted date string
        end_date (str): iso-formatted date string
        day_increment (int):    Number of days in an incremental chunk.
    Yields:
        row (OrderedDict):  Report row value as a python OrderedDict object.
    Example:
        >>> CONFIG = {"security_token": "br549", "username": "your@example.com", "password": "ultrasecret", "api_version": "v42.0" }
        >>> REPORT_ID = "abc123xyz789"
        >>> FIELDNAMES = ["Foo", "The_Date", "Bar"]
        >>> data = chunk_report_by_date(CONFIG, REPORT_ID, FIELDNAMES, date_fieldname="The_Date", start_date="2019-06-01", end_date="2019-07-01")
        >>> print(next(data))
        OrderedDict([('Foo', 'The thing'), ('The_Date', '6/1/2019') ('Bar', 'The other thing')])
    """

    sf = Chunky(**config)

    chunks = sf.get_daterange_chunked_report(
        report_id,
        date_fieldname=date_fieldname,
        start_date=start_date,
        end_date=end_date,
        day_increment=day_increment,
    )

    while True:
        try:
            parser = ReportParser(next(chunks))
            for line in parser.records():
                yield OrderedDict([(k, v) for k, v in zip(fieldnames, line)])
        except StopIteration:
            break
