#!/usr/bin/env python

import argparse
import logging
import os

__author__ = 'Refael Kohen'

'''
SinglecellUtils: Utils for singlecell pipeline

Arguments:
    --pipeline-dir: Working directory of the pipeline
    --samples: Space separator list of the samples names.
    --step: Step of the pipeline. For example: 2_aggregation
    --logFile: (optional) Where the log file should be written.
'''


class CellRangerUtils(object):
    def __init__(self, samples_list, path_to_cellranger_analysis_dir, output_file):
        '''
        :type samples_list: list
        :type path_to_cellranger_analysis: str
        :type output_path
        '''
        self.samples_list = samples_list
        self.path_to_cellranger_analysis_dir = path_to_cellranger_analysis_dir
        self.output_file = output_file

    def create_input_for_aggregation(self):
        with open(self.output_file, 'w') as out_file:
            out_file.write("library_id,molecule_h5\n")
            for sample in self.samples_list:
                out_file.write(','.join([sample, os.path.join(self.path_to_cellranger_analysis_dir, sample, 'outs',
                                                             'molecule_info.h5\n')]))



###### main methods #####

def parse_args():
    help_txt = "Create utils files for single cell analysis."
    parser = argparse.ArgumentParser(description=help_txt)
    parser.add_argument('--pipeline-dir', type=str, help='Working directory of the pipeline', required=True)
    parser.add_argument('--samples', type=str, nargs='+', help='Space separator list of the samples names',
                        required=True)
    parser.add_argument('--step', type=str, help='Create files for this step of the pipeline', required=True)
    parser.add_argument('--logFile', help='Log File', required=False)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    # parse command line
    args = parse_args()
    logging_args = {
        "level": logging.DEBUG,
        "filemode": 'w',
        "format": '%(asctime)s %(message)s',
        "datefmt": '%m/%d/%Y %H:%M:%S'
    }

    # set up log file
    if args.logFile is not None:
        logging_args["filename"] = args.logFile
    logging.basicConfig(**logging_args)

    if args.step == '2_aggregation':
        try:
            output_file = os.path.join(args.pipeline_dir, '2_aggregation', 'list.csv')
            path_to_cellranger_analysis_dir = os.path.join(args.pipeline_dir, '1_count')
            CellRangerUtils(args.samples, path_to_cellranger_analysis_dir, output_file).create_input_for_aggregation()
        except Exception as e:
            logging.info(e.message)

