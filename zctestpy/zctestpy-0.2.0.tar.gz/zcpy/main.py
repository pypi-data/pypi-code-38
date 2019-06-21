#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import re
import sys

from version import __version__
import basic_data_analysis
import assembly
import pre
import report

def get_arguments():
    """
    Parse the command line arguments.
    """
    parser = argparse.ArgumentParser(usage='Use "python %(prog)s -h/--help" for more information')
    parser.add_argument('-i', '--input', help='Fastq file path or Folder path containing fast5 or fastq files', required=True)
    parser.add_argument('-s', '--strain_list', help='2 columns or 4 columns, a tab-delimited list containing barcodes, strain names and/or PE reads1 path and reads2 path', required=True)
    parser.add_argument('-b', '--barcoding', help='Search for barcodes to demultiplex sequencing data', action='store_true')
    # parser.add_argument('-1', '--short_read1', help='FASTQ file of first short reads in each pair (optional)')
    # parser.add_argument('-2', '--short_read2', help='FASTQ file of second short reads in each pair (optional)')
    parser.add_argument('-g', '--genomesize', help='genome size, <number>[g|m|k], for example: 4800000, 48000k, 4.8m', default=None)
    # parser.add_argument('-p', '--prefix', default='sample', help='Prefix name (default: sample)')
    # parser.add_argument('--format', help='Input file format, fast5 or fastq (default: fastq)', choices=('fast5', 'fastq'), default='fastq')
    parser.add_argument('-t', '--thread', help='use NUM threads (default: 16)', type=int, default=16)
    parser.add_argument('-o', '--outdir', help='Output dir (default: None)', default=None)
    parser.add_argument('--step', help='Analysis steps: only basic data analysis [1], only assembly [2], or basic data analysis and assembly [all]', choices=('1', '2', 'all'), default='all')
    parser.add_argument('-f', '--flowcell', help='Flowcell used during the sequencing run (default: FLO-MIN106)', default='FLO-MIN106')
    parser.add_argument('-k', '--kit', help='Kit used during the sequencing run (default: SQK-LSK109)', default='SQK-LSK109')
    parser.add_argument('--barcode_kit', help='Barcode Kits used during the sequencing run (default: EXP-NBD104)', default='EXP-NBD104')
    parser.add_argument('-q', '--min_quality', help='Filter on a minimum average read quality score (default: 7)', default=7, type=int)
    parser.add_argument('-l', '--min_length', help='Filter on a minimum read length (default: 2000)', default=2000, type=int)
    parser.add_argument('-m', '--max_length', help='Filter on a maximum read length (default: 100000000)', default=100000000, type=int)
    # parser.add_argument('--minreadlength', help='Filter on a maximum read length (default: 100000000)', default=100000000, type=int)
    parser.add_argument('--minoverlaplength', help='Canu assembly: ignore read-to-read overlaps shorter than "number" bases long (default: 500)', default=500, type=int)
    parser.add_argument('-v', '--version', action='version', version=__version__, help="Show program's version number and exit")
    args = parser.parse_args()

    return args


def main():
    args = get_arguments()

    strain_info, columns = pre.pre_list(args.strain_list)

    if columns == 2:
        if args.genomesize is None:
            print('Error: parameter "genomesize" is required when using canu software for long-read-only assembly.\n')
            sys.exit(-1)


    if args.step == '1':
       # Step1: Basci_Data_Analysis
        basic_data_analysis_outdir = os.path.join(args.outdir, '01.Basic_Data_Analysis')

        basic_data_analysis.basic_data_analysis(input=args.input, strain_barcode_dict=strain_info, outdir=basic_data_analysis_outdir, 
            flowcell=args.flowcell, kit=args.kit, barcode_kits=args.barcode_kit,
            thread=args.thread, barcoding=args.barcoding, min_quality=args.min_quality, 
            min_length=args.min_length, max_length=args.max_length)

        os.system('cp {} {}'.format(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'logo.jpg'), basic_data_analysis_outdir))
        report.main(basic_data_analysis_outdir, min_quality=args.min_quality, min_len=args.min_length, max_len=args.max_length)
    elif args.step == '2':
        # Setp1: Assembly (Skip Basic Data Analysis)

        assembly_outdir = os.path.join(args.outdir, '02.Assembly')

        if not os.path.isdir(assembly_outdir):
            os.makedirs(assembly_outdir)

        assembly.assembly_one(args.input, strain_info=strain_info, thread=args.thread, genomesize=args.genomesize, outdir=assembly_outdir, minReadLength=args.min_length, minOverlapLength=args.minoverlaplength)
        # Step3:     
        assembly.annotation(strain_info, args.outdir)
    else:
        # Step1: Basci_Data_Analysis
        basic_data_analysis_outdir = os.path.join(args.outdir, '01.Basic_Data_Analysis')

        basic_data_analysis.basic_data_analysis(input=args.input, strain_barcode_dict=strain_info, outdir=basic_data_analysis_outdir, 
            flowcell=args.flowcell, kit=args.kit, barcode_kits=args.barcode_kit,
            thread=args.thread, barcoding=args.barcoding, min_quality=args.min_quality, 
            min_length=args.min_length, max_length=args.max_length)

        os.system('cp {} {}'.format(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'logo.jpg'), basic_data_analysis_outdir))

        report.main(basic_data_analysis_outdir, min_quality=args.min_quality, min_len=args.min_length, max_len=args.max_length)

        # Step2: Assembly
        assembly_outdir = os.path.join(args.outdir, '02.Assembly')

        if not os.path.isdir(assembly_outdir):
            os.makedirs(assembly_outdir)

        if args.barcoding:
            nanopore_fq_file = os.path.join(basic_data_analysis_outdir, 'barcode_demultiplexing_data')
        else:
            nanopore_fq_file = basic_data_analysis_outdir
        assembly.assembly_all(nanopore_fq_file, strain_info=strain_info, thread=args.thread, genomesize=args.genomesize, outdir=assembly_outdir, minReadLength=args.min_length, minOverlapLength=args.minoverlaplength)

        # Step3:     
        assembly.annotation(strain_info, args.outdir)

if __name__ == '__main__':
    main()
