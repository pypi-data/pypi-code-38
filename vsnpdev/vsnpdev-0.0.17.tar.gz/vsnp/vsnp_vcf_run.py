#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import SetupLogging
from vsnp.install_dependencies import install_deps
from vsnp.vsnp_vcf_methods import VCFMethods
from datetime import datetime
from pathlib import Path
import subprocess
import logging
import os

__author__ = 'adamkoziol'


class VCF(object):
    def main(self):
        """
        Run all the VCF-specific methods
        """
        self.fastq_manipulation()
        self.best_reference_calculation()
        self.reference_mapping()
        self.stat_calculation()
        self.snp_calling()
        self.typing()
        self.report()

    def fastq_manipulation(self):
        """
        Determine the number of strains to process. Create strain-specific working directories with relative symlinks
        to FASTQ files
        """
        logging.info('Locating FASTQ files, creating strain-specific working directories and symlinks to files')
        fastq_files = VCFMethods.file_list(path=self.path)
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

    def best_reference_calculation(self):
        """
        Determine the best reference using MASH
        """
        logging.info('Running MASH analyses')
        fastq_sketch_dict = VCFMethods.call_mash_sketch(strain_fastq_dict=self.strain_fastq_dict,
                                                        strain_name_dict=self.strain_name_dict,
                                                        logfile=self.logfile)
        logging.debug(
            'Strain-specific MASH sketch files: \n{files}'.format(
                files='\n'.join(['{strain_name}: {sketch_file}'.format(strain_name=sn, sketch_file=sf)
                                 for sn, sf in fastq_sketch_dict.items()])))
        logging.info('Parsing MASH outputs to determine closest reference genomes')
        mash_dist_dict = VCFMethods.call_mash_dist(strain_fastq_dict=self.strain_fastq_dict,
                                                   strain_name_dict=self.strain_name_dict,
                                                   fastq_sketch_dict=fastq_sketch_dict,
                                                   ref_sketch_file=os.path.join(
                                                       self.dependency_path, 'mash', 'vsnp_reference.msh'),
                                                   logfile=self.logfile)
        logging.debug(
            'Strain-specific MASH output tables: \n{files}'.format(
                files='\n'.join(['{strain_name}: {table}'.format(strain_name=sn, table=tf)
                                 for sn, tf in mash_dist_dict.items()])))
        logging.info('Loading reference genome: species dictionary')
        accession_species_dict = VCFMethods.parse_mash_accession_species(mash_species_file=os.path.join(
            self.dependency_path, 'mash', 'species_accessions.csv'))
        logging.info('Determining closest reference genome and extracting corresponding species from MASH outputs')
        self.strain_best_ref_dict, self.strain_ref_matches_dict, self.strain_species_dict = \
            VCFMethods.mash_best_ref(mash_dist_dict=mash_dist_dict,
                                     accession_species_dict=accession_species_dict,
                                     min_matches=self.matching_hashes)
        logging.debug(
            'Strain-specific MASH-calculated best reference file: \n{files}'.format(
                files='\n'.join(['{strain_name}: {best_ref}'.format(strain_name=sn, best_ref=br)
                                 for sn, br in self.strain_best_ref_dict.items()])))
        logging.debug(
            'Number of matches to strain-specific MASH-calculated best reference file: \n{files}'.format(
                files='\n'.join(['{strain_name}: {num_matches}'.format(strain_name=sn, num_matches=nm)
                                 for sn, nm in self.strain_ref_matches_dict.items()])))
        logging.debug(
            'Species code for best reference file: \n{files}'.format(
                files='\n'.join(['{strain_name}: {species_code}'.format(strain_name=sn, species_code=sc)
                                 for sn, sc in self.strain_species_dict.items()])))

    def reference_mapping(self):
        """
        Perform reference mapping with bowtie2, and attempt to assemble any unmapped reads into contigs with SKESA
        """
        logging.info('Extracting paths to reference genomes')
        reference_link_path_dict, reference_link_dict \
            = VCFMethods.reference_folder(strain_best_ref_dict=self.strain_best_ref_dict,
                                          dependency_path=self.dependency_path)
        logging.info('Indexing reference file for {rm} analyses'.format(rm=self.reference_mapper))
        strain_mapper_index_dict, self.strain_reference_abs_path_dict, self.strain_reference_dep_path_dict = \
            VCFMethods.index_ref_genome(reference_link_path_dict=reference_link_path_dict,
                                        dependency_path=self.dependency_path,
                                        logfile=self.logfile,
                                        reference_mapper=self.reference_mapper)
        logging.info('Performing reference mapping using {rm}'.format(rm=self.reference_mapper))
        self.strain_sorted_bam_dict = VCFMethods.map_ref_genome(
            strain_fastq_dict=self.strain_fastq_dict,
            strain_name_dict=self.strain_name_dict,
            strain_mapper_index_dict=strain_mapper_index_dict,
            reference_mapper=self.reference_mapper,
            threads=self.threads,
            logfile=self.logfile)
        logging.debug('Sorted BAM files: \n{files}'.format(
                files='\n'.join(['{strain_name}: {bam_file}'.format(strain_name=sn, bam_file=bf)
                                 for sn, bf in self.strain_sorted_bam_dict.items()])))
        logging.info('Extracting unmapped reads')
        strain_unmapped_reads_dict = VCFMethods.extract_unmapped_reads(
            strain_sorted_bam_dict=self.strain_sorted_bam_dict,
            strain_name_dict=self.strain_name_dict,
            threads=self.threads,
            logfile=self.logfile)
        logging.info('Attempting to assemble unmapped reads with SKESA')
        self.strain_skesa_output_fasta_dict = VCFMethods.assemble_unmapped_reads(
            strain_unmapped_reads_dict=strain_unmapped_reads_dict,
            strain_name_dict=self.strain_name_dict,
            threads=self.threads,
            logfile=self.logfile)
        logging.debug('SKESA assemblies: \n{files}'.format(
            files='\n'.join(['{strain_name}: {assembly}'.format(strain_name=sn, assembly=af)
                             for sn, af in self.strain_skesa_output_fasta_dict.items()])))

    def stat_calculation(self):
        """
        Calculate raw stats on FASTQ file size, quality and length distributions of FASTQ reads, and qualimap-generated
        statistics on reference mapping
        """
        logging.info('Calculating quality and length distributions of FASTQ reads')
        self.strain_qhist_dict, \
            self.strain_lhist_dict = VCFMethods.run_reformat_reads(strain_fastq_dict=self.strain_fastq_dict,
                                                                   strain_name_dict=self.strain_name_dict,
                                                                   logfile=self.logfile)
        self.strain_average_quality_dict, self.strain_qual_over_thirty_dict = \
            VCFMethods.parse_quality_histogram(strain_qhist_dict=self.strain_qhist_dict)
        logging.debug('Average strain quality score: \n{files}'.format(
            files='\n'.join(['{strain_name}: {quality}'.format(strain_name=sn, quality=qs)
                             for sn, qs in self.strain_average_quality_dict.items()])))
        self.strain_avg_read_lengths = VCFMethods.parse_length_histograms(strain_lhist_dict=self.strain_lhist_dict)
        logging.debug('Average strain read lengths: \n{files}'.format(
            files='\n'.join(['{strain_name}: {read_lengths}'.format(strain_name=sn, read_lengths=rl)
                             for sn, rl in self.strain_avg_read_lengths.items()])))
        logging.info('Calculating size of FASTQ files')
        self.strain_fastq_size_dict = VCFMethods.find_fastq_size(self.strain_fastq_dict)
        logging.debug('FASTQ file size: \n{files}'.format(
            files='\n'.join(['{strain_name}: {file_size}'.format(strain_name=sn, file_size=fs)
                             for sn, fs in self.strain_fastq_size_dict.items()])))
        logging.info('Counting of contigs in assemblies of unmapped reads')
        self.strain_unmapped_contigs_dict = VCFMethods.assembly_stats(
            strain_skesa_output_fasta_dict=self.strain_skesa_output_fasta_dict)
        VCFMethods.samtools_index(strain_sorted_bam_dict=self.strain_sorted_bam_dict,
                                  strain_name_dict=self.strain_name_dict,
                                  threads=self.threads,
                                  logfile=self.logfile)
        logging.debug('Number of contigs in SKESA assemblies: \n{files}'.format(
            files='\n'.join(['{strain_name}: {num_contigs}'.format(strain_name=sn, num_contigs=nc)
                             for sn, nc in self.strain_unmapped_contigs_dict.items()])))
        logging.info('Running qualimap analyses on sorted BAM files')
        strain_qualimap_report_dict = VCFMethods.run_qualimap(strain_sorted_bam_dict=self.strain_sorted_bam_dict,
                                                              strain_name_dict=self.strain_name_dict,
                                                              logfile=self.logfile)
        self.strain_qualimap_outputs_dict = VCFMethods.parse_qualimap(
            strain_qualimap_report_dict=strain_qualimap_report_dict)

    def snp_calling(self):
        """
        Prep files for SNP calling. Use deepvariant to call SNPs. Parse the outputs from deepvariant
        """
        if 'deepvariant' in self.variant_caller:
            logging.info('Preparing files for SNP calling with deepvariant make_examples')
            strain_examples_dict, strain_variant_path_dict, strain_gvcf_tfrecords_dict = \
                VCFMethods.deepvariant_make_examples(strain_sorted_bam_dict=self.strain_sorted_bam_dict,
                                                     strain_name_dict=self.strain_name_dict,
                                                     strain_reference_abs_path_dict=self.strain_reference_abs_path_dict,
                                                     vcf_path=os.path.join(self.path, 'vcf_files'),
                                                     home=self.home,
                                                     threads=self.threads,
                                                     logfile=self.logfile,
                                                     deepvariant_version=self.deepvariant_version)
            logging.info('Calling variants with deepvariant call_variants')
            strain_call_variants_dict = \
                VCFMethods.deepvariant_call_variants(strain_variant_path_dict=strain_variant_path_dict,
                                                     strain_name_dict=self.strain_name_dict,
                                                     dependency_path=self.dependency_path,
                                                     vcf_path=os.path.join(self.path, 'vcf_files'),
                                                     home=self.home,
                                                     threads=self.threads,
                                                     logfile=self.logfile,
                                                     variant_caller=self.variant_caller,
                                                     deepvariant_version=self.deepvariant_version)
            logging.info('Creating VCF files with deepvariant postprocess_variants')
            strain_vcf_dict = \
                VCFMethods.deepvariant_postprocess_variants_multiprocessing(
                    strain_call_variants_dict=strain_call_variants_dict,
                    strain_variant_path_dict=strain_variant_path_dict,
                    strain_name_dict=self.strain_name_dict,
                    strain_reference_abs_path_dict=self.strain_reference_abs_path_dict,
                    strain_gvcf_tfrecords_dict=strain_gvcf_tfrecords_dict,
                    vcf_path=os.path.join(self.path, 'vcf_files'),
                    home=self.home,
                    logfile=self.logfile,
                    deepvariant_version=self.deepvariant_version,
                    threads=self.threads)
            logging.info('Parsing gVCF files to find high quality SNPs')
            self.strain_num_high_quality_snps_dict = VCFMethods.parse_gvcf(strain_vcf_dict=strain_vcf_dict)
        else:
            logging.info('Creating regions file for freebayes-parallel')
            strain_ref_regions_dict = \
                VCFMethods.reference_regions(strain_reference_abs_path_dict=self.strain_reference_abs_path_dict,
                                             logfile=self.logfile)
            logging.info('Creating gVCF files with freebayes-parallel')
            strain_vcf_dict = VCFMethods.freebayes(strain_sorted_bam_dict=self.strain_sorted_bam_dict,
                                                   strain_name_dict=self.strain_name_dict,
                                                   strain_reference_abs_path_dict=self.strain_reference_abs_path_dict,
                                                   strain_ref_regions_dict=strain_ref_regions_dict,
                                                   threads=self.threads,
                                                   logfile=self.logfile)
            logging.info('Parsing gVCF files to find high quality SNPs')
            self.strain_num_high_quality_snps_dict = VCFMethods.parse_vcf(strain_vcf_dict=strain_vcf_dict)
        VCFMethods.copy_vcf_files(strain_vcf_dict=strain_vcf_dict,
                                  vcf_path=os.path.join(self.path, 'vcf_files'))
        logging.debug('Number high quality SNPs: \n{files}'.format(
            files='\n'.join(['{strain_name}: {num_snps}'.format(strain_name=sn, num_snps=ns)
                             for sn, ns in self.strain_num_high_quality_snps_dict.items()])))

    def typing(self):
        """
        Perform typing analyses including spoligotyping, and the subsequence extraction of binary, octal, hexadecimal,
        and sb codes. Also determine MLST profiles of samples
        """
        logging.info('Searching for matches to spoligo sequences')
        strain_spoligo_stats_dict = VCFMethods.bait_spoligo(strain_fastq_dict=self.strain_fastq_dict,
                                                            strain_name_dict=self.strain_name_dict,
                                                            spoligo_file=os.path.join(self.dependency_path,
                                                                                      'mycobacterium',
                                                                                      'spacers.fasta'),
                                                            threads=self.threads,
                                                            logfile=self.logfile,
                                                            kmer=25)
        logging.info('Calculating binary, octal, and hexadecimal codes')
        self.strain_binary_code_dict, \
            self.strain_octal_code_dict, \
            self.strain_hexadecimal_code_dict = \
            VCFMethods.parse_spoligo(strain_spoligo_stats_dict=strain_spoligo_stats_dict)
        logging.debug('Strain binary codes: \n{files}'.format(
            files='\n'.join(['{strain_name}: {binary_code}'.format(strain_name=sn, binary_code=bc)
                             for sn, bc in self.strain_binary_code_dict.items()])))
        logging.debug('Strain octal codes: \n{files}'.format(
            files='\n'.join(['{strain_name}: {octal_code}'.format(strain_name=sn, octal_code=oc)
                             for sn, oc in self.strain_octal_code_dict.items()])))
        logging.debug('Strain hexadecimal codes: \n{files}'.format(
            files='\n'.join(['{strain_name}: {hex_code}'.format(strain_name=sn, hex_code=hc)
                             for sn, hc in self.strain_hexadecimal_code_dict.items()])))
        logging.info('Extracting sb codes')
        self.strain_sbcode_dict = VCFMethods.extract_sbcode(
            strain_reference_dep_path_dict=self.strain_reference_dep_path_dict,
            strain_octal_code_dict=self.strain_octal_code_dict)
        logging.debug('Strain sb codes: \n{files}'.format(
            files='\n'.join(['{strain_name}: {sb_code}'.format(strain_name=sn, sb_code=sc)
                             for sn, sc in self.strain_sbcode_dict.items()])))
        logging.info('Performing MLST analyses')
        VCFMethods.brucella_mlst(seqpath=self.path,
                                 mlst_db_path=os.path.join(self.dependency_path, 'brucella', 'MLST'),
                                 logfile=self.logfile)
        logging.info('Parsing MLST outputs')
        self.strain_mlst_dict = VCFMethods.parse_mlst_report(strain_name_dict=self.strain_name_dict,
                                                             mlst_report=os.path.join(self.path, 'reports', 'mlst.csv'))
        logging.debug('MLST results: \n{files}'.format(
            files='\n'.join(['{strain_name}: {mlst_result}'.format(strain_name=sn, mlst_result=mr)
                             for sn, mr in self.strain_mlst_dict.items()])))

    def report(self):
        """
        Create the .xlsx report consistent with the legacy vSNP format
        """
        logging.info('Creating report')
        VCFMethods.create_vcf_report(
            start_time=self.start_time,
            strain_species_dict=self.strain_species_dict,
            strain_best_ref_dict=self.strain_best_ref_dict,
            strain_fastq_size_dict=self.strain_fastq_size_dict,
            strain_average_quality_dict=self.strain_average_quality_dict,
            strain_qual_over_thirty_dict=self.strain_qual_over_thirty_dict,
            strain_qualimap_outputs_dict=self.strain_qualimap_outputs_dict,
            strain_avg_read_lengths=self.strain_avg_read_lengths,
            strain_unmapped_contigs_dict=self.strain_unmapped_contigs_dict,
            strain_num_high_quality_snps_dict=self.strain_num_high_quality_snps_dict,
            strain_mlst_dict=self.strain_mlst_dict,
            strain_octal_code_dict=self.strain_octal_code_dict,
            strain_sbcode_dict=self.strain_sbcode_dict,
            strain_hexadecimal_code_dict=self.strain_hexadecimal_code_dict,
            strain_binary_code_dict=self.strain_binary_code_dict,
            report_path=self.report_path)

    def __init__(self, path, threads, debug, reference_mapper, variant_caller, matching_hashes):
        """
        :param path: type STR: Path of folder containing FASTQ files
        :param threads: type INT: Number of threads to use in the analyses
        :param debug: type BOOL: Boolean of whether debug level logs are printed to terminal
        :param reference_mapper: type STR: Name of the reference mapping software to use (choices are bwa and bowtie2)
        :param variant_caller: type STR: Name of the variant calling software to use (choices are deep variant and
        freebayes)
        :param matching_hashes: type INT: Minimum number of matching hashes in MASH analyses in order for a match
        to be declared successful
        """
        SetupLogging(debug=debug)
        # Determine the path in which the sequence files are located. Allow for ~ expansion
        if path.startswith('~'):
            self.path = os.path.abspath(os.path.expanduser(os.path.join(path)))
        else:
            self.path = os.path.abspath(os.path.join(path))
        # Ensure that the path exists
        assert os.path.isdir(self.path), 'Invalid path specified: {path}'.format(path=self.path)
        logging.debug('Supplied sequence path: \n{path}'.format(path=self.path))
        # Initialise class variables
        self.threads = threads
        self.report_path = os.path.join(self.path, 'reports')
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
        self.reference_mapper = reference_mapper
        self.variant_caller = variant_caller
        # Ensure that if deepvariant or deepvariant-gpu is requested, the image has been installed, and the system
        # is able to run it properly
        self.deepvariant_version = '0.8.0'
        if self.variant_caller == 'deepvariant':
            cmd = 'docker run --rm gcr.io/deepvariant-docker/deepvariant:{dvv} ' \
                  '/opt/deepvariant/bin/call_variants -h'.format(dvv=self.deepvariant_version)
            cmd_sts, return_code = run_cmd(cmd)
            if not cmd_sts:
                self.deepvariant_version = '0.7.2'
                cmd = 'docker run --rm gcr.io/deepvariant-docker/deepvariant:{dvv} ' \
                      '/opt/deepvariant/bin/call_variants -h'.format(dvv=self.deepvariant_version)
                cmd_sts, return_code = run_cmd(cmd=cmd)
                if not cmd_sts:
                    raise subprocess.CalledProcessError(return_code, cmd=cmd)
        elif self.variant_caller == 'deepvariant-gpu':
            cmd = 'nvida-docker run --rm gcr.io/deepvariant-docker/deepvariant:{dvv} ' \
                  '/opt/deepvariant/bin/call_variants -h'.format(dvv=self.deepvariant_version)
            cmd_sts, return_code = run_cmd(cmd)
            if not cmd_sts:
                raise subprocess.CalledProcessError(return_code, cmd=cmd)
        self.matching_hashes = matching_hashes
        self.logfile = os.path.join(self.path, 'log')
        self.start_time = datetime.now()
        self.home = str(Path.home())
        self.strain_name_dict = dict()
        self.strain_fastq_dict = dict()
        self.strain_best_ref_dict = dict()
        self.strain_ref_matches_dict = dict()
        self.strain_species_dict = dict()
        self.strain_sorted_bam_dict = dict()
        self.strain_reference_abs_path_dict = dict()
        self.strain_reference_dep_path_dict = dict()
        self.strain_skesa_output_fasta_dict = dict()
        self.strain_qhist_dict = dict()
        self.strain_lhist_dict = dict()
        self.strain_average_quality_dict = dict()
        self.strain_qual_over_thirty_dict = dict()
        self.strain_avg_read_lengths = dict()
        self.strain_fastq_size_dict = dict()
        self.strain_unmapped_contigs_dict = dict()
        self.strain_qualimap_outputs_dict = dict()
        self.strain_num_high_quality_snps_dict = dict()
        self.strain_binary_code_dict = dict()
        self.strain_octal_code_dict = dict()
        self.strain_hexadecimal_code_dict = dict()
        self.strain_sbcode_dict = dict()
        self.strain_mlst_dict = dict()


def run_cmd(cmd):
    """
    Runs a command using subprocess, and returns both the stdout and stderr from that command
    If exit code from command is non-zero, raises subprocess.CalledProcessError
    :param cmd: command to run as a string, as it would be called on the command line
    :return: out, err: Strings that are the stdout and stderr from the command called.
    """
    command_status = True
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    if p.returncode not in [0, 1]:
        command_status = False
    return command_status, p.returncode
