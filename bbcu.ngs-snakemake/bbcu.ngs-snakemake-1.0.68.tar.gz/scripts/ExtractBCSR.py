#!/usr/bin/env python

import argparse
import collections
import gzip
import logging
import re
import sys

import pysam

__author__ = 'pmbarlev'
'''
ExtractBCSR: "Extract BarCode Single Read"

Overview: Extract UMI barcodes from the seq field fastq file, and append them to the readname field. Supports single-read sequencing in which sequences are in read1 and the UMI barcodes are either part of the sequence, or in read2.

Output: a fastq file in which the following bam tags are appended to the readName line:
   barcode: in the tag RX:Z:[barcode]
   quals in tag QX:Z:[qual]

Optionally, collect barcode frequency histogram in csv format.

Remark: It is considerably faster to write to a non-gzipped fastq file.

Arguments:
    --fastqIn: Input fastq with sequenced reads
    --fastqOut: Name of the fastq to be written.
    --fastqUMI: (optional) Name of the fastq file containing the UMI barcodes. The order of reads must match fastqIn.
    --bcHistFileName: (optional) Name of file where the barcode frequency file should be written.
    --logFile: (optional) Where the log file should be written.

Typical Usage:

python ExtractBCSR.py \
--fastqIn input/myfastq.R1.fastq \
--fastqOut expected_out/myfastq.bcExt.R1.fastq \
--fastqUMI input/myfastq.R2.fastq \
--bcHistFileName hist.csv


Generated metrics files: Optionally, a histrogram conataining the number of appearances of each UMI barcode can be generated. E.g.,
    ...
    CATGTTGA,11
    CATCAGCAT,1
    CGGGTGCGG,62
    ...

 Note: since this data is collected prior to de-Duplication it is of very limited utility.
'''


class BCExtractor(object):
    def __init__(self, fastq_in_name, fastq_out_name, umi_fastq_name=None):
        '''
        :type fastq_in_name: str
        :type fastq_out_name: str
        :type bc_length: int
        :type umi_fastq_name: str
        '''

        # Set input variables
        self.has_umi_fastq = (umi_fastq_name is not None)
        # Set file readers and writers. Determine if input/output bam is gzipped, and initialize file reader
        # appropriately
        # read 1
        self.r1_fq_reader = pysam.FastxFile(fastq_in_name)
        # It doesn't seem that pysam has a fastq writing object
        if not fastq_out_name:
            self.r1_fq_writer = sys.stdout
        else:
            self.r1_fq_writer = gzip.open(fastq_out_name, 'w') if fastq_out_name.endswith(".gz") else \
                open(fastq_out_name, 'w')

        # read 2
        if self.has_umi_fastq:
            self.r2_fq_reader = pysam.FastxFile(umi_fastq_name)

        # Set counters
        self.bc_hist = collections.Counter()
        self.num_reads_processed = 0
        self.num_barcodes_seen = 0
        self.no_bc_found = 0

    def __call__(self):
        if self.has_umi_fastq:
            logging.info("Processing UMI from R2 (UMI fastq)")
        else:
            logging.info("Processing UMI from R1")

        # Traverse fastq files
        for seq_read in self.r1_fq_reader:
            umi_read = self.r2_fq_reader.next() if self.has_umi_fastq else seq_read
            # Check sure that the readnames match (in case the fastqs aren't in order)
            if seq_read.name != umi_read.name:
                raise ValueError("%d 'th read names do not match: read_seq %s, and umi_seq %s" % (
                self.num_reads_processed + 1, seq_read.name, umi_read.name))
            out_read = self.process_read(seq_read, umi_read)
            self.r1_fq_writer.write(out_read.__str__() + "\n")

            # Log progress
            self.num_reads_processed += 1
            if self.num_reads_processed % 100000 == 0:
                logging.info("%d Reads processed" % self.num_reads_processed)

        # Close file handles
        self.r1_fq_reader.close()
        self.r1_fq_writer.close()
        if self.has_umi_fastq:
            self.r2_fq_reader.close()

        # Log summary stats
        logging.info("Done. %d reads processed." % self.num_reads_processed)
        logging.info("%d distinct barcodes seen." % len(self.bc_hist.keys()))
        logging.info("%d reads missing barcodes" % self.no_bc_found)

    ### Read processing ###

    def process_read(self, seq_read, umi_read):
        """
        :type seq_read: pysam.cfaidx.FastqProxy
        :type umi_read: pysam.cfaidx.FastqProxy
        :rtype: pysam.cfaidx.FastqProxy
        """
        bc_regex = "(^.{8})"  # New version of fastq files: R2 contains only the UMI in start of the read without the barcode
        if len(umi_read.sequence) == 15: # Old version of fastq files: R2 contain sample barcode (7 bases) and then 8 bases of the UMI.
            bc_regex = ".{7}(.{8})"
        match = re.match(bc_regex, umi_read.sequence)
        if not match:
            self.no_bc_found += 1
        else:
            bc = match.group(1)
            bc_quals = umi_read.quality[match.start(1): match.end(1)]

            # Trim the barcode from the read, if it is in read 1
            if not self.has_umi_fastq:
                seq_read.sequence = seq_read.sequence[0:match.start(1)] + seq_read.sequence[match.end(1):]
                seq_read.quality = seq_read.quality[0:match.start(1)] + seq_read.quality[match.end(1):]

            # Insert bc and bc_quals into the read name
            # We convert bc_qual to a list so that mappers don't trim the read names
            seq_read.name += "_RX:Z:%s_QX:Z:%s" % (bc, qual_string_to_list(bc_quals))
            self.bc_hist[bc] += 1

        return seq_read

    # Write a csv file containing the histogram of the barcodes seen.
    def write_hist(self, hist_file_name):
        with open(hist_file_name, 'w') as histWriter:
            for bc in sorted(self.bc_hist.keys()):
                histWriter.write(bc + "," + str(self.bc_hist[bc]) + "\n")


###### Util ######

# A function which converts a qual string (ascii code +33) to a comma separated list of numbers.
# E.g., "E/6" -> "36,14,21"
# The reason for using this function is that many mappers (including TopHat and STAR) trim after certain characters in the read name (to which we append the qual tag)
def qual_string_to_list(qual_string):
    return ",".join(map(lambda c: str(ord(c) - 33), list(qual_string)))


# And the inverse
def qual_list_to_string(qual_list):
    return "".join(map(lambda i: chr(int(i) + 33), qual_list.split(",")))


###### main method #####

def parse_args():
    help_txt = "Extract UMI barcodes from R1 or R2 seq, and append to read 1 read-name"
    parser = argparse.ArgumentParser(description=help_txt)

    parser.add_argument('--fastqIn', help='Input Fastq', required=True)
    parser.add_argument('--fastqUMI', help='umi Fastq', required=False)
    parser.add_argument('--fastqOut',
                        help='Output Fastq Filename. If no path is given, output will be written to stdout (for piping)',
                        default=None, required=False)
    parser.add_argument('--bcHistFileName', help='Filename for barcode histogram file', required=False)
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
        "datefmt": '%m/%d/%Y %H:%M:%S'
    }

    # set up log file
    if args.logFile is not None:
        logging_args["filename"] = args.logFile
    logging.basicConfig(**logging_args)

    # Do work
    logging.info('Program started')
    BC_extractor = BCExtractor(args.fastqIn, args.fastqOut, umi_fastq_name=args.fastqUMI)
    BC_extractor()
    # Write bc histogram
    if args.bcHistFileName:
        BC_extractor.write_hist(args.bcHistFileName)
        logging.info("Barcode histogram written to " + args.bcHistFileName)
