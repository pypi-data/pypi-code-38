from collections import defaultdict
from functools import partial
import itertools
import os
import os.path

from pprofile_ext import handlers
from pprofile_ext import util
from pprofile_ext.html import file
from pprofile_ext.html import summary


def get_reverse_dict(pdict):
    """
    Build the reverse call information from the profile dictionary. The reverse
    call information basically state: this line was called from this other line.

    :param pdict: profile dictionary
    :return: reverse call dictionary
    """
    def update_reverse_call_dict(hashkey, line_number):
        """Helper function to update the info in the reverse call dictionary"""
        rdict[hashkey][line_number][(from_file, from_line['line_number'])] += from_line['hits']
        return rdict

    rdict = defaultdict(partial(defaultdict, (partial(defaultdict, int))))
    for key, fdict in pdict.items():
        if key != 'summary':
            from_file = fdict['file_summary']['name']
            for from_line in fdict['lines']:
                for call in from_line['calls']:
                    rdict = update_reverse_call_dict(util.hashkey(call['file_name']),
                                                     call['line_number'])

    return rdict


def update_profile_dict_with_reverse_dict(pdict, rdict):
    """
    Updates the profile information in `pdict` with the reverse call
    information in `rdict`.

    :param pdict: profile dictionary
    :param rdict: reverse call dictionary
    :return: updated profile dictionary
    """
    for key, calls_from in rdict.items():
        if key in pdict:
            for line in pdict[key]['lines']:
                if line['line_number'] in calls_from:
                    line['calls_from'] = calls_from[line['line_number']]

    return pdict


def get_profile_dict(stream):
    """
    Consumes the `stream` containing the pprofile output and returns a dictionary containing
    the parsed profile information

    :param stream: stream
    :return: dictionary
    """
    lines = (line.rstrip('\n') for line in stream)

    profile_dict = dict()
    for section in handlers.split_sections(lines):
        for section_dict in itertools.chain.from_iterable(handlers.parse_section(section, (handlers.summary_handler,
                                                                                           handlers.file_handler))):
            profile_dict = util.update(profile_dict, section_dict)

    return profile_dict


def process_profile(output_dir):
    """
    Generate the HTML from the pprofile output stored in `output_dir`.

    :param output_dir: location to store the profile output

    :return: path to the index.html file (relative to the notebook)
    """
    pname = os.path.abspath(os.path.join(output_dir, 'pprofile.txt'))

    # parse pprofile.txt and create the html output
    with open(pname, 'r') as f:
        pdict = get_profile_dict(f)
        rdict = get_reverse_dict(pdict)
        pdict = update_profile_dict_with_reverse_dict(pdict, rdict)

        # generate html pages: summary page first
        pdict = summary.html_summary(pdict, output_dir)
        # then an HTML file per file in the profile output
        file.html_files(pdict, output_dir)

    return output_dir + '/index.html'


def indent_code(code):
    """
    Takes the lines of code in `code` and adds for spaces to each line.

    :param code: string containing code to be profiled

    :return: string containing indented code
    """
    return [' ' * 4 + line for line in code.split('\n')]


def compile_code(code, output_dir):
    """
    Generates the code necessary to run a profile on `code` and compiles it. The code generated is

        import pprofile
        profiler = pprofile.Profiler()
        with profiler:
            `code`
        profiler_dump_starts('output_dir/pprofile.txt')

    :param code: string holding the code to be profiled
    :param output_dir: location to store the profile output

    :return: compiled code
    """

    pname = os.path.abspath(os.path.join(output_dir, 'pprofile.txt'))

    pcode = ['import pprofile',
             'profiler = pprofile.Profile()',
             'with profiler():']

    pcode += indent_code(code)
    pcode += ["profiler.dump_stats('{0}')".format(pname)]

    pcode = '\n'.join(pcode)

    return compile(pcode, '<string>', 'exec')


def create_output_dir(output_dir):
    """
    Create the output directory for the profile output. If the directory exists a different
    directory will be created names `output_dir`_1, etc.

    :param output_dir: user supplied name of the output directory for the profile output

    :return: path to output_dir
    """
    # output_dir is a directory relative to the current working directory, which
    # is at the same level as the notebook
    path, cntr = output_dir, 1
    while os.path.exists(path):
        path = output_dir + '_{0}'.format(cntr)
        cntr += 1

    # create the actual directory
    os.makedirs(path)

    return path

