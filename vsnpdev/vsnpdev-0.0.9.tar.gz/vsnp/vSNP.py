#!/usr/bin/env python3
from vsnp.vsnp_tree_run import VSNPTree
from vsnp.vsnp_vcf_run import VCF
from argparse import ArgumentParser, RawTextHelpFormatter
import multiprocessing
import os

__author__ = 'adamkoziol'
__version__ = '0.0.1'


def vsnp(args):
    """
    Full vSNP pipeline
    """
    vsnp_vcf = VCF(path=args.path,
                   threads=args.threads,
                   debug=args.debug,
                   reference_mapper=args.referencemapper,
                   variant_caller=args.variantcaller,
                   matching_hashes=args.matchinghashes)
    vsnp_vcf.main()
    vsnp_tree = VSNPTree(path=os.path.join(args.path, 'vcf_files'),
                         threads=args.threads,
                         debug=args.debug,
                         filter_positions=args.filterpositions)
    vsnp_tree.main()


def vcf(args):
    """
    VCF creation component of vSNP pipeline
    """
    vsnp_vcf = VCF(path=args.path,
                   threads=args.threads,
                   debug=args.debug,
                   reference_mapper=args.referencemapper,
                   variant_caller=args.variantcaller,
                   matching_hashes=args.matchinghashes)
    vsnp_vcf.main()


def tree(args):
    """
    Phylogenetic tree creation
    """
    vsnp_tree = VSNPTree(path=args.path,
                         threads=args.threads,
                         debug=args.debug,
                         filter_positions=args.filterpositions)
    vsnp_tree.main()


def cli():
    parser = ArgumentParser(
        description='vSNP: bacterial validation SNP analysis tool. USDA APHIS Veterinary Services (VS) Mycobacterium '
                    'tuberculosis complex, mainly M. bovis, and Brucella sp. SNP pipeline. Genotyping from whole '
                    'genome sequence (WGS) outputting BAM, VCF, SNP tables and phylogentic trees.')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s commit {}'.format(__version__))
    subparsers = parser.add_subparsers(title='Available analyses')
    # Create a parental parser from which the subparsers can inherit arguments
    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument('-p', '--path',
                               required=True,
                               type=str,
                               help='Specify path of folder containing files to be processed')
    parent_parser.add_argument('-t', '--threads',
                               default=multiprocessing.cpu_count() - 1,
                               help='Number of threads. Default is the number of cores in the system - 1')
    parent_parser.add_argument('-d', '--debug',
                               action='store_true',
                               help='Allow debug-level logging to be printed to the terminal')
    # Create a subparser to run the VCF creation component of the script
    vcf_subparser = subparsers.add_parser(parents=[parent_parser],
                                          name='vcf',
                                          description='',
                                          formatter_class=RawTextHelpFormatter,
                                          help='Create VCF files from FASTQ inputs')
    vcf_subparser.add_argument('-r', '--referencemapper',
                               choices=['bowtie2', 'bwa'],
                               default='bwa',
                               help='Specify the reference mapper to use. Choices are bwa and bowtie2. Default is bwa')
    vcf_subparser.add_argument('-vc', '--variantcaller',
                               choices=['deepvariant', 'deepvariant-gpu', 'freebayes'],
                               default='freebayes',
                               help='Specify the variant calling software to use. Choices are deepvariant, '
                                    'deepvariant-gpu and freebayes. Default is freebayes')
    vcf_subparser.add_argument('-m', '--matchinghashes',
                               type=int,
                               default=500,
                               help='Minimum number of matching hashes returned from MASH in order for a query Brucella'
                                    ' strain to be successfully matched to a reference strain. Default is 500')
    vcf_subparser.set_defaults(func=vcf)
    # Create a subparser to run the phylogenetic tree creation component of the script
    tree_subparser = subparsers.add_parser(parents=[parent_parser],
                                           name='tree',
                                           description='',
                                           formatter_class=RawTextHelpFormatter,
                                           help='Perform phylogenetic analyses on VCF inputs')
    tree_subparser.add_argument('-f', '--filterpositions',
                                action='store_true',
                                help='Use the Filtered_Regions.xlsx file to filter SNPs')
    vcf_subparser.add_argument('-vc', '--variantcaller',
                               choices=['deepvariant', 'freebayes'],
                               default='freebayes',
                               help='Specify the variant calling software used to create VCF files. '
                                    'Choices are deepvariant and freebayes. Default is freebayes')
    tree_subparser.set_defaults(func=tree)
    # Create a subparser to run the full vSNP pipeline (VCF and subsequent phylogenetic tree creation)
    vsnp_subparser = subparsers.add_parser(parents=[vcf_subparser],
                                           name='vsnp',
                                           description='',
                                           formatter_class=RawTextHelpFormatter,
                                           add_help=False)
    vsnp_subparser.add_argument('-f', '--filterpositions',
                                action='store_true',
                                help='Use the Filtered_Regions.xlsx file to filter SNPs')
    vsnp_subparser.set_defaults(func=vsnp)
    # Get the arguments into an object
    arguments = parser.parse_args()
    # Run the appropriate function for each sub-parser.
    if hasattr(arguments, 'func'):
        arguments.func(arguments)
    # If the 'func' attribute doesn't exist, display the basic help
    else:
        parser.parse_args(['-h'])


if __name__ == '__main__':
    cli()
