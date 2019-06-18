import argparse
import os
import subprocess

from fastr.utils.cmd import add_parser_doc_link


def get_parser():
    parser = argparse.ArgumentParser(
        description="Run pylint in such a way that the output is written to a file")
    parser.add_argument('--output_file', metavar='PYLINT.OUT', required=True, type=str,
                        help='The file to result in')
    return parser


def run_pylint(out_file, pylint_args):
    print('Saving result to {}'.format(out_file))
    with open(out_file, 'w') as fh_out:
        print('Running: pylint {}'.format(' '.join(pylint_args)))
        proc = subprocess.Popen(['pylint'] + pylint_args, stdout=fh_out)
        proc.wait(timeout=600)  # Max 10 minutes


def main():
    """
    Tiny wrapper in pylint so the output can be saved to a file (for test automation)
    """
    parser = add_parser_doc_link(get_parser(), __file__)
    args, unknown = parser.parse_known_args()
    output_file = os.path.abspath(args.output_file)
    run_pylint(output_file, unknown)


if __name__ == '__main__':
    main()
