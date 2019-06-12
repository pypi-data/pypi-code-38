#!/usr/bin/env python

import argparse
import logging.config
import os

from fastqcReports.settings import DEFAULT_LOG_DIR, PROJECT_NAME
from fastqcReports.reporter import Reporter

logger = logging.getLogger(PROJECT_NAME + '.' + __name__)

def run(run_params):
    outfile_base = run_params.output_file_base
    run_params.fastq_dir = ''
    del run_params.output_file_base
    reporter = Reporter(**vars(run_params))
    reporter.write_table(outfile_base)


def get_options():
    parser = argparse.ArgumentParser(description='Run the fastqcTaxonomy pipeline')
    parser.add_argument('--fastqc-dir', type=str, required=True, help='Path to fastqc folder')
    parser.add_argument('--paired-end', action='store_true', default=False, help='True or False')
    parser.add_argument('--output-file-base', type=str, required=True, help='Path to output file')
    parser.add_argument('--log-dir', type=str, required=False, default=DEFAULT_LOG_DIR,
                        help='Write log files to this directory')
    parser.add_argument('--logging_config', type=str, required=False,
                        help='Load logging configuration from this file (overrides default settings)')
    args = parser.parse_args()
    return args

def main():
    args = get_options()
    if args.logging_config:
        print("Loading logging configuration from file: %s" % args.logging_config)
        assert os.path.isfile(args.logging_config), 'Could not find logging configuration file %s' % args.logging_config
        logging.config.fileConfig(args.logging_config)
    else:
        from fastqcReports.logging_conf import add_run_log_handlers
        add_run_log_handlers(logs_dir=DEFAULT_LOG_DIR)
    del args.logging_config
    del args.log_dir
    run(args)

if __name__ == "__main__":
    main()
