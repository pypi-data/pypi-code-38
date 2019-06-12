#!/usr/bin/env python

import argparse
import logging.config
import os
import shutil

from fastqcReports.settings import DEFAULT_LOG_DIR, PROJECT_NAME
from fastqcReports.reporter import Reporter

logger = logging.getLogger(PROJECT_NAME + '.' + __name__)

def run(run_params):
    rep_output_dir = os.path.join(run_params.fastqc_dir, 'resources')
    if os.path.exists(rep_output_dir ):
        if run_params.force:
            shutil.rmtree(rep_output_dir )
        else:
            assert('The fastqcReports already run on this folder, to overwride the previous results run with --force parameter')
    os.mkdir(rep_output_dir, 0755)
    del run_params.force
    reporter = Reporter(**vars(run_params))
    reporter.run()

def get_options():
    parser = argparse.ArgumentParser(description='Run the fastqcTaxonomy pipeline')
    parser.add_argument('--fastq-dir', type=str, required=True, help='Path to fastq folder')
    parser.add_argument('--fastqc-dir', type=str, required=True, help='Path to fastqc folder')
    parser.add_argument('--paired-end', action='store_true', default=False, help='True or False')
    parser.add_argument('-f', '--force', action='store_true', help='Overwride the previous results')
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
