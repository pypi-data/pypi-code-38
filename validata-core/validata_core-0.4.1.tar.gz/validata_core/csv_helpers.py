import csv

import tabulator

import logging

log = logging.getLogger(__name__)


def detect_dialect(source, **stream_params):
    """Read source using `tabulator.loader`, but use `csv.Sniffer` to detect delimiter, because `tabulator.parsers.csv` tries
    only those delimiters: '',\t;|''.
    """
    with tabulator.Stream(source, **stream_params) as stream:
        parser = stream._Stream__parser
        parser.reset()
        sample = prepare_sample(stream._Stream__parser._CSVParser__chars)
    try:
        return csv.Sniffer().sniff(sample)
    except Exception as e:
        log.exception(e)
        return None


def prepare_sample(stream):
    sample_lines = []
    while True:
        try:
            sample_lines.append(next(stream))
        except StopIteration:
            break
        if len(sample_lines) >= tabulator.config.CSV_SAMPLE_LINES:
            break
    return ''.join(sample_lines)
