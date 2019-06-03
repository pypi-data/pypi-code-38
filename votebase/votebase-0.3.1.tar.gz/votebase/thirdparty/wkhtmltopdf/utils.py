from django.conf import settings

from wkhtmltopdf.views import PDFTemplateResponse
from wkhtmltopdf.utils import (check_output, copy, os, chain, _options_to_args,
                               sys)


def wkhtmltopdf_fix(pages, output=None, **kwargs):
    """
    Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.

    pages: List of file paths or URLs of the html to be converted.
    output: Optional output file path. If None, the output is returned.
    **kwargs: Passed to wkhtmltopdf via _extra_args() (See
              https://github.com/antialize/wkhtmltopdf/blob/master/README_WKHTMLTOPDF
              for acceptable args.)
              Kwargs is passed through as arguments. e.g.:
                  {'footer_html': 'http://example.com/foot.html'}
              becomes
                  '--footer-html http://example.com/foot.html'

              Where there is no value passed, use True. e.g.:
                  {'disable_javascript': True}
              becomes:
                  '--disable-javascript'

              To disable a default option, use None. e.g:
                  {'quiet': None'}
              becomes:
                  ''

    example usage:
        wkhtmltopdf(pages=['/tmp/example.html'],
                    dpi=300,
                    orientation='Landscape',
                    disable_javascript=True)
    """
    if isinstance(pages, basestring):
        # Support a single page.
        pages = [pages]

    if output is None:
        # Standard output.
        output = '-'

    # Default options:
    options = getattr(settings, 'WKHTMLTOPDF_CMD_OPTIONS', None)
    if options is None:
        options = {'quiet': True}
    else:
        options = copy(options)
    options.update(kwargs)

    # Force --encoding utf8 unless the user has explicitly overridden this.
    options.setdefault('encoding', 'utf8')

    env = getattr(settings, 'WKHTMLTOPDF_ENV', None)
    if env is not None:
        env = dict(os.environ, **env)

    cmd = getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf')
    args = list(chain(cmd.split(),
        _options_to_args(**options),
        list(pages),
        [output]))
    #    return check_output(args, stderr=sys.stderr, env=env)
    try:
        return check_output(args, stderr=sys.stderr, env=env)
    except AttributeError:
        return check_output(args, env=env)


class PDFTemplateResponse(PDFTemplateResponse):
    def convert_to_pdf(self, filename,
                       header_filename=None, footer_filename=None):
        cmd_options = self.cmd_options.copy()
        # Clobber header_html and footer_html only if filenames are
        # provided. These keys may be in self.cmd_options as hardcoded
        # static files.
        if header_filename is not None:
            cmd_options['header_html'] = header_filename
        if footer_filename is not None:
            cmd_options['footer_html'] = footer_filename
        return wkhtmltopdf_fix(pages=[filename], **cmd_options)
