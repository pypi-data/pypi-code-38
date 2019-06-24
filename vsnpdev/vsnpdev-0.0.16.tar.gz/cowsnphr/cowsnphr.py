#!/usr/bin/env python3
from accessoryFunctions.accessoryFunctions import run_subprocess, SetupLogging, write_to_logfile
from vsnp.vsnp_vcf_methods import VCFMethods
from vsnp.vsnp_tree_methods import VSNPTreeMethods
from Bio import SeqIO
from argparse import ArgumentParser
from pathlib import Path
import multiprocessing
from glob import glob
import pkg_resources
import logging
import os

__author__ = 'adamkoziol'


class COWSNPhR(object):

    def main(self):
        self.fastq_manipulation()
        self.reference_mapping()
        self.snp_calling()
        self.load_snps()
        self.phylogenetic_trees()
        self.annotate_snps()
        self.order_snps()
        self.create_report()

    def fastq_manipulation(self):
        """
        Determine the number of strains to process. Create strain-specific working directories with relative symlinks
        to FASTQ files
        """
        logging.info('Locating FASTQ files, creating strain-specific working directories and symlinks to files')
        fastq_files = VCFMethods.file_list(path=self.seq_path)
        logging.debug('FASTQ files: \n{fastq_files}'.format(fastq_files='\n'.join(fastq_files)))
        strain_folder_dict = VCFMethods.strain_list(fastq_files=fastq_files)
        self.strain_name_dict = VCFMethods.strain_namer(strain_folders=strain_folder_dict)
        logging.debug('Strain names: \n{strain_names}'.format(strain_names='\n'.join(sorted(self.strain_name_dict))))
        self.strain_fastq_dict = VCFMethods.file_link(strain_folder_dict=strain_folder_dict,
                                                      strain_name_dict=self.strain_name_dict)
        logging.debug(
            'Strain-specific symlinked FASTQ files: \n{symlinks}'.format(
                symlinks='\n'.join(['{strain_name}: {fastq_files}'.format(strain_name=sn, fastq_files=ff)
                                    for sn, ff in self.strain_fastq_dict.items()])))

    def reference_mapping(self):
        """
        Perform reference mapping with bowtie2, and attempt to assemble any unmapped reads into contigs with SKESA
        """
        logging.info('Extracting paths to reference genomes')
        self.ref_file()
        logging.info('Running bowtie2 build')
        strain_bowtie2_index_dict, self.strain_reference_abs_path_dict, self.strain_reference_dep_path_dict = \
            VCFMethods.bowtie2_build(reference_link_path_dict=self.reference_link_path_dict,
                                     dependency_path=self.ref_path,
                                     logfile=self.logfile)
        logging.info('Running bowtie2 reference mapping')
        self.strain_sorted_bam_dict = VCFMethods.bowtie2_map(
            strain_fastq_dict=self.strain_fastq_dict,
            strain_name_dict=self.strain_name_dict,
            strain_bowtie2_index_dict=strain_bowtie2_index_dict,
            threads=self.threads,
            logfile=self.logfile)
        logging.debug('Sorted BAM files: \n{files}'.format(
                files='\n'.join(['{strain_name}: {bam_file}'.format(strain_name=sn, bam_file=bf)
                                 for sn, bf in self.strain_sorted_bam_dict.items()])))
        logging.info('Indexing sorted BAM files')
        VCFMethods.samtools_index(strain_sorted_bam_dict=self.strain_sorted_bam_dict,
                                  strain_name_dict=self.strain_name_dict,
                                  threads=self.threads,
                                  logfile=self.logfile)

    def ref_file(self):
        """
        reference_link_path_dict: Dictionary of strain name: relative path to symlinked reference genome
        :return:
        """
        for strain_name in self.strain_name_dict:
            fasta = glob(os.path.join(self.ref_path, '*.fasta'))[0]
            self.reference_link_path_dict[strain_name] = fasta
            self.strain_consolidated_ref_dict[strain_name] = os.path.basename(os.path.splitext(fasta)[0])

    def snp_calling(self):
        """
        Prep files for SNP calling. Use deepvariant to call SNPs. Parse the outputs from deepvariant
        """
        logging.info('Preparing files for SNP calling with deepvariant make_examples')
        strain_examples_dict, strain_variant_path_dict, strain_gvcf_tfrecords_dict = \
            VCFMethods.deepvariant_make_examples(strain_sorted_bam_dict=self.strain_sorted_bam_dict,
                                                 strain_name_dict=self.strain_name_dict,
                                                 strain_reference_abs_path_dict=self.strain_reference_abs_path_dict,
                                                 vcf_path=os.path.join(self.seq_path, 'vcf_files'),
                                                 home=self.home,
                                                 logfile=self.logfile,
                                                 threads=self.threads,
                                                 working_path=self.working_path)
        logging.info('Calling variants with deepvariant call_variants')
        strain_call_variants_dict = \
            VCFMethods.deepvariant_call_variants_multiprocessing(strain_variant_path_dict=strain_variant_path_dict,
                                                                 strain_name_dict=self.strain_name_dict,
                                                                 dependency_path=self.dependency_path,
                                                                 vcf_path=os.path.join(self.seq_path, 'vcf_files'),
                                                                 home=self.home,
                                                                 threads=self.threads,
                                                                 logfile=self.logfile,
                                                                 working_path=self.working_path)
        logging.info('Creating VCF files with deepvariant postprocess_variants')
        self.strain_vcf_dict = \
            VCFMethods.deepvariant_postprocess_variants(
                strain_call_variants_dict=strain_call_variants_dict,
                strain_variant_path_dict=strain_variant_path_dict,
                strain_name_dict=self.strain_name_dict,
                strain_reference_abs_path_dict=self.strain_reference_abs_path_dict,
                strain_gvcf_tfrecords_dict=strain_gvcf_tfrecords_dict,
                vcf_path=os.path.join(self.seq_path, 'vcf_files'),
                home=self.home,
                logfile=self.logfile,
                working_path=self.working_path)
        logging.info('Copying gVCF files to common folder')
        VCFMethods.copy_vcf_files(strain_vcf_dict=self.strain_vcf_dict,
                                  vcf_path=os.path.join(self.seq_path, 'vcf_files'))

    def load_snps(self):
        logging.info('Parsing gVCF files')
        self.strain_parsed_vcf_dict, self.strain_best_ref_dict, self.strain_best_ref_set_dict = \
            VSNPTreeMethods.load_vcf(strain_vcf_dict=self.strain_vcf_dict,
                                     threads=self.threads)
        logging.debug('Parsed gVCF summaries:')
        if self.debug:
            pass_dict, insertion_dict, deletion_dict = \
                VSNPTreeMethods.summarise_vcf_outputs(strain_parsed_vcf_dict=self.strain_parsed_vcf_dict)

            logging.debug('SNP bases: \n{results}'.format(
                results='\n'.join(['{strain_name}: {pass_filter}'.format(strain_name=sn, pass_filter=ps)
                                   for sn, ps in pass_dict.items()])))
            logging.debug('Inserted bases: \n{results}'.format(
                results='\n'.join(['{strain_name}: {insertion_calls}'.format(strain_name=sn, insertion_calls=ic)
                                   for sn, ic in insertion_dict.items()])))
            logging.debug('Deleted bases: \n{results}'.format(
                results='\n'.join(['{strain_name}: {deletion_calls}'.format(strain_name=sn, deletion_calls=dc)
                                   for sn, dc in deletion_dict.items()])))
        logging.info('Loading SNP positions')
        consolidated_ref_snp_positions, strain_snp_positions, self.ref_snp_positions = \
            VSNPTreeMethods.load_snp_positions(strain_parsed_vcf_dict=self.strain_parsed_vcf_dict,
                                               strain_consolidated_ref_dict=self.strain_consolidated_ref_dict)
        group_positions_set = self.group_strains(strain_snp_positions=strain_snp_positions)
        logging.debug('Number of SNPs per contig:')
        if self.debug:
            for species_code, group_dict in group_positions_set.items():
                for group, ref_dict in group_dict.items():
                    for ref_chrom, pos_set in ref_dict.items():
                        if pos_set:
                            print(ref_chrom, len(pos_set))
        logging.info("Performing SNP density filtering")
        filtered_group_positions = VSNPTreeMethods.filter_snps(group_positions_set=group_positions_set,
                                                               threshold=3)
        if self.debug:
            logging.debug('Number of SNPs per contig following density filtering:')
            for species_code, group_dict in filtered_group_positions.items():
                for group, ref_dict in group_dict.items():
                    for ref_chrom, pos_set in ref_dict.items():
                        if pos_set:
                            print(ref_chrom, len(pos_set))
        logging.info('Loading SNP sequences')
        self.group_strain_snp_sequence, self.species_group_best_ref = \
            VSNPTreeMethods.load_snp_sequence(strain_parsed_vcf_dict=self.strain_parsed_vcf_dict,
                                              strain_consolidated_ref_dict=self.strain_consolidated_ref_dict,
                                              group_positions_set=filtered_group_positions,
                                              strain_groups=self.strain_groups,
                                              strain_species_dict=self.strain_species_dict,
                                              consolidated_ref_snp_positions=consolidated_ref_snp_positions)
        logging.info('Creating multi-FASTA files of core SNPs')
        group_folders, species_folders, self.group_fasta_dict = \
            VSNPTreeMethods.create_multifasta(group_strain_snp_sequence=self.group_strain_snp_sequence,
                                              fasta_path=self.fasta_path,
                                              group_positions_set=filtered_group_positions,
                                              nested=False)
        logging.debug('Multi-FASTA alignment output:')
        if self.debug:
            for species_code, group_dict in self.group_fasta_dict.items():
                for group, fasta_file in group_dict.items():
                    print(fasta_file)

    def group_strains(self, strain_snp_positions):
        """
        Find all the SNP positions present in the strains in each group
        :param strain_snp_positions: type DICT: Dictionary of strain name: ref chromosome: positions
        :return: group_positions_set: Dictionary of species: group: reference chromosome name: positions
        """
        # Initialise a dictionary to store group-specific SNP positions for each reference chromosome
        group_positions_set = dict()
        # In order to re-use code, the species and group must be provided. Use generic values
        species = 'species'
        group = 'group'
        for strain_name in strain_snp_positions:
            self.strain_groups[strain_name] = [group]
            self.strain_species_dict[strain_name] = species
            for ref_chrom, pos_list in sorted(strain_snp_positions[strain_name].items()):
                # Initialise the species key in the dictionary if required
                if species not in group_positions_set:
                    group_positions_set[species] = dict()
                # Initialise the group key in the dictionary if required
                if group not in group_positions_set[species]:
                    group_positions_set[species][group] = dict()
                if ref_chrom not in group_positions_set[species][group]:
                    group_positions_set[species][group][ref_chrom] = set()
                # Add the group-specific positions to the set
                for pos in pos_list:
                    group_positions_set[species][group][ref_chrom].add(pos)
        return group_positions_set

    def phylogenetic_trees(self):
        """
        Create, parse, and copy phylogenetic trees
        """
        logging.info('Creating phylogenetic trees with FastTree')
        species_group_trees = self.run_fasttree(group_fasta_dict=self.group_fasta_dict,
                                                strain_consolidated_ref_dict=self.strain_consolidated_ref_dict,
                                                strain_groups=self.strain_groups,
                                                logfile=self.logfile)
        logging.info('Parsing strain order from phylogenetic trees')
        self.species_group_order_dict = VSNPTreeMethods.parse_tree_order(species_group_trees=species_group_trees)
        logging.info('Copying phylogenetic trees to {tree_path}'.format(tree_path=self.tree_path))
        VSNPTreeMethods.copy_trees(species_group_trees=species_group_trees,
                                   tree_path=self.tree_path)

    @staticmethod
    def run_fasttree(group_fasta_dict, strain_consolidated_ref_dict, strain_groups, logfile):
        """
        Create maximum-likelihood tree using FastTree
        :param group_fasta_dict: type DICT: Dictionary of species code: group name: FASTA file created for the group
        :param strain_consolidated_ref_dict: type DICT: Dictionary of strain name: extracted reference genome name
        :param strain_groups: type DICT: Dictionary of strain name: list of group(s) for which the strain contains the
        defining SNP
        :param logfile: type STR: Absolute path to logfile basename
        :return: species_group_trees: Dictionary of species code: group name: dictionary of tree type: absolute path
        to FastTree output tree
        """
        # Initialise a dictionary to store the absolute paths of the output trees
        species_group_trees = dict()
        for species, group_dict in group_fasta_dict.items():
            # Initialise the species key in the dictionary if necessary
            if species not in species_group_trees:
                species_group_trees[species] = dict()
            for strain_name, best_ref in strain_consolidated_ref_dict.items():
                for group, fasta_file in group_dict.items():
                    if group in strain_groups[strain_name]:
                        # Initialise the group key in the dictionary if necessary
                        if group not in species_group_trees[species]:
                            species_group_trees[species][group] = dict()
                        # Set the path of the working dir
                        output_dir = os.path.dirname(fasta_file)
                        best_tree = os.path.join(output_dir,
                                                 '{species}_{group}.tre'
                                                 .format(species=species,
                                                         group=group))
                        species_group_trees[species][group]['best_tree'] = best_tree
                        # Create a system call to FastTree
                        fasttree_cmd = 'FastTree -gamma  -nt {fasta_file} > {tree_file}'\
                            .format(fasta_file=fasta_file,
                                    tree_file=best_tree)
                        # Run the system call if the output best tree doesn't already exist
                        if not os.path.isfile(best_tree):
                            out, err = run_subprocess(command=fasttree_cmd)
                            # Write the stdout and stderr to the main logfiles
                            write_to_logfile(out=out,
                                             err=err,
                                             logfile=logfile)
        return species_group_trees

    def annotate_snps(self):
        """
        Load GenBank files, and annotate SNPs
        """
        logging.info('Loading GenBank files for closest reference genomes')
        self.load_genbank_file(reference_link_path_dict=self.reference_link_path_dict)
        logging.info('Annotating SNPs')
        self.species_group_annotated_snps_dict = \
            VSNPTreeMethods.annotate_snps(group_strain_snp_sequence=self.group_strain_snp_sequence,
                                          full_best_ref_gbk_dict=self.full_best_ref_gbk_dict,
                                          strain_best_ref_set_dict=self.strain_best_ref_set_dict,
                                          ref_snp_positions=self.ref_snp_positions)

    def load_genbank_file(self, reference_link_path_dict):
        """
        Use SeqIO to parse the best reference genome GenBank file for annotating SNP locations
        :param reference_link_path_dict: type DICT: Dictionary of strain name: relative path to reference genome
        dependency folder
        :return: full_best_ref_gbk_dict: Dictionary of best ref: ref position: SeqIO parsed GenBank file-sourced
        records from closest reference genome for that position
        """
        # Initialise a dictionary to store the SeqIO parsed GenBank files
        best_ref_gbk_dict = dict()
        for strain_name, best_ref_file in reference_link_path_dict.items():
            best_ref_path = os.path.dirname(best_ref_file)
            best_ref = os.path.splitext(best_ref_file)[0]
            gbk_file = glob(os.path.join(best_ref_path, '{br}*.gbk'.format(br=best_ref)))[0]
            # Only parse the file if it has not already been parsed
            if best_ref not in best_ref_gbk_dict:
                # Use SeqIO to first parse the GenBank file, and convert the parsed object to a dictionary
                gbk_dict = SeqIO.to_dict(SeqIO.parse(gbk_file, "genbank"))
                # Add the GenBank dictionary to the best reference-specific dictionary
                best_ref_gbk_dict[best_ref] = gbk_dict
        for best_ref, gbk_dict in best_ref_gbk_dict.items():
            self.full_best_ref_gbk_dict[best_ref] = dict()
            for ref_name, record in gbk_dict.items():
                if record.name not in self.full_best_ref_gbk_dict:
                    self.full_best_ref_gbk_dict[record.name] = dict()
                for feature in record.features:
                    # Ignore the full record
                    if feature.type != 'source':
                        # Iterate through the full length of the feature, and add each position to the dictionary
                        for i in range(int(feature.location.start), int(feature.location.end) + 1):
                            self.full_best_ref_gbk_dict[record.name][i] = feature
        return self.full_best_ref_gbk_dict

    def order_snps(self):
        """
        Order the SNPs based on prevalence and phylogeny
        """
        logging.info('Counting prevalence of SNPs')
        species_group_snp_num_dict = \
            VSNPTreeMethods.determine_snp_number(group_strain_snp_sequence=self.group_strain_snp_sequence,
                                                 species_group_best_ref=self.species_group_best_ref)
        logging.debug('SNP prevalence')
        if self.debug:
            for ref_chrom, pos_dict in species_group_snp_num_dict['species']['group'].items():
                print(ref_chrom, pos_dict)
        logging.info('Ranking SNPs based on prevalence')
        species_group_snp_rank, self.species_group_num_snps = \
            VSNPTreeMethods.rank_snps(species_group_snp_num_dict=species_group_snp_num_dict)
        logging.debug('Ranked SNPs')
        if self.debug:
            for num_snps, ref_dict in sorted(species_group_snp_rank['species']['group'].items(), reverse=True):
                for ref_chrom, pos_dict in ref_dict.items():
                    print(num_snps, ref_chrom, pos_dict)
        logging.info('Sorting SNPs based on order of strains in phylogenetic trees')
        self.species_group_sorted_snps = \
            VSNPTreeMethods.sort_snps(species_group_order_dict=self.species_group_order_dict,
                                      species_group_snp_rank=species_group_snp_rank,
                                      species_group_best_ref=self.species_group_best_ref,
                                      group_strain_snp_sequence=self.group_strain_snp_sequence)
        logging.debug('Sorted SNPs')
        if self.debug:
            for num_snps, ref_dict in self.species_group_sorted_snps['species']['group'].items():
                for ref_chrom, pos_dict in ref_dict.items():
                    print(num_snps, ref_chrom, pos_dict)

    def create_report(self):
        """
        Create the summary report of the analyses
        """
        logging.info('Creating summary tables')
        VSNPTreeMethods.create_summary_table(species_group_sorted_snps=self.species_group_sorted_snps,
                                             species_group_order_dict=self.species_group_order_dict,
                                             species_group_best_ref=self.species_group_best_ref,
                                             group_strain_snp_sequence=self.group_strain_snp_sequence,
                                             species_group_annotated_snps_dict=self.species_group_annotated_snps_dict,
                                             species_group_num_snps=self.species_group_num_snps,
                                             summary_path=self.summary_path)

    def __init__(self, seq_path, ref_path, threads, working_path, debug):
        # Determine the path in which the sequence files are located. Allow for ~ expansion
        if seq_path.startswith('~'):
            self.seq_path = os.path.abspath(os.path.expanduser(os.path.join(seq_path)))
        else:
            self.seq_path = os.path.abspath(os.path.join(seq_path))
        self.debug = debug
        SetupLogging(self.debug)
        # Ensure that the path exists
        assert os.path.isdir(self.seq_path), 'Invalid path specified: {path}'.format(path=self.seq_path)
        logging.debug('Supplied sequence path: \n{path}'.format(path=self.seq_path))
        # Initialise class variables
        self.threads = threads
        self.report_path = os.path.join(self.seq_path, 'reports')
        if ref_path.startswith('~'):
            self.ref_path = os.path.abspath(os.path.expanduser(os.path.join(ref_path)))
        else:
            self.ref_path = os.path.abspath(os.path.join(ref_path))
        # Ensure that the path exists
        assert os.path.isdir(self.ref_path), 'Invalid path specified: {path}'.format(path=self.ref_path)
        logging.debug('Supplied reference path: \n{path}'.format(path=self.ref_path))
        # Determine if an additional volume
        if working_path:
            self.working_path = os.path.abspath(os.path.join(working_path))
        else:
            self.working_path = str()
        self.home = str(Path.home())
        self.dependency_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dependencies')
        self.fasta_path = os.path.join(self.seq_path, 'alignments')
        self.tree_path = os.path.join(self.seq_path, 'tree_files')
        self.summary_path = os.path.join(self.seq_path, 'summary_tables')
        self.logfile = os.path.join(self.seq_path, 'log')
        self.strain_name_dict = dict()
        self.strain_fastq_dict = dict()
        self.strain_consolidated_ref_dict = dict()
        self.strain_reference_abs_path_dict = dict()
        self.strain_reference_dep_path_dict = dict()
        self.strain_sorted_bam_dict = dict()
        self.reference_link_path_dict = dict()
        self.strain_vcf_dict = dict()
        self.strain_parsed_vcf_dict = dict()
        self.strain_best_ref_dict = dict()
        self.strain_best_ref_set_dict = dict()
        self.ref_snp_positions = dict()
        self.group_strain_snp_sequence = dict()
        self.species_group_best_ref = dict()
        self.group_fasta_dict = dict()
        self.strain_groups = dict()
        self.strain_species_dict = dict()
        self.species_group_order_dict = dict()
        self.species_group_annotated_snps_dict = dict()
        self.full_best_ref_gbk_dict = dict()
        self.species_group_num_snps = dict()
        self.species_group_sorted_snps = dict()


def get_version():
    try:
        version = 'COWSNPhR {version}'.format(version=pkg_resources.get_distribution('vsnpdev').version)
    except pkg_resources.DistributionNotFound:
        version = 'COWSNPhR (Unknown version)'
    return version


def main():
    # Parser for arguments
    parser = ArgumentParser(description='Finds SNPs between provided sequences and reference genome')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=get_version())
    parser.add_argument('-s', '--sequence_path',
                        required=True,
                        help='Path to folder containing sequencing reads')
    parser.add_argument('-r', '--reference_path',
                        required=True,
                        help='Provide the location of the folder containing the reference FASTA and GenBank files')
    parser.add_argument('-t', '--threads',
                        default=multiprocessing.cpu_count() - 1,
                        help='Number of threads. Default is the number of cores in the system - 1')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Enable debugging-level messages to be printed to the terminal')
    parser.add_argument('-w', '--working_path',
                        default=str(),
                        help='If you are running these analyses anywhere other than your $HOME directory, you will '
                             'need to provide the path to the drive e.g. /mnt/nas. This is necessary for the docker '
                             'calls to deepvariant. An additional volume will be mounted in the docker container: '
                             'e.g. -v /mnt/nas:/mnt/nas')
    args = parser.parse_args()
    cowsnphr = COWSNPhR(seq_path=args.sequence_path,
                        ref_path=args.reference_path,
                        threads=args.threads,
                        working_path=args.working_path,
                        debug=args.debug)
    cowsnphr.main()


if __name__ == '__main__':
    main()
