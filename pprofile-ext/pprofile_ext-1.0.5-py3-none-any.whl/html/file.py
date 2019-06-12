import re

import six
from six.moves import zip
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from pprofile_ext import html

PYTHON_LEXER = PythonLexer()
HTML_FORMATTER = HtmlFormatter()


def add_total_time(pdict):
    """
    For each line in the profile add an item holding the total execution time
    for the line. The total execution time is the execution time of the line itself
    and the execution time of any of the calls associated with the line.

    Also adds a label adding the total execution of all the lines in the file
    to the 'file_summary' section.

    :param pdict: profile dict
    :return: profile dict
    """

    for line in pdict['lines']:
        line['total_time'] = line['time'] + sum([c['time'] for c in line['calls']])

    pdict['file_summary']['total_time'] = sum([line['total_time'] for line in pdict['lines']])

    return pdict


def highlight_code(pdict):
    """
    For each line in the profile add an item containing the syntax highlighted HTML
    version of the code. The key of the time is 'highlight'

    The function used Pygments to do the parsing/highlihting

    :param pdict: profile dict
    :return: profile dict
    """
    # reconstruct the entire code so that we can get the syntax highlighting of
    # blocks correctly
    html_code = highlight('\n'.join([(l['code'] if len(l['code']) > 0 else ' ') for l in pdict['lines']]),
                          PYTHON_LEXER, HTML_FORMATTER)

    # strip out the <div> and <pre> tags, we're going to replace them later
    is_, ie_ = html_code.find('<pre>'), html_code.rfind('</pre>')
    html_code = html_code[is_+len('<pre>'):ie_]

    # add back the <div> and <pre> tags, but for every line and add the highlighted code to the pdict
    hcode = ['<div style="margin-top:-8px;margin-bottom:-8px;" class="highlight"><pre>{0}</pre></div>'.format(line.encode('utf-8').decode())
             for line in html_code.split('\n')]
    for line, _hcode in zip(pdict['lines'], hcode):
        line['highlight'] = _hcode

    return pdict


def highlight_line(single_line):

    html_code = highlight(single_line, PYTHON_LEXER, HTML_FORMATTER)

    # strip out the <div> and <pre> tags, we're going to replace them later
    is_, ie_ = html_code.find('<pre>'), html_code.rfind('</pre>')
    html_code = html_code[is_+len('<pre>'):ie_]

    # add back the <div> and <pre> tags, but for every line and add the highlighted code to the pdict
    return '<div style="margin-top:-8px;margin-bottom:-8px;" class="highlight"><pre>{0}</pre></div>'.format(html_code.encode('utf-8').decode())


def calls_from(line, max_calls_from=5):
    # get the 5 most called from lines
    cfs = sorted([(key, count) for key, count in line['calls_from'].items()],
                 key=lambda x: x[1], reverse=True)[:max_calls_from]

    tags = [html.href('{0}#line{1}'.format(html.get_html_filename('', file), line),
                      str(idx + 1)) for idx, ((file, line), cnt) in enumerate(cfs)]

    space = '<div style="display:inline-block;height:12px;width:2px;background-color:#eeeeee";></div>'
    return space.join(tags)


def insert_call_for_line(code, call):
    """
    Replace the call['entry_point'] in `line` with a HTML <a> tag providing a link to the
    file / line of the actual `call` dict

    :param code: string containing the highlighted code
    :param call: dict containing the information for the specific code

    :return: updated string
    """
    replace_string = call['entry_point']

    return re.sub(r'(?<!\w)({0})(?!\w)'.format(replace_string),
                  html.href('{0}#line{1}'.format(html.get_html_filename('', call['file_name']),
                                                 call['line_number']), replace_string),
                  code)


def handle_lambda(call, line, file):
    """
    Resolve calls that point to <lambda>. Finds the lambda definition in the file/line
    pointed to by the `call` and extracts the name of the variable that gets assigned
    the lambda.

    :param call: call dictionary
    :param line: line dictionary
    :param file: file dictionary of the file pointed to by the call

    :return: updated call dictionary
    """

    if call['entry_point'] == '<lambda>':
        if line['line_number'] == call['line_number']:
            return {}

        num = call['line_number']
        # file the name of the variable defined in file['lines'][num-1]
        m = re.search(r'(?<=\s)(\w*)(?=\s*=\s*lambda)', file['lines'][num-1]['code'])
        if m is not None:
            call['entry_point'] = m.group(0)

    return call


def handle_init(call, line, file):
    """
    Resolve calls that point to __init__. Finds the preceding class definition in the
    file/line pointed to by the `call` and extracts the name of the class.

    :param call: call dictionary
    :param line: line dictionary
    :param file: file dictionary of the file pointed to by the call

    :return: updated call dictionary    """
    if call['entry_point'] == '__init__':

        num = call['line_number']
        # if the line contains the ' cls(' replace the entry point with cls
        m = re.search(r'(?<=\s)(cls)(?={0})'.format(re.escape('(')), line['code'])
        if m is not None:
            call['entry_point'] = 'cls'
            return call

        # otherwise we need to find the first class definition above the line holding the init
        while num > -1:
            m = re.search(r'(?<=class\s)(\w*)(?={0})'.format(re.escape('(')), file['lines'][num]['code'])
            if m is not None:
                call['entry_point'] = m.group(0)
                return call
            num -= 1

    # if this is not a __init__ entry point or we failed to find one, then return the call itself
    return call


def resolve_calls_for_file(file, pdict, filemap):
    """
    Resolve as many calls as possible in `file`. Used separate handlers for resolving
    <lambda>s and __init__s

    :param file: file dictionary
    :param pdict: profile dictionary
    :param filemap: map of file_name to file hash in the main profile dictionary

    :return: updated profile dictionary
    """
    for line in file['lines']:
        line['calls'] = [c for c in [handle_lambda(call, line, pdict[filemap[call['file_name']]])
                                     for call in line['calls']] if len(c) > 0]
        line['calls'] = [c for c in [handle_init(call, line, pdict[filemap[call['file_name']]])
                                     for call in line['calls']] if len(c) > 0]

    return pdict


def resolve_calls(pdict):
    """
    This is an attempt to resolve calls to constructors (__init__) and lambdas. These
    calls can be across files so we need the entire dict of information

    :param pdict: profile dict dictionary

    :return: updated profile dictionary
    """
    filemap = dict((v['file_summary']['name'], k) for k, v in six.iteritems(pdict) if k != 'summary')

    for file in [file for k, file in six.iteritems(pdict) if k != 'summary']:
        pdict = resolve_calls_for_file(file, pdict, filemap)

    return pdict


def clean_pdict(pdict):
    """
    For some reason pprofile screws up some of the profile stats when profiling cells in and
    ipython notebook. This function attempts cleans up those lines by inserting additional
    "line breaks"

    :param pdict: profile dictionary

    :return: updated profile dictionary
    """
    for file in [file for k, file in six.iteritems(pdict) if k != 'summary']:
        file['lines'] = [line for line in file['lines'] if not line['code'].strip().startswith('(call)')]

    return pdict


def insert_calls(pdict):
    """
    For each line insert HTML links to all of the calls in that line (if possible)

    :param pdict: profile dictionary

    :return: updated profile dictionary
    """
    for line in pdict['lines']:
        for call in line['calls']:
            line['highlight'] = insert_call_for_line(line['highlight'], call)

    return pdict


def html_file_summary(pdict):
    """
    Generate the HTML for the file summary section. This includes the file name and
    duration in seconds and percentage.

    :param pdict: profile dictionary

    :return: sequence containing the HTML for the file summary section
    """
    return ['<div style="top:0;position:fixed;background-color:#eeeeee;">',
            html.href('index.html', 'index'),
            '</div>'
            '</br></br>',
            '<b>File name</b> : {0}</br>'.format(html.strip_pointy(pdict['name'])),
            '<b>Duration (sec)</b> : {0} seconds</br>'.format(pdict['duration']),
            '<b>Duration (perc)</b> : {0} &#37</br>'.format(pdict['percentage'])]


def get_column_specs(pdict, summary=False):
    """Return the column specifications for the html table"""

    if summary:
        col2 = lambda l: html.div(html.href('#line{0}'.format(l['line_number']), l['line_number']))
        col8 = lambda l: highlight_line(l['code'].lstrip())
    else:
        col2 = lambda l: html.div('<a name=line{0}>{0}</a>'.format(l['line_number']))
        col8 = lambda l: l['highlight']

    column_specs = (html.column_spec('',
                                     lambda l: html.box(l['time'], l['total_time'],
                                                        pdict['file_summary']['total_time']),
                                     40,
                                     padding_left=0,
                                     padding_right=0),
                    html.column_spec('line',
                                     col2,
                                     40),
                    html.column_spec('hits',
                                     lambda l: html.div(html.pre('{0}'.format(l['hits'] if l['hits'] > 0 else ''))),
                                     70),
                    html.column_spec('total time',
                                     lambda l: html.div(html.pre('{0:.4f}'.format(l['total_time'])
                                                                 if l['total_time'] > 0 else '')),
                                     70),
                    html.column_spec('self time',
                                     lambda l: html.div(html.pre('{0:.4f}'.format(l['time']) if l['time'] > 0 else '')),
                                     70),
                    html.column_spec('time per hit',
                                     lambda l: html.div(html.pre('{0:.2e}'.format(l['time_per_hit'])
                                                                 if l['time_per_hit'] > 0 else '')),
                                     70),
                    html.column_spec('called from',
                                     lambda l: html.div(calls_from(l)),
                                     50,
                                     align='left'),
                    html.column_spec('',
                                     col8,
                                     None,
                                     padding_right=0,
                                     align='left')
                    )

    return column_specs


def html_file_most_expensive(pdict, max_lines=10):
    """
    Generate the HTML for the most expensive lines section. This includes all the information
    for the most expensive `max_lines` lines. The line number in the section are HTML link to
    the actual lines in the source code section.

    :param pdict: profile dictionary

    :return: sequence containing the HTML for the most expensive lines section
    """
    # sort lines by total_time in reverse order
    sorted_lines = sorted([line for line in pdict['lines']],
                          key=lambda l: l['total_time'],
                          reverse=True)[:max_lines]

    # columns_specs for the table columns of the most expensive lines section
    column_specs = get_column_specs(pdict, summary=True)

    # generate the HTML
    h = html.html()

    with h.title():
        h.add('most expensive lines')
    with h.table():
        # header row
        with h.table_row():
            for c in column_specs:
                h.add(c(None, header=True))
        # content rows
        for line in sorted_lines:
            with h.table_row():
                for c in column_specs:
                    h.add(c(line))

    return h.buffer


def html_file_lines(pdict):
    """
    Generate the HTML for the source code section.

    :param pdict: profile dictionary

    :return: sequence containing the HTML for the most expensive lines section
    """

    # columns_specs for the table columns of the source section
    column_specs = get_column_specs(pdict)

    # generate the html
    h = html.html()

    with h.title():
        h.add('source code')
    with h.table():
        # header row
        with h.table_row():
            for c in column_specs:
                h.add(c(None, header=True))
        # content rows
        for line in pdict['lines']:
            with h.table_row():
                for c in column_specs:
                    h.add(c(line))

    return h.buffer


def html_file(pdict, output_dir):
    """
    Generate the HTML output for a single file.

    :param pdict: profile dictionary
    :param output_dir: location where html file is written

    :return: updated profile dictionary
    """
    # each line has a 'time', or self_time, and a 'total_time', which is the time spent
    # in the line itself and in its calls. so add the total_time to the line dict
    pdict = add_total_time(pdict)
    # include pretty syntax highlighting
    pdict = highlight_code(pdict)
    # add HTML links for calls
    pdict = insert_calls(pdict)

    # generate the html
    h = html.html()

    with h.preamble():
        h.add(html_file_summary(pdict['file_summary']))
        h.add(html.hrule())
        h.add(html_file_most_expensive(pdict))
        h.add(html_file_lines(pdict))

    # write the html to file
    with open(html.get_html_filename(output_dir, pdict['file_summary']['name']), 'w') as f:
        f.write(''.join(h.buffer))

    return pdict


def html_files(pdict, output_dir):
    """
    For each file in the profile generate the HTML

    :param pdict: profile dictionary
    :param output_dir: location where html files are written

    :return: updated profile dictionary
    """

    pdict = clean_pdict(pdict)
    pdict = resolve_calls(pdict)

    for fdict in (v for k, v in six.iteritems(pdict) if k != 'summary'):
        html_file(fdict, output_dir)

    return pdict
