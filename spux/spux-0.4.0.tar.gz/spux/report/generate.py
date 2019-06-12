# # # # # # # # # # # # # # # # # # # # # # # # # #
# Generate various LaTeX code for tables and figures
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import glob
import os
import shutil
import numpy
import re
import PIL

from ..io import dumper
from ..utils import shell

def txt_table (entries, headers=None, title=None, align='l', formatters = {}, widths=None):
    """Generate an ASCII table from the list of dicts with table entries."""

    if headers is None:
        headers = list (entries [0] .keys ())


    if type (align) == list:
        aligns = {header : align [column] for column, header in enumerate (headers)}
    else:
        aligns = {header : align for header in headers}
    for header in headers:
        if aligns [header] in ['l', 'r', 'c']:
            aligns [header] += 'just'
        else:
            aligns [header] = 'ljust'

    entries = [{header : (formatters [header] (entry [header]) if header in formatters else entry [header]) for header in headers} for entry in entries]

    if widths is None:
        widths = [max ([len (str (entry [header])) for entry in entries] + [len (header)]) for header in headers]
    extent = sum (widths) + 3 * (len (entries [0]) - 1)
    if title is not None:
        extent = max (extent, len (title))

    text = ''
    text += '=' * extent + '\n'

    if title is not None:
        text += title + ' ' * (extent - len (title)) + '\n'
        text += '=' * extent + '\n'

    text += ' | '.join ([getattr (header, aligns [header]) (width) for header, width in zip (headers, widths)]) + '\n'
    text += ' + '.join (['-' * width for width in widths]) + '\n'
    for entry in entries:
        text += ' | '.join ([getattr (str (entry [header]), aligns [header]) (width) for header, width in zip (headers, widths)]) + '\n'
    text += '=' * extent
    return text

def tex_escape (text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """

    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

def tex_table (entries, headers=None, align='l', formatters={}, math=False, columns=None):
    """Generate TeX code with the table from the specified entries and headers."""

    if headers is None:
        headers = list (entries [0] .keys ())

    if columns is not None:
        tables = int (numpy.ceil (len (headers) / columns))
        batches = numpy.array_split (numpy.array (headers), tables)
        return '\n\n'.join ([tex_table (entries, batch, align, formatters, math) for batch in batches])

    if type (align) == list:
        aligns = '|' + '|'.join (align) + '|'
    else:
        aligns = '|' + (align + '|') * len (entries [0])

    text = r'\begin{tabular}{%s}' % aligns + '\n'
    text += r'\hline' + '\n'
    text += (r' & '.join ([r'%s'] * len (headers))) % tuple (headers) + r'\\' + '\n'
    text += r'\hline' + '\n'
    text += r'\hline' + '\n'
    for entry in entries:
        template = r'$%s$' if math else '%s'
        cells = {header : (formatters [header] (entry [header]) if header in formatters else entry [header]) for header in headers}
        text += r' & '.join ([template % (cells [header] if math else tex_escape (str (cells [header]))) for header in headers]) + r'\\' + '\n'
        text += r'\hline' + '\n'

    text += r'\end{tabular}'

    return text

def report (authors=None, title=None, date=None, order=None, reportdir='report', figuredir='fig', latexdir='latex', htmldir='htmldir'):
    """Generates latex source files and the compiled pdf for the SPUX report."""

    print (' :: Generating LaTeX report in "%s" directory...' % latexdir)
    print ('  : -> HTML files (e.g. for Authorea) are generated in "%s" directory...' % htmldir)

    if authors is None:
        authors = 'Author(s) not specified'

    if title is None:
        title = 'SPUX report for "%s" inference' % dumper.prefixname ()

    if date is None:
        date = r'\today'

    if order is None:

        order = {}

        order ['reports'] = {}
        order ['reports'] ['setup'] = ['config']
        order ['reports'] ['results'] = ['environment', 'resources', 'setup', 'evaluations', 'metrics', 'MAP']
        order ['reports'] ['performance'] = ['runtimes']

        order ['figures'] = {}
        order ['figures'] ['setup'] = []
        order ['figures'] ['setup'] += ['dataset']
        order ['figures'] ['setup'] += ['distributions-prior']
        order ['figures'] ['setup'] += ['distributions-initial']
        order ['figures'] ['setup'] += ['errors']

        order ['figures'] ['results'] = []
        order ['figures'] ['results'] += ['unsuccessfuls']
        order ['figures'] ['results'] += ['resets']
        order ['figures'] ['results'] += ['parameters']
        order ['figures'] ['results'] += ['likelihoods']
        # order ['figures'] ['results'] += ['max_avg_errs']
        order ['figures'] ['results'] += ['fitscores']
        order ['figures'] ['results'] += ['accuracies']
        order ['figures'] ['results'] += ['particles']
        order ['figures'] ['results'] += ['redraw']
        order ['figures'] ['results'] += ['acceptances']
        order ['figures'] ['results'] += ['autocorrelations']
        order ['figures'] ['results'] += ['posteriors']
        order ['figures'] ['results'] += ['posterior2d']
        order ['figures'] ['results'] += ['predictions']
        order ['figures'] ['results'] += ['qq']

        order ['figures'] ['performance'] = []
        order ['figures'] ['performance'] += ['traffic']
        order ['figures'] ['performance'] += ['runtimes']
        order ['figures'] ['performance'] += ['efficiency']
        order ['figures'] ['performance'] += ['timestamps']

    directory, filename = os.path.split (os.path.realpath (__file__))
    templatesdir = os.path.join (directory, 'templates')

    dumper.mkdir (latexdir)

    # read table template
    with open (os.path.join (templatesdir, 'table.tex'), 'r') as file:
        tabletex = file.read ()

    # read figure template
    with open (os.path.join (templatesdir, 'figure.tex'), 'r') as file:
        figuretex = file.read ()

    def generate_section (section, template, texs = None, pdfs = None):

        # read template
        with open (os.path.join (templatesdir, template), 'r') as file:
            templatetex = file.read ()

        # get all .tex files from the reportdir
        if texs is None:
            texs = glob.glob (os.path.join (reportdir, '*.tex'))
            texs = sorted ([os.path.basename (tex) for tex in texs])
            if len (texs) == 0:
                print (' :: WARNING: No reports found in %s.' % reportdir)
        texs_used = {tex : False for tex in texs}
        reports = []

        # add all .tex files into report
        if len (texs) > 0:
            for name in order ['reports'] [section]:
                for tex in texs:
                    if name in tex:
                        captionfile = os.path.join (reportdir, tex [:-4] + '.cap')
                        if os.path.exists (captionfile):
                            with open (captionfile, 'r') as file:
                                caption = tex_escape (file.read ())
                        else:
                            caption = 'Table caption is not specified.'
                        args = {'table' : tex, 'caption' : caption, 'label' : tex [:-4]}
                        reports += [tabletex % args]
                        texs_used [tex] = True

        # get all .tex files from the reportdir
        if pdfs is None:
            pdfs = glob.glob (os.path.join (figuredir, '*.pdf'))
            pdfs = sorted ([os.path.basename (pdf) for pdf in pdfs])
            if len (pdfs) == 0:
                print (' :: WARNING: No figures found in %s.' % figuredir)
        pdfs_used = {pdf : False for pdf in pdfs}
        figures = []

        # add all .pdf files into report (include .tex captions, if available)
        if len (pdfs) > 0:
            for name in order ['figures'] [section]:
                for pdf in pdfs:
                    if name in pdf:
                        captionfile = os.path.join (figuredir, pdf [:-4] + '.cap')
                        if os.path.exists (captionfile):
                            with open (captionfile, 'r') as file:
                                caption = tex_escape (file.read ())
                        else:
                            caption = 'Figure caption is not specified.'
                        pngfile = os.path.join (figuredir, pdf [:-4] + '.png')
                        width = min (1, max (0.5, PIL.Image.open (pngfile) .size [0] / 4000))
                        args = {'figure' : pdf [:-4], 'width' : width, 'caption' : caption, 'label' : pdf [:-4]}
                        figures += [figuretex % args]
                        pdfs_used [pdf] = True

        # save pwd_section.tex
        args = {}
        args ['reports'] = '\n\n'.join (reports) if len (reports) > 0 else 'No reports found.'
        args ['figures'] = '\n\n'.join (figures) if len (figures) > 0 else 'No figures found.'
        dumper.text (templatetex % args, template, latexdir, prefix=True)

        return texs_used, pdfs_used

    # generate setup section
    texs_setup, pdfs_setup = generate_section (section = 'setup', template = 'setup.tex')

    # generate results section
    texs_results, pdfs_results = generate_section (section = 'results', template = 'results.tex')

    # generate performance section
    texs_performance, pdfs_performance = generate_section (section = 'performance', template = 'performance.tex')

    # generate section with all remaining reports and figures
    texs_misc = [tex for tex in texs_setup.keys () if not (texs_setup [tex] or texs_results [tex] or texs_performance [tex])]
    pdfs_misc = [pdf for pdf in pdfs_setup.keys () if not (pdfs_setup [pdf] or pdfs_results [pdf] or pdfs_performance [pdf])]
    order ['reports'] ['miscellaneous'] = texs_misc
    order ['figures'] ['miscellaneous'] = pdfs_misc
    generate_section (section = 'miscellaneous', template = 'miscellaneous.tex', texs = texs_misc, pdfs = pdfs_misc)

    # read title template and fill it
    with open (os.path.join (templatesdir, 'title.tex'), 'r') as file:
        titletex = file.read ()
        args = {'title' : title}
        dumper.text (titletex % args, 'title.tex', latexdir, prefix=False)

    # read report template and fill it
    with open (os.path.join (templatesdir, 'report.tex'), 'r') as file:
        reporttex = file.read ()
        args = {'authors' : authors, 'date' : date}
        args ['setup'] = dumper.prefixname ('setup.tex')
        args ['results'] = dumper.prefixname ('results.tex')
        args ['performance'] = dumper.prefixname ('performance.tex')
        args ['miscellaneous'] = dumper.prefixname ('miscellaneous.tex')
        dumper.text (reporttex % args, 'report.tex', latexdir, prefix=True)

    # copy remaining needed files (header, logo, etc.)
    shutil.copyfile (os.path.join (templatesdir, 'header.tex'), os.path.join (latexdir, 'header.tex'))
    shutil.copyfile (os.path.join (templatesdir, 'spux-logo.png'), os.path.join (latexdir, 'spux-logo.png'))

    # compile PDF
    if shutil.which ('pdflatex') is None:
        print (' :: SKIPPING: Command "pdflatex" is not available - PDF will not be compiled.')
    else:
        command = 'pdflatex %s' % dumper.prefixname ('report.tex')
        shell.execute (command, latexdir)