from __future__ import print_function, absolute_import, unicode_literals
import glob
import os
import multiprocessing
import lxml.etree as et
from ilabs.client.ilabs_predictor import ILabsPredictor
import logging


BRS_S = '{http://innodatalabs.com/brs}s'  # BRS label tag from BRS specs


def predict_file(domain, input_filename, output_filename, user_key, strip_labels):
    '''
    Executes prediction on a file content, and saves result to output file
    '''
    predictor = ILabsPredictor.init(domain, user_key=user_key)

    try:
        with open(input_filename, 'rb') as f:
            input_bytes = f.read()
            if strip_labels:
                xml = et.fromstring(input_bytes)
                et.strip_tags(xml, BRS_S)
                input_bytes = et.tostring(
                    xml,
                    xml_declaration=True,
                    encoding='utf-8'
                )

        output_bytes = predictor(input_bytes)

        with open(output_filename, 'wb') as f:
            f.write(output_bytes)

    except RuntimeError as e:
        return e


def missing_files(input_dir, output_dir):
    '''
    Finds files that are present in the "input_dir", but missing from the
    "output_dir"
    '''
    input_names = {
        os.path.basename(x)
        for x in glob.glob(input_dir + '/*') if os.path.isfile(x)
    }

    output_names = {
        os.path.basename(x)
        for x in glob.glob(output_dir + '/*') if os.path.isfile(x)
    }

    return sorted(input_names - output_names)


def ilabs_bulk_upload(
    domain,
    input,
    output,
    user_key=None,
    strip_labels=False,
    verbose=0
):
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)

    if os.path.isfile(input):
        if os.path.isdir(output):
            raise RuntimeError('When input is a single file, output is expected to be a file too. But its a directory: ' + output)
        elif os.path.isfile(output):
            print('Output file exists, nothing to do: ' + output)
            return

        error = predict_file(domain, input, output, user_key, strip_labels)
        print(os.path.basename(output), error or 'OK')

        return

    if not os.path.isdir(input):
        raise RuntimeError('Input file/directory does not exist: ' + input)

    if os.path.isfile(output):
        raise RuntimeError('When input is directory, output is expected to be a directory. But its a file: ' + output)

    if not os.path.exists(output):
        os.mkdir(output)
        print('Created output directory: ' + output)

    fileset = missing_files(input, output)
    if not fileset:
        return

    for fname in fileset:
        error = predict_file(
            domain,
            os.path.join(input, fname),
            os.path.join(output, fname),
            user_key,
            strip_labels
        )

        print(fname, error or 'OK')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Sends all files from the input '
                    'directory to prediction service and '
                    'places result in the output directory')

    parser.add_argument('--domain', '-d', required=True,
                        help='Prediction domain')
    parser.add_argument('--user_key', '-u', help='Secret user key')
    parser.add_argument('input',
                        help='Input file or directory')
    parser.add_argument('output',
                        help='Output file or directory')
    parser.add_argument('--strip_labels', '-s', action='store_true',
                        help='If set, assumes that files are BRS and '
                        'strips off <brs:s> labels before sending')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Increases verbosity. Use multiple times to get even more verbose')

    args = parser.parse_args()

    ilabs_bulk_upload(**args.__dict__)


if __name__ == '__main__':
    main()
