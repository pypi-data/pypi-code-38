import os
import sys
import inspect
import re

if 'setuptools' not in sys.modules:

    from sphinxcontrib.autoanysrc import analyzers

    class CustomAnalyzer(analyzers.BaseAnalyzer):
        """
        Simple class that takes arbitrary files, starts and ends blocks, and strips comment characters
        """

        comment_starts_with = '"""'  # String to start a comment block
        comment_ends_with = '"""'    # String to end a comment block
        strip_leading = 0            # Number of characters to strip from the beginning of the comments

        def process_line(self, line):
            yield line

        def process(self, content):

            in_comment_block = False

            for lineno, srcline in enumerate(content.split('\n')):

                line = srcline.rstrip()
                if in_comment_block:
                    if line.startswith(self.comment_ends_with):
                        in_comment_block = False
                        yield '', lineno
                        continue

                    if len(line) < self.strip_leading:
                        yield '', lineno
                    else:
                        for parsed in self.process_line(line[self.strip_leading:]):
                            yield parsed, lineno

                elif line.startswith(self.comment_starts_with):
                    in_comment_block = True


    class ShellScriptAnalyzer(CustomAnalyzer):
        """
        Processes shell scripts

        Comment blocks start and end with ##!.
        Assumes the comments start with # and a space, so
        it just returns the line with the first two characters stripped.
        """

        comment_starts_with = '##!'
        comment_ends_with = '##!'
        strip_leading = 2


    class PODAnalyzer(CustomAnalyzer):
        """
        Processes perl scripts with POD comments

        Comment blocks start with =pod and end with =cut.
        """

        comment_starts_with = '=pod'
        comment_ends_with = '=cut'

        headers = ['=', '~', '+', '^', '*', '-', '#']

        # Just the POD markup that I use
        markup = {
            'B': '**',
            'C': '``',
            'I': '`'
        }

        def process_line(self, line):

            for key in self.markup:
                line = re.sub(r'' + key + r'\<([^\>]+)\>',
                              r'' + self.markup[key] + r'\1' + self.markup[key],
                              line)

            if line.startswith('=head'):
                output = ' '.join(line.split()[1:])
                end = []

                if output.endswith(':'):
                    output = output.rstrip(':')
                    end.append('::')

                for final in [output, self.headers[int(line[5]) - 1] * len(output)] + end:
                    yield final

            elif line.endswith(':') and not line.endswith('::'):
                yield line + ':'

            else:
                yield line


def pretty_exe_doc(program, parser, stack=1, under='-'):
    """
    Takes the name of a script and a parser that will give the help message for it.
    The module that called this function will then add a header to the docstring
    of the script, followed immediately by the help message generated
    by the OptionParser

    :param str program: Name of the program that we want to make the header
    :param optparser.Option parser: Either a parser or a callable with no arguments
                                    that will give the desired parser
    :param int stack: How far up the stack to get the docstring to change
    :param str under: The character you want for the program underline
    """

    if os.path.basename(sys.argv[0]) == 'sphinx-build':
        # Get the calling module
        mod = inspect.getmodule(inspect.stack()[stack][0])

        # Get parser
        _parser = parser() if '__call__' in dir(parser) else parser

        # Make the parser use the correct program
        _parser.set_usage(mod.__usage__.replace('%prog', program))

        # Modify docs by adding a header and usate
        mod.__doc__ = '\n'.join(['', program, under * len(program), '::', ''] +
                                ['    %s' % l for l in _parser.format_help().split('\n')]) + \
                                mod.__doc__



__version__ = '0.3.0'
