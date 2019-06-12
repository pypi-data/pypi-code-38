def command_line_parser(line):
    """
    Parses lines of the following form:

        Command line: ['to_html.py']

    :param line: sequence of lines
    :return: string containing the command_line, e.g., 'to_html.py'
    """
    idx_start, idx_end = line.find("['"), line.find("']")

    if idx_start == -1 or idx_end == -1:
        return ''
    else:
        return line[idx_start+2:idx_end]


def total_duration_parser(line):
    """
    Parses lines of the following form:

        Total duration: 5248.89s

    :param line: string
    :return: float containing total duration in seconds
    """
    try:
        return float(line.rstrip('s')[len('Total duration:'):].strip())
    except:
        return 0.


def file_duration_parser(line):
    """
    Parses lines of the following form: extracts only the seconds part

        File duration: 5248.68s (100.00%)

    :param line: string
    :return: float containing the duration for the file in seconds
    """
    line = line[len('File duration:'):]
    ie = line.find('s')
    try:
        return float(line[:ie])
    except:
        return 0.


def file_name_parser(line):
    """
    Parses lines of the following form: extracts only the seconds part

        File: to_html.py

    :param line: string
    :return: string containing the name of the file
    """
    ie = line.find(':')
    if ie == -1:
        return ''
    else:
        return line[ie+1:].strip()


def file_percentage_parser(line):
    """
    Parses lines of the following form: extracts only the seconds part

        File duration: 5248.68s (100.00%)

    :param line: string
    :return: float containing the duration for the file in percentage
    """
    is_ = line.find('(')
    ie_ = line.find('%')
    try:
        return float(line[is_+1:ie_])
    except:
        return 0.


def parse_line(line):
    """
    Parses lines of the following form

        Line #|      Hits|         Time| Time per hit|      %|Source code
        ------+----------+-------------+-------------+-------+-----------
             1|         2|   4.1008e-05|   2.0504e-05|  0.00%|import os

    Extracts a dict of (line_number, hits, time, time_per_hit, percentage, code)

    :param line: string
    :return: tuple
    """
    columns = line.split('|')

    return {'line_number': int(columns[0]),
            'hits': int(columns[1]),
            'time': float(columns[2]),
            'time_per_hit': float(columns[3]),
            'percentage': float(columns[4][:-1]),
            'code': '|'.join(columns[5:]),
            'calls': list(),
            'calls_from': dict()
            }


def parse_call(line):
    """
    Parses lines of the following form

        Line #|      Hits|         Time| Time per hit|      %|Source code
        ------+----------+-------------+-------------+-------+-----------
        (call)|      2528|     0.352177|   0.00013931|  0.01%|# to_html.py:74 get_html_filename

    Extracts a dict of (hits, time, time_per_hit, percentage, file_name, line_number, entry_point)

    :param line: string
    :return: tuple
    """
    columns = line.split('|')
    first, sep, second = columns[5].rpartition(':')
    line_number, sep, entry_point = second.partition(' ')
    file_name = first.strip('# ')

    return {'hits': int(columns[1]),
            'time': float(columns[2]),
            'time_per_hit': float(columns[3]),
            'percentage': float(columns[4][:-1]),
            'file_name': file_name,
            'line_number': int(line_number),
            'entry_point': entry_point
            }
