import itertools
import re

from pprofile_ext import util
from pprofile_ext import parsers

RE_LINE = re.compile(r'\s*\d+\|')
RE_CALL = re.compile(r'\s*\(call\)\|')


def stuff_in_dict(this_dict, key):
    """
    if the `this_dict` dictionary is not empty then return a new dictionary that
    has one (key, value) pair, where the key is set to `key` and the value is set to `this_dict`

    :param this_dict: dictionary
    :param key: string
    :return: dictionary
    """
    return {key: this_dict} if len(this_dict) > 0 else {}


def command_line_handler(section):
    """
    Extracts the command_line information from section

    :param section: sequence of lines
    :return: yields a dict(('command_line', <command>), ) or {}
    """
    for line in section:
        if line.startswith('Command line:'):
            yield {'command_line': parsers.command_line_parser(line)}


def total_duration_handler(section):
    """
    Parses lines of the following form:

       Total duration: 5248.89s

    :param section: generator of lines
    :return: yields a dict(('total_duration', <seconds>), ) or {}
    """
    for line in section:
        if line.startswith('Total duration:'):
            yield {'total_duration': parsers.total_duration_parser(line)}


def summary_handler(section):
    """
    Extract the information from the PProfile summary section

    :param section: sequence of lines
    :return: dictionary
    """
    summary_dict = dict()
    for section_dict in itertools.chain.from_iterable(parse_section(section, (command_line_handler,
                                                                              total_duration_handler))):
        summary_dict = util.update(summary_dict, section_dict)

    yield {'summary': summary_dict}


def file_summary_handle(section):
    """
    Extract the file summary information for a given file

    :param section: sequence of lines
    :return: dictionary
    """
    fs_dict = dict()
    for line in section:
        if line.startswith('File:'):
            fs_dict = util.update(fs_dict, {'name': parsers.file_name_parser(line)})
        if line.startswith('File duration:'):
            fs_dict = util.update(fs_dict, {'duration': parsers.file_duration_parser(line)})
            fs_dict = util.update(fs_dict, {'percentage': parsers.file_percentage_parser(line)})

    yield stuff_in_dict(fs_dict, 'file_summary')


def line_handler(section):
    """
    Extract line information. This is a tricky thing since the also want to handle the (call)...
    information, which will allows to navigate more easily through the code. However, to parse
    (call) information we need to add information to the last line (non-call) handled...

    :param section: sequence of lines
    :return: dictionary
    """
    lines = list()
    for line in section:
        if RE_LINE.match(line):
            lines.append(parsers.parse_line(line))
        if RE_CALL.match(line):
            # parse the line and add it to the calls if the last line parsed
            call = parsers.parse_call(line)
            lines[-1]['calls'].append(call)

    yield stuff_in_dict(lines, 'lines')


def file_handler(section):
    """
    Extract the information for a single file in the profile

    :param section: sequence of lines
    :return: dictionary
    """
    file_dict = {}
    for file_section in split_sections(section, section_marker='-----'):
        for fdict in itertools.chain.from_iterable(parse_section(file_section, (file_summary_handle,
                                                                                line_handler))):
            file_dict = util.update(file_dict, fdict)

    yield stuff_in_dict(file_dict, util.hashkey(file_dict['file_summary']['name']) if file_dict else '')


def parse_section(section, handlers):
    """
    Applies each handler in the list of `handlers` to the section, which is a
    sequence of lines. Each handler yields one or more dictionaries containing
    the information extracted from the section.

    :param section: sequence of strings representing all the lines in a section
    :param handlers: sequence of handlers

    :return: yields dictionaries containing the information contained within
             each section
    """
    return (handler(section) for handler in handlers)


def split_sections(lines, section_marker='File:'):
    """
    Splits the sequences of `lines` into sections based on the `section_marker`.
    A line that starts with the section_marker signals the start of a new section
    in the sequence of lines.

    :param lines: sequence of lines
    :keyword section_marker: string that demarkates the start of a new section;
             default is 'File:'

    :return: a generator of sections
    """
    section = list()
    for line in lines:
        if line.startswith(section_marker):
            # this is the start of a new section so yield the current section
            yield section
            section = list()
        # add the line to the current section
        section.append(line)

    yield section
