#!/usr/bin/env python
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Helpers to manipulate source files
Check that each git tracked source file in the current directory contains a
copyright statement.
'''
from __future__ import print_function

import os
import re
from itertools import islice
from datetime import date

COPYRIGHT_SIGNATURE = re.compile(r'\bcopyright\b', re.I)
CHECKED_FILES = re.compile(
    r'.*(\.(i?[ch](pp|xx|c)?|cc|hh|py|C|cmake|[yx]ml|qm[ts]|dtd|xsd|ent|bat|[cz]?sh|js|html?)|'
    r'CMakeLists.txt|Jenkinsfile)$')

COPYRIGHT_STATEMENT = '''
(c) Copyright {} CERN for the benefit of the LHCb Collaboration

This software is distributed under the terms of the GNU General Public
Licence version 3 (GPL Version 3), copied verbatim in the file "{}".

In applying this licence, CERN does not waive the privileges and immunities
granted to it by virtue of its status as an Intergovernmental Organization
or submit itself to any jurisdiction.
'''

# see https://www.python.org/dev/peps/pep-0263 for the regex
ENCODING_DECLARATION = re.compile(
    r'^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)')

CLANG_FORMAT_VERSION = '8'
YAPF_VERSION = '0.24.0'
FORMATTABLE_LANGUAGES = ['c', 'py']


def is_script(path):
    '''
    Check if a given file starts with the magic sequence '#!'.
    '''
    with open(path, 'rb') as f:
        return f.read(2) == b'#!'


def to_check(path):
    '''
    Check if path is meant to contain a copyright statement.
    '''
    return os.path.isfile(path) and (bool(CHECKED_FILES.match(path))
                                     or is_script(path))


def is_empty(path):
    '''
    Check if file is empty or virtually empty (only spaces).
    '''

    def only_blanks():
        with open(path) as f:
            for l in f:
                if l.strip():
                    return False
        return True

    zero_size = os.stat(path).st_size == 0
    return zero_size or only_blanks()


def has_copyright(path):
    '''
    Check if there's a copyright signature in the first 100 lines of a file.
    '''
    with open(path) as f:
        return any(COPYRIGHT_SIGNATURE.search(l) for l in islice(f, 100))


def get_files(reference=None):
    '''
    Return iterable with the list of names of files to check.
    '''
    from subprocess import check_output
    if reference is None:
        all = check_output(['git', 'ls-files',
                            '-z']).rstrip('\x00').split('\x00')
    else:
        prefix_len = len(
            check_output(['git', 'rev-parse', '--show-prefix']).strip())
        all = (path[prefix_len:] for path in check_output([
            'git', 'diff', '--name-only', '--no-renames', '--diff-filter=MA',
            '-z', reference + '...', '.'
        ]).rstrip('\x00').split('\x00'))
    return (path for path in all if to_check(path))


def report(filenames, inverted=False, target=None):
    '''
    Print a report with the list of filenames.

    If porcelain is True, print only the names without descriptive message.
    '''
    print(
        ('The following {} files {}contain a copyright statement:\n- ').format(
            len(filenames), '' if inverted else 'do not '),
        end='')
    print('\n- '.join(filenames))
    if not inverted:
        if target:
            print('\nYou can fix the {} files without copyright statement '
                  'with:\n\n  $ lb-check-copyright --porcelain {} '
                  '| xargs -r lb-add-copyright\n'.format(
                      len(filenames), target))
        else:
            print('\nyou can fix them with the command lb-add-copyright\n')


def to_comment(text, lang_family='#', width=80):
    r'''
    Convert a chunk of text into comment for source files.

    The parameter lang_family can be used to tune the style of the comment:

        - 'c' for C/C++
        - '#' (default) for Python, shell, etc.
        - 'xml' for XML files

    >>> print(to_comment('a\nb\nc\n'), end='')
    ###############################################################################
    # a                                                                           #
    # b                                                                           #
    # c                                                                           #
    ###############################################################################
    >>> print(to_comment('a\nb\nc\n', 'c'), end='')
    /*****************************************************************************\
    * a                                                                           *
    * b                                                                           *
    * c                                                                           *
    \*****************************************************************************/
    >>> print(to_comment('a\nb\nc\n', 'xml'), end='')
    <!--
        a
        b
        c
    -->
    '''
    if lang_family == 'c':
        head = '/{}\\'.format((width - 3) * '*')
        line = '* {:%d} *' % (width - 5)
        tail = '\\{}/'.format((width - 3) * '*')
    elif lang_family in ('#', 'py'):
        head = (width - 1) * '#'
        line = '# {:%d} #' % (width - 5)
        tail = head
    elif lang_family == 'xml':
        head = '<!--'
        line = '    {}'
        tail = '-->'
    else:
        raise ValueError('invalid language family: {}'.format(lang_family))

    data = [head]
    data.extend(line.format(l.rstrip()).rstrip() for l in text.splitlines())
    data.append(tail)
    data.append('')
    return '\n'.join(data)


def lang_family(path):
    '''
    Detect language family of a file.
    '''
    if re.match(r'.*\.(xml|xsd|dtd|html?|qm[ts]|ent)$', path):
        return 'xml'
    elif re.match(r'(.*\.(i?[ch](pp|xx|c)?|cc|hh|C|opts|js)|'
                  r'Jenkinsfile)$', path):
        return 'c'
    elif re.match(r'.*\.py$', path) or re.match(r'^#!.*python',
                                                open(path).readline(120)):
        return 'py'
    else:
        return '#'


def find_encoding_declaration_line(lines, limit=2):
    '''
    Look for encoding declaration line (PEP-263) in a file and return the index
    of the line containing it, or None if not found.
    '''
    for i, l in enumerate(islice(lines, limit)):
        if ENCODING_DECLARATION.match(l):
            return i


def add_copyright_to_file(path, year=None, license_fn=None):
    '''
    Add copyright statement to the given file for the specified year (or range
    of years).  If the year argument is not specified, the current year is
    used.
    '''
    lang = lang_family(path)
    text = to_comment(COPYRIGHT_STATEMENT.format(
        year or date.today().year,
        license_fn or 'COPYING'
    ).strip(), lang)
    with open(path, 'rb') as f:
        data = f.readlines()

    offset = 0
    encoding_offset = find_encoding_declaration_line(data)
    if encoding_offset is not None:
        offset = encoding_offset + 1
    elif data[0].startswith('#!'):
        offset = 1
    elif lang == 'xml':
        offset = 1 if not path.endswith('.ent') else 0
        for l in data:
            if l.strip():
                # lcgdict selection files are a bit special
                if 'lcgdict' in l or '<!--' in l:
                    offset = 0
                break

    data.insert(offset, text)
    with open(path, 'wb') as f:
        f.writelines(data)


def call_formatter(cmd, input):
    '''
    Return the formatted version of the given file.
    '''
    from subprocess import Popen, PIPE, CalledProcessError
    import logging
    logging.debug('calling %r', cmd)
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out, err = p.communicate(input)
    if p.returncode:
        raise CalledProcessError(p.returncode, cmd, err)
    return out


def get_git_root(path):
    from subprocess import Popen, PIPE
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    p = Popen(['git', 'rev-parse', '--show-toplevel'],
              cwd=path,
              stdout=PIPE,
              stderr=PIPE)
    out, _ = p.communicate()
    if p.returncode == 0:
        return out.strip()
    else:
        return None


def find_clang_format(path):
    while not os.path.isdir(path):
        path = os.path.dirname(path)
    while True:
        parent = os.path.dirname(path)
        if os.path.exists(os.path.join(path, '.clang-format')):
            return path
        elif parent != path:
            path = parent
        else:
            return None  # root dir reached


_found_clang_format_dirs = []


def ensure_clang_format_style(path):
    from logging import debug
    path = os.path.abspath(path)
    global _found_clang_format_dirs
    if not any(
            os.path.commonprefix([d, path]) for d in _found_clang_format_dirs):
        base = find_clang_format(path)
        if base:
            debug('found .clang-format in %s', base)
            _found_clang_format_dirs.append(base)
        else:
            base = get_git_root(path)
            debug('found .git top dir in %s', base)
            if base:
                from LbDevTools import createClangFormat
                createClangFormat(os.path.join(base, '.clang-format'))
                _found_clang_format_dirs.append(base)


def find_command(names):
    from whichcraft import which
    from itertools import imap, ifilter
    try:
        return next(ifilter(None, imap(which, names)))
    except StopIteration:
        return None


class CommandNotFound(RuntimeError):
    def __init__(self, message):
        super(CommandNotFound, self).__init__(message)


def get_clang_format_cmd(version=CLANG_FORMAT_VERSION):
    cmd = find_command(
        cmd.format(version) for cmd in [
            'clang-format-{}', 'lcg-clang-format-{}', 'lcg-clang-format-{}.0',
            'lcg-clang-format-{}.0.0'
        ])
    if not cmd:
        raise CommandNotFound('clang-format-%s not found' % version)
    return cmd


def get_yapf_format_cmd(version=YAPF_VERSION):
    from subprocess import check_output
    cmd = find_command(['yapf'])
    if not cmd:
        raise CommandNotFound('yapf not found')
    found_version = check_output([cmd, '--version']).split()[-1]
    if found_version != version:
        raise CommandNotFound(
            'wrong yapf version %s (%s required)' % (found_version, version))
    return cmd


class Formatter:
    def __init__(self, clang_format_cmd, yapf_cmd):
        self.clang_format_cmd = clang_format_cmd
        self.yapf_cmd = yapf_cmd

    def cmd(self, path, lang):
        '''
        Return the command to run to format the file 'path' for language
        'lang'.
        '''
        if lang == 'c':
            assert self.clang_format_cmd, ('tried to format C/C++ file but '
                                           'clang-format is not available')
            ensure_clang_format_style(path)
            return [
                self.clang_format_cmd, '-style=file', '-fallback-style=none',
                '-assume-filename=' + path
            ]
        elif lang == 'py':
            assert self.yapf_cmd, ('tried to format Python file but '
                                   'yapf is not available')
            return [self.yapf_cmd]
        else:
            assert False, 'invalid language %r' % lang

    def __call__(self, input, path, lang, retry=True):
        '''
        Apply formatting rules to a file.

        :param input: content of the file to format
        :param path: name of the file
        :param lang: language ('c' or 'py')
        :param retry: boolean flag to tell if we have to retry the formatting
                      with a slightly modified name (see
                      https://gitlab.cern.ch/lhcb-core/LbDevTools/issues/20)

        :return: modified file, exception in case of problems
        '''
        import logging
        from subprocess import CalledProcessError
        try:
            return call_formatter(self.cmd(path, lang), input)

        except CalledProcessError:
            if lang == 'c' and path.endswith('.h') and retry:
                # this is a workaround for cases where clang-format does
                # not correctly detect the language
                try:
                    alias = path + 'h'
                    logging.info('retry formatting of %s as %s', path, alias)
                    return self(input, alias, lang, False)
                except CalledProcessError:
                    # ignore failures in the retry
                    pass
            raise  # raise original exception


# --- Scripts


def check_copyright():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='''
    Check that each git tracked source file in the current directory contains a
    copyright statement.
    ''')
    parser.add_argument(
        'reference',
        nargs='?',
        help='commit-ish to use as reference to only check changed file')
    parser.add_argument(
        '--porcelain',
        action='store_true',
        help='only print the list of files w/o copyright')
    parser.add_argument(
        '-z',
        action='store_const',
        dest='separator',
        const='\x00',
        help='when using --porcelain, paths are separated with NUL character')
    parser.add_argument(
        '--inverted',
        action='store_true',
        help='list files w/ copyright, instead of w/o (Default)')
    parser.set_defaults(inverted=False, separator='\n')

    args = parser.parse_args()

    missing = [
        path for path in get_files(args.reference)
        # we only deal with non-empty files and we report as "missing"
        # those without copyright, unless `args.inverted` is True, in which
        # case we invert the answer of has_copyright, to report the file _with_
        # copyright notice
        if not is_empty(path) and not (args.inverted ^ has_copyright(path))
    ]
    if missing:
        missing.sort()
        if not args.porcelain:
            report(missing, args.inverted, args.reference)
        else:
            print(args.separator.join(missing), end=args.separator)
        exit(1)


def add_copyright():
    from argparse import ArgumentParser
    parser = ArgumentParser(
        description='Add standard LHCb copyright statement to files.')
    parser.add_argument('files', nargs='+', help='files to modify')
    parser.add_argument(
        '--year', help='copyright year specification (default: current year)')
    parser.add_argument(
        '--license-fn', help='Name of the license file (default: COPYING)')
    parser.add_argument(
        '--force',
        action='store_true',
        help='add copyright also to non supported file types')

    args = parser.parse_args()

    for path in args.files:
        if not args.force and not to_check(path):
            print('warning: cannot add copyright to {} (file type not '
                  'supported)'.format(path))
        elif has_copyright(path):
            print('warning: {} already has a copyright statement'.format(path))
        else:
            add_copyright_to_file(path, args.year, args.license_fn)


def format():
    from argparse import ArgumentParser
    import logging
    parser = ArgumentParser(description='Reformat C++ and Python files.')
    parser.add_argument(
        'files',
        nargs='*',
        help='files to modify (empty list means all git tracked files)')
    parser.add_argument(
        '--clang-format-version',
        help='version of clang-format to use '
        '(default: %(default)s)')
    parser.add_argument(
        '--yapf-version', help='version of yapf to use (default: %(default)s)')
    parser.add_argument(
        '--verbose',
        action='store_const',
        const=logging.INFO,
        dest='log_level',
        help='print info messages')
    parser.add_argument(
        '--debug',
        action='store_const',
        const=logging.DEBUG,
        dest='log_level',
        help='print debug messages')
    parser.add_argument(
        '-n', '--dry-run', action='store_true', help='do not modify the files')
    parser.add_argument(
        '--format-patch',
        help='create a patch file with the changes, '
        'in this mode the first file argument is interpreted '
        'as reference branch')
    parser.add_argument(
        '-P',
        '--pipe',
        metavar='LANGUAGE',
        choices=FORMATTABLE_LANGUAGES,
        help='format from stdin to stdout (allowed values: %s)' %
        FORMATTABLE_LANGUAGES)
    parser.set_defaults(
        files=[],
        clang_format_version=CLANG_FORMAT_VERSION,
        yapf_version=YAPF_VERSION,
        log_level=logging.WARNING)

    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)

    if args.format_patch and args.pipe:
        parser.error('incompatible options --format-patch and -P/--pipe')

    if args.format_patch and len(args.files) > 1:
        parser.error('wrong number of arguments: at most one argument must be '
                     'provided when using --format-patch')

    if args.pipe and args.files:
        parser.error('cannot process explicit files in --pipe mode')

    from logging import debug, warning, info
    from subprocess import CalledProcessError
    from difflib import unified_diff

    # look for the required commands
    clang_format_cmd = yapf_cmd = None
    try:
        clang_format_cmd = get_clang_format_cmd(args.clang_format_version)
        info('using clang-format: %s', clang_format_cmd)
    except CommandNotFound as err:
        (parser.error if args.pipe == 'c' else warning)(
            '%s: C/C++ formatting not available' % err)

    try:
        yapf_cmd = get_yapf_format_cmd(args.yapf_version)
        info('using yapf: %s', yapf_cmd)
    except CommandNotFound as err:
        (parser.error if args.pipe == 'py' else warning)(
            '%s: Python formatting not available' % err)

    def can_format(path):
        if to_check(path):
            lang = lang_family(path)
            if ((clang_format_cmd and lang == 'c')
                    or (yapf_cmd and lang == 'py')):
                return lang
        return None

    if not args.pipe:
        if not args.files:
            args.files = filter(can_format, get_files())
        elif args.format_patch:
            # if we have args for --format-patch, it's a reference commit
            args.files = filter(can_format, get_files(args.files[0]))

    if args.pipe:
        import sys
        if args.pipe == 'c':
            ensure_clang_format_style(os.getcwd())
            cmd = [clang_format_cmd, '-style=file', '-fallback-style=none']
        else:
            cmd = [yapf_cmd]
        debug('cmd %s', cmd)
        print(call_formatter(cmd, sys.stdin.read()), end='')
    patch = []
    formatter = Formatter(clang_format_cmd, yapf_cmd)
    for path in args.files:
        lang = can_format(path)
        if lang:
            if is_empty(path):
                # make sure virtually empty files are empty
                with open(path, 'w'):
                    continue

            try:
                with open(path) as f:
                    input = f.read()
                output = formatter(input, path, lang)
                if args.format_patch:
                    patch.extend(
                        unified_diff(
                            input.splitlines(True), output.splitlines(True),
                            os.path.join('a', path), os.path.join('b', path)))
                elif output != input:
                    if args.dry_run:
                        print(path, 'should be changed')
                    else:
                        info('%s changed', path)
                        with open(path, 'w') as f:
                            f.write(output)
            except CalledProcessError as err:
                warning('could not format %r: %s\n%s', path, err,
                        err.output.rstrip())
        else:
            warning('cannot format %s (file type not supported)', path)

    # check if we need to create a patch file
    if patch:
        # we found some
        from email.message import Message
        from email.utils import formatdate
        msg = Message()
        msg.add_header('From', 'Gitlab CI <noreply@cern.ch>')
        msg.add_header('Date', formatdate())
        msg.add_header('Subject', '[PATCH] Fixed formatting')
        msg.set_payload('\n'.join([
            'patch generated by {}'.format(
                '{CI_PROJECT_URL}/-/jobs/{CI_JOB_ID}'.format(
                    **os.environ) if 'CI' in os.environ else 'standalone job'),
            '', '', ''.join(patch)
        ]))
        if args.format_patch == '-':
            print(msg.as_string())
        else:
            if (os.path.dirname(args.format_patch)
                    and not os.path.isdir(os.path.dirname(args.format_patch))):
                os.makedirs(os.path.dirname(args.format_patch))
            with open(args.format_patch, 'wb') as patchfile:
                patchfile.write(msg.as_string())
            print(
                '=======================================',
                ' You can fix formatting with:',
                '',
                sep='\n')
            if 'CI' in os.environ:
                print('   curl {CI_PROJECT_URL}/-/jobs/{CI_JOB_ID}/'
                      'artifacts/raw/{0} | '
                      'git am'.format(args.format_patch, **os.environ))
            else:
                print('   git am {}'.format(args.format_patch))
            print('', '=======================================', sep='\n')
        exit(1)


def clang_format():
    '''
    Simple wrapper to redirect calls to the required clang-format version.
    '''
    import sys
    try:
        os.execv(get_clang_format_cmd(), sys.argv)
    except CommandNotFound as err:
        exit('%s: internal command %s' % (os.path.basename(sys.argv[0]), err))


if __name__ == '__main__':
    # when invoked as a script, call the function with the same name
    # (check_copyright if no match)
    import sys
    name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if name.startswith('lb-'):  # special cases
        name = name[3:].replace('-', '_')
    main = globals().get(name, check_copyright)
    main()
