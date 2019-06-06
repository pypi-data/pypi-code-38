import argparse

from ligo.gracedb import rest

from .. import followup_advocate


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version', action='version', version=followup_advocate.__version__)
    parser.add_argument(
        '--service', default=rest.DEFAULT_SERVICE_URL, help='GraceDb API URL')
    subparsers = parser.add_subparsers(help='sub-command help')

    authors = argparse.ArgumentParser(add_help=False)
    authors.add_argument(
        'authors', metavar="'A. Einstein (IAS)'", nargs='*', help='Authors')

    def add_command(func, **kwargs):
        subparser = subparsers.add_parser(
            func.__name__, **dict(kwargs, help=func.__doc__))
        subparser.set_defaults(func=func)
        return subparser

    cmd = add_command(followup_advocate.authors, parents=[authors])

    cmd = add_command(followup_advocate.compose, parents=[authors])
    cmd.add_argument(
        '-m', '--mailto', action='store_true',
        help='Open new message in default e-mail client [default: false]')
    cmd.add_argument('gracedb_id', metavar='S123456',
                     help='GraceDB ID of superevent')

    cmd = add_command(followup_advocate.compose_RAVEN, parents=[authors])
    cmd.add_argument('gracedb_id', metavar='S123456',
                     help='GraceDB ID of superevent')

    cmd = add_command(followup_advocate.compose_grb_medium_latency,
                      parents=[authors])
    cmd.add_argument('gracedb_id', metavar='E123456', help='GraceDB ID of GRB')

    cmd = add_command(followup_advocate.compose_retraction, parents=[authors])
    cmd.add_argument('gracedb_id', metavar='S123456', help='GraceDB ID')

    cmd = add_command(followup_advocate.compare_skymaps)
    cmd.add_argument(
        'paths', nargs='+', metavar='S123456/filename.fits.gz',
        help='Specify sky maps by GraceDB ID and filename')

    opts = parser.parse_args(args).__dict__
    func = opts.pop('func')
    print(func(**opts))
