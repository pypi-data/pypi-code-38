import argparse
import os
import zipfile

from fastr.utils.cmd import add_parser_doc_link


def get_parser():
    parser = argparse.ArgumentParser(
        description="Create a dump of a network run directory that contains the"
                    " most important information for debugging. This includes a"
                    " serialization of the network, all the job command and"
                    " result files, the extra job information files and the "
                    " provenance files. No data files will be included, but note"
                    " that if jobs get sensitive information passed via the "
                    " command line this will be included in the job files.")
    parser.add_argument('indir', metavar='RUNDIR',
                        help='The run directory to dump')
    parser.add_argument('outfile', metavar='DUMP.zip',
                        help='The file to place the dump in')
    return parser


def create_zip(directory, output_file):
    with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(os.path.join(directory, './__sink_data__.json'), './__sink_data__.json')
        for path, _, files in os.walk(directory):
            for filename in files:
                if filename.startswith('__fastr'):
                    file_path = os.path.join(path, filename)
                    relative_path = file_path.replace(directory, './', 1)
                    zip_file.write(file_path, relative_path)


def main():
    """
    Dump the contents of a network run tempdir into a zip for remote assistance
    """
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    create_zip(args.indir, args.outfile)


if __name__ == '__main__':
    main()
