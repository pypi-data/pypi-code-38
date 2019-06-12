#!/usr/bin/env python

__author__ = 'pmbarlev'

import pysam
import logging
import argparse
from ExtractBCSR import qual_list_to_string

'''
Overview:
    In a bam file, move the UMI barcode (and quals) from the read name (as appended by ExtractBCSR) to bam tags:
    RX:Z:<UMI barcode> and QX:Z:<quals>

Input:
    A bam in which the read name has the form <Illumina read name>_RX:Z:<UMI barcode>_QX:Z:<barcode quals>

Output:
    A bam in with RX and QX tags (and the tags are removed from the read name)

Arguments:
    --bamIn: The path to the input bam.
    --bamOut: The path to the output bam.
    --logFile: loggging output (optional, default is std-err)

Usage:
    python MoveBC.py \
    --bamIn in.bam \
    --bamOut out.bam


'''

class BCMover(object):
    def __init__(self, bamIn, bamOut):
        '''
        :type bamIn: str
        :type bamOut: str
        '''
        self.reader  = pysam.AlignmentFile(bamIn, "rb")
        '''
        :type pysam.AlignmentFile
        '''
        self.writer = pysam.AlignmentFile(bamOut, "wb", template=self.reader)
        '''
        :type pysam.AlignmentFile
        '''

    def __call__(self):
        num_reads_processed = 0
        for read in self.reader:
            '''
            :type read: pysam.calignedsegment.AlignedSegment
            '''
            name, bc_tag, qt_tag = read.query_name.split("_")
            read.query_name = name
            # set bc tag
            bc_tag_list = bc_tag.split(":")
            read.setTag(bc_tag_list[0], bc_tag_list[2], value_type=bc_tag_list[1])
            # set qt tag
            qt_tag_list = qt_tag.split(":")
            read.setTag(qt_tag_list[0], qual_list_to_string(qt_tag_list[2]), value_type=qt_tag_list[1])
            # write read
            self.writer.write(read)
            num_reads_processed += 1
            if num_reads_processed%1e5 == 0:
                logging.debug("%d reads processed" %num_reads_processed)
        self.reader.close()
        self.writer.close()
        logging.info("%d reads processed" %num_reads_processed)

###### main method ######

def parse_args():
    help_txt = "Move UMI barcode related tags (in a bam) from the read name to tags"
    parser = argparse.ArgumentParser(description=help_txt)

    parser.add_argument('--bamIn', help='Input Bam. use - to read from stdin', required=True)
    parser.add_argument('--bamOut', help='Output bam. Use - to write to stdout', required=False)
    parser.add_argument('--logFile', help='Log File', required=False)

    args = parser.parse_args()
    return args


if __name__ == "__main__":

    # parse command line
    args = parse_args()
    logging_args = {
        "level": logging.DEBUG,
        "filemode": 'w',
        "format": '%(asctime)s %(message)s',
        "datefmt":'%m/%d/%Y %H:%M:%S'
    }

    # set up log file
    if args.logFile is not None:
        logging_args["filename"] = args.logFile
    logging.basicConfig(**logging_args)

    # Do work
    logging.info('MoveBC Program started')
    bc_mover = BCMover(bamIn=args.bamIn, bamOut=args.bamOut)
    bc_mover()
    logging.info('MoveBC Program finished')





