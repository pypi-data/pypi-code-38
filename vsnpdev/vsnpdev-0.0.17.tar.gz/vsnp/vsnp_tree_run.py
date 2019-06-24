#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import SetupLogging
from vsnp.install_dependencies import install_deps
from vsnp.vsnp_tree_methods import VSNPTreeMethods
from datetime import datetime
import logging
import os

__author__ = 'adamkoziol'


class VSNPTree(object):

    def main(self):
        """
        Run all the vSNP tree-specific methods
        """
        self.vcf_load()
        self.load_snp_sequence()
        self.phylogenetic_trees()
        self.annotate_snps()
        self.order_snps()
        self.create_report()

    def vcf_load(self):
        logging.info('Locating gVCF files')
        file_list = VSNPTreeMethods.file_list(file_path=self.file_path)
        logging.info('Extracting sequence names')
        self.strain_vcf_dict = VSNPTreeMethods.strain_list(vcf_files=file_list)
        logging.debug('gVCF files to be processed: \n{files}'.format(
            files='\n'.join(['{strain_name}: {gvcf_file}'.format(strain_name=sn, gvcf_file=gf)
                             for sn, gf in self.strain_vcf_dict.items()])))
        self.accession_species_dict = VSNPTreeMethods.parse_accession_species(ref_species_file=os.path.join(
            self.dependency_path, 'mash', 'species_accessions.csv'))
        logging.info('Parsing gVCF files')
        if self.variant_caller == 'deepvariant':
            self.strain_parsed_vcf_dict, self.strain_best_ref_dict, self.strain_best_ref_set_dict = \
                VSNPTreeMethods.load_gvcf(strain_vcf_dict=self.strain_vcf_dict,
                                          threads=self.threads,
                                          qual_cutoff=30)
        else:
            self.strain_parsed_vcf_dict, self.strain_best_ref_dict, self.strain_best_ref_set_dict = \
                VSNPTreeMethods.load_vcf(strain_vcf_dict=self.strain_vcf_dict)
        logging.debug('Parsed gVCF summaries:')
        if self.debug:
            pass_dict, insertion_dict, deletion_dict = \
                VSNPTreeMethods.summarise_gvcf_outputs(strain_parsed_vcf_dict=self.strain_parsed_vcf_dict)

            logging.debug('SNP bases: \n{results}'.format(
                results='\n'.join(['{strain_name}: {pass_filter}'.format(strain_name=sn, pass_filter=ps)
                                   for sn, ps in pass_dict.items()])))
            logging.debug('Inserted bases: \n{results}'.format(
                results='\n'.join(['{strain_name}: {insertion_calls}'.format(strain_name=sn, insertion_calls=ic)
                                   for sn, ic in insertion_dict.items()])))
            logging.debug('Deleted bases: \n{results}'.format(
                results='\n'.join(['{strain_name}: {deletion_calls}'.format(strain_name=sn, deletion_calls=dc)
                                   for sn, dc in deletion_dict.items()])))
        logging.debug('Extracted reference genomes: \n{results}'.format(
            results='\n'.join(['{strain_name}: {ref_set}'.format(strain_name=sn, ref_set=rs) for sn, rs in
                               self.strain_best_ref_set_dict.items()])))

    def load_snp_sequence(self):
        logging.info('Linking extracted reference genome to species code and reference FASTA file')
        self.strain_species_dict, strain_best_ref_fasta_dict = \
            VSNPTreeMethods.determine_ref_species(strain_best_ref_dict=self.strain_best_ref_dict,
                                                  accession_species_dict=self.accession_species_dict)
        logging.debug('Species codes: \n{results}'.format(
            results='\n'.join(['{strain_name}: {species_code}'.format(strain_name=sn, species_code=sc)
                               for sn, sc in self.strain_species_dict.items()])))
        logging.debug('Reference FASTA files \n{results}'.format(
            results='\n'.join(['{strain_name}: {ref_file}'.format(strain_name=sn, ref_file=rf)
                               for sn, rf in strain_best_ref_fasta_dict.items()])))
        self.reference_link_path_dict, reference_link_dict = \
            VSNPTreeMethods.reference_folder(strain_best_ref_fasta_dict=strain_best_ref_fasta_dict,
                                             dependency_path=self.dependency_path)
        self.strain_consolidated_ref_dict = \
            VSNPTreeMethods.consolidate_group_ref_genomes(reference_link_dict=reference_link_dict,
                                                          strain_best_ref_dict=self.strain_best_ref_dict)
        logging.info('Loading defining SNPs')
        defining_snp_dict = \
            VSNPTreeMethods.extract_defining_snps(reference_link_path_dict=self.reference_link_path_dict,
                                                  strain_species_dict=self.strain_species_dict,
                                                  dependency_path=self.dependency_path)
        logging.info('Loading SNP positions')
        consolidated_ref_snp_positions, strain_snp_positions, self.ref_snp_positions = \
            VSNPTreeMethods.load_gvcf_snp_positions(strain_parsed_vcf_dict=self.strain_parsed_vcf_dict,
                                                    strain_consolidated_ref_dict=self.strain_consolidated_ref_dict)
        logging.info('Determining to which groups strains are members using defining SNPs')
        self.strain_groups = VSNPTreeMethods.determine_groups(strain_snp_positions=strain_snp_positions,
                                                              defining_snp_dict=defining_snp_dict)
        logging.debug('Calculated group membership: \n{results}'.format(
            results='\n'.join(['{strain_name}: {group_list}'.format(strain_name=sn, group_list=gl)
                               for sn, gl in self.strain_groups.items()])))
        logging.info('Determining group-specific SNP positions')
        group_positions_set = \
            VSNPTreeMethods.determine_group_snp_positions(strain_snp_positions=strain_snp_positions,
                                                          strain_groups=self.strain_groups,
                                                          strain_species_dict=self.strain_species_dict)
        # Filter the positions if desired
        if self.filter_positions:
            group_positions_set = VSNPTreeMethods.filter_snps(group_positions_set)
        if self.debug:
            logging.debug('Number of SNPs per group:')
            for species_code, group_dict in group_positions_set.items():
                for group, ref_dict in group_dict.items():
                    for ref_chrom, pos_set in ref_dict.items():
                        print(species_code, group, ref_chrom, len(pos_set))
        logging.info('Loading group-specific SNP sequence')
        group_strain_snp_sequence, self.species_group_best_ref = \
            VSNPTreeMethods.load_snp_sequence(strain_parsed_vcf_dict=self.strain_parsed_vcf_dict,
                                              strain_consolidated_ref_dict=self.strain_consolidated_ref_dict,
                                              group_positions_set=group_positions_set,
                                              strain_groups=self.strain_groups,
                                              strain_species_dict=self.strain_species_dict,
                                              consolidated_ref_snp_positions=consolidated_ref_snp_positions)
        self.group_strain_snp_sequence, non_identical_group_positions = \
            VSNPTreeMethods.remove_identical_calls(group_strain_snp_sequence=group_strain_snp_sequence,
                                                   consolidated_ref_snp_positions=consolidated_ref_snp_positions)
        logging.info('Creating multi-FASTA files of group-specific core SNPs')
        group_folders, species_folders, self.group_fasta_dict = \
            VSNPTreeMethods.create_multifasta(group_strain_snp_sequence=self.group_strain_snp_sequence,
                                              group_positions_set=non_identical_group_positions,
                                              fasta_path=self.fasta_path)
        logging.debug('Multi-FASTA alignment files created:')
        if self.debug:
            for species_code, group_dict in self.group_fasta_dict.items():
                for group, fasta_file in group_dict.items():
                    print(species_code, group, fasta_file)

    def phylogenetic_trees(self):
        logging.info('Creating phylogenetic trees with RAxML')
        species_group_trees = VSNPTreeMethods.run_raxml(group_fasta_dict=self.group_fasta_dict,
                                                        strain_consolidated_ref_dict=self.strain_consolidated_ref_dict,
                                                        strain_groups=self.strain_groups,
                                                        threads=self.threads,
                                                        logfile=self.logfile)
        logging.debug('Tree files:')
        if self.debug:
            for species_code, group_dict in species_group_trees.items():
                for group, tree_file in group_dict.items():
                    print(species_code, group, tree_file['best_tree'])
        logging.info('Parsing strain order from phylogenetic trees')
        self.species_group_order_dict = VSNPTreeMethods.parse_tree_order(species_group_trees=species_group_trees)
        logging.debug('Strain order:')
        if self.debug:
            for species_code, group_dict in self.species_group_order_dict.items():
                for group, strain_order in group_dict.items():
                    print(species_code, group, strain_order)
        logging.info('Copying phylogenetic trees to {tree_path}'.format(tree_path=self.tree_path))
        VSNPTreeMethods.copy_trees(species_group_trees=species_group_trees,
                                   tree_path=self.tree_path)

    def annotate_snps(self):
        logging.info('Loading GenBank files for closest reference genomes')
        full_best_ref_gbk_dict = \
            VSNPTreeMethods.load_genbank_file(reference_link_path_dict=self.reference_link_path_dict,
                                              strain_best_ref_set_dict=self.strain_best_ref_set_dict,
                                              dependency_path=self.dependency_path)
        logging.info('Annotating SNPs')
        self.species_group_annotated_snps_dict = \
            VSNPTreeMethods.annotate_snps(group_strain_snp_sequence=self.group_strain_snp_sequence,
                                          full_best_ref_gbk_dict=full_best_ref_gbk_dict,
                                          strain_best_ref_set_dict=self.strain_best_ref_set_dict,
                                          ref_snp_positions=self.ref_snp_positions)

    def order_snps(self):
        logging.info('Counting prevalence of SNPs')
        species_group_snp_num_dict = \
            VSNPTreeMethods.determine_snp_number(group_strain_snp_sequence=self.group_strain_snp_sequence,
                                                 species_group_best_ref=self.species_group_best_ref)
        logging.info('Ranking SNPs based on prevalence')
        species_group_snp_rank, self.species_group_num_snps = \
            VSNPTreeMethods.rank_snps(species_group_snp_num_dict=species_group_snp_num_dict)
        logging.info('Sorting SNPs based on order of strains in phylogenetic trees')
        self.species_group_sorted_snps = \
            VSNPTreeMethods.sort_snps(species_group_order_dict=self.species_group_order_dict,
                                      species_group_snp_rank=species_group_snp_rank,
                                      species_group_best_ref=self.species_group_best_ref,
                                      group_strain_snp_sequence=self.group_strain_snp_sequence)

    def create_report(self):
        logging.info('Creating summary tables')
        VSNPTreeMethods.create_summary_table(species_group_sorted_snps=self.species_group_sorted_snps,
                                             species_group_order_dict=self.species_group_order_dict,
                                             species_group_best_ref=self.species_group_best_ref,
                                             group_strain_snp_sequence=self.group_strain_snp_sequence,
                                             species_group_annotated_snps_dict=self.species_group_annotated_snps_dict,
                                             species_group_num_snps=self.species_group_num_snps,
                                             summary_path=self.summary_path)

    def __init__(self, path, threads, debug, variant_caller, filter_positions):
        """
        :param path: type STR: Path of folder containing VCF files
        :param threads: type INT: Number of threads to use in the analyses
        :param debug: type BOOL: Boolean of whether debug level logs are printed to terminal
        :param filter_positions: type BOOL: Boolean of whether the calculated SNPs should be filtered with the
        Filtered_Regions.xlsx file
        """
        logging.info('vSNP phylogenetic tree creation module')
        SetupLogging(debug=debug)
        self.debug = debug
        # Determine the path in which the sequence files are located. Allow for ~ expansion
        if path.startswith('~'):
            self.file_path = os.path.abspath(os.path.expanduser(os.path.join(path)))
        else:
            self.file_path = os.path.abspath(os.path.join(path))
        # Ensure that the path exists
        assert os.path.isdir(self.file_path), 'Invalid path specified: {path}'.format(path=self.file_path)
        logging.debug('Supplied sequence path: \n{path}'.format(path=self.file_path))
        # Initialise class variables
        self.threads = threads
        self.report_path = os.path.join(self.file_path, 'reports')
        self.fasta_path = os.path.join(self.file_path, 'alignments')
        self.tree_path = os.path.join(self.file_path, 'tree_files')
        self.summary_path = os.path.join(self.file_path, 'summary_tables')
        # Extract the path of the folder containing this script
        self.script_path = os.path.abspath(os.path.dirname(__file__))
        # Use the script path to set the absolute path of the dependencies folder
        self.dependency_root = os.path.dirname(self.script_path)
        self.dependency_path = os.path.join(self.dependency_root, 'dependencies')
        # If the dependency folder is not present, download it
        if not os.path.isdir(self.dependency_path):
            install_deps(dependency_root=self.dependency_root)
        assert os.path.isdir(self.dependency_path), 'Something went wrong with the install. Cannot locate the ' \
                                                    'dependencies folder in: {sp}'.format(sp=self.script_path)
        self.variant_caller = variant_caller
        self.filter_positions = filter_positions
        self.logfile = os.path.join(self.file_path, 'log')
        self.start_time = datetime.now()
        # initialise variables
        self.strain_vcf_dict = dict()
        self.accession_species_dict = dict()
        self.strain_parsed_vcf_dict = dict()
        self.strain_best_ref_dict = dict()
        self.strain_best_ref_set_dict = dict()
        self.strain_species_dict = dict()
        self.reference_link_path_dict = dict()
        self.strain_consolidated_ref_dict = dict()
        self.ref_snp_positions = dict()
        self.strain_groups = dict()
        self.group_strain_snp_sequence = dict()
        self.species_group_best_ref = dict()
        self.group_fasta_dict = dict()
        self.species_group_order_dict = dict()
        self.species_group_annotated_snps_dict = dict()
        self.species_group_num_snps = dict()
        self.species_group_sorted_snps = dict()
