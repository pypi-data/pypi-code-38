#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import filer, make_path, relative_symlink, run_subprocess, \
    write_to_logfile
from Bio import SeqIO
import multiprocessing
from glob import glob
import xlsxwriter
import shutil
import gzip
import os
import re

__author__ = 'adamkoziol'


class VCFMethods(object):
    @staticmethod
    def file_list(path):
        """
        Create a list of all FASTQ files present in the supplied path. Accepts .fastq.gz, .fastq, .fq, and .fq.gz
        extensions only
        :param path: type STR: absolute path of folder containing FASTQ files
        :return fastq_files: sorted list of all FASTQ files present in the supplied path
        """
        # Use glob to find the acceptable extensions of FASTQ files in the supplied path
        fastq_files = glob(os.path.join(path, '*.fastq'))
        fastq_files = fastq_files + glob(os.path.join(path, '*.fastq.gz'))
        fastq_files = fastq_files + glob(os.path.join(path, '*.fq'))
        fastq_files = fastq_files + glob(os.path.join(path, '*.fq.gz'))
        # Sort the list of fastq files
        fastq_files = sorted(fastq_files)
        # Ensure that there are actually files present in the path
        assert fastq_files, 'Cannot find FASTQ files in the supplied path: {path}'.format(path=path)
        return fastq_files

    @staticmethod
    def strain_list(fastq_files):
        """
        Use the filer method to parse a list of absolute paths of FASTQ files to yield the name of the strain.
        e.g. /path/to/03-1057_S10_L001_R1_001.fastq.gz will return /path/to/03-1057:
        /path/to/03-1057_S10_L001_R1_001.fastq.gz
        :param fastq_files: type LIST: List of absolute of paired and/or unpaired FASTQ files
        :return strain_dict: dictionary of the absolute paths to the base strain name: FASTQ files
        """
        # As filer returns a set of the names, transform this set into a sorted list
        strain_dict = filer(filelist=fastq_files,
                            returndict=True)
        return strain_dict

    @staticmethod
    def strain_namer(strain_folders):
        """
        Extract the base strain name from a list of absolute paths with the strain name (this list is usually created
        using the strain_list method above
        e.g. /path/to/03-1057 will yield 03-1057
        :param strain_folders: type iterable: List or dictionary of absolute paths and base strain names
        :return: strain_names: list of strain base names
        """
        # Initialise a dictionary to store the strain names
        strain_name_dict = dict()
        for strain_folder in strain_folders:
            # Extract the base name from the absolute path plus base name
            strain_name = os.path.basename(strain_folder)
            strain_name_dict[strain_name] = strain_folder
        return strain_name_dict

    @staticmethod
    def file_link(strain_folder_dict, strain_name_dict):
        """
        Create folders for each strain. Create relative symlinks to the original FASTQ files from within the folder
        :param strain_folder_dict: type DICT: Dictionary of strain folder path: FASTQ files
        :param strain_name_dict: type DICT: Dictionary of base strain name: strain folder path
        :return: strain_fastq_dict: Dictionary of strain name: list of absolute path(s) of FASTQ file(s)
        """
        #
        strain_fastq_dict = dict()
        for strain_name, strain_folder in strain_name_dict.items():
            # Create the strain folder path if required
            make_path(strain_folder)
            # Use the strain_folder value from the strain_name_dict as the key to extract the list of FASTQ files
            # associated with each strain
            for fastq_file in strain_folder_dict[strain_folder]:
                # Create relative symlinks between the original FASTQ files and the strain folder
                symlink_path = relative_symlink(src_file=fastq_file,
                                                output_dir=strain_folder,
                                                export_output=True)
                # Add the absolute path of the symlink to the dictionary
                try:
                    strain_fastq_dict[strain_name].append(symlink_path)
                except KeyError:
                    strain_fastq_dict[strain_name] = [symlink_path]
        return strain_fastq_dict

    @staticmethod
    def run_reformat_reads(strain_fastq_dict, strain_name_dict, logfile):
        """
        Run reformat.sh from the BBMAP suite of tools. This will create histograms of the number of reads with a
        specific phred quality score, as well the number of reads of a specific length
        :param strain_fastq_dict: type DICT: Dictionary of strain name: list of absolute path(s) of FASTQ file(s)
        :param strain_name_dict: type DICT: Dictionary of base strain name: strain folder path
        :param logfile: type STR: Absolute path to logfile basename
        :return: strain_qhist_dict: Dictionary of strain name: list of absolute paths to read set-specific
        quality histograms
        :return: strain_lhist_dict: Dictionary of strain name: list of absolute path to read set-specific
        length histograms
        """
        # Initialise dictionaries to store the absolute paths of the quality count, and the length distribution
        # histograms for each set of reads
        strain_qhist_dict = dict()
        strain_lhist_dict = dict()
        for strain_name, fastq_files in strain_fastq_dict.items():
            # Initialise the strain-specific lists in the dictionaries
            strain_qhist_dict[strain_name] = list()
            strain_lhist_dict[strain_name] = list()
            # Extract the absolute path of the strain-specific working directory
            strain_folder = strain_name_dict[strain_name]
            # Initialise a counter to properly name the histogram files
            count = 1
            for fastq_file in fastq_files:
                # Set the absolute path of the quality and length histogram output file. Include the
                # strain name, as well as the file number count
                qual_histo = os.path.join(strain_folder, '{sn}_R{count}_qchist.csv'.format(sn=strain_name,
                                                                                           count=count))
                length_histo = os.path.join(strain_folder, '{sn}_R{count}_lhist.csv'.format(sn=strain_name,
                                                                                            count=count))
                # Create the system call to reformat.sh. qchist: count of bases with each quality value, lhist:
                # read length histogram
                reformat_cmd = 'reformat.sh in={fastq} qchist={qchist} lhist={lhist}' \
                    .format(fastq=fastq_file,
                            qchist=qual_histo,
                            lhist=length_histo)
                # Only run the analyses if the output file doesn't already exist
                if not os.path.isfile(length_histo):
                    out, err = run_subprocess(command=reformat_cmd)
                    # Write the stdout, and stderr to the main logfile, as well as to the strain-specific logs
                    write_to_logfile(out=out,
                                     err=err,
                                     logfile=logfile,
                                     samplelog=os.path.join(strain_folder, 'log.out'),
                                     sampleerr=os.path.join(strain_folder, 'log.err'))
                # Increase the file numbering count
                count += 1
                # Append the absolute path to the list of paths
                strain_qhist_dict[strain_name].append(qual_histo)
                strain_lhist_dict[strain_name].append(length_histo)
        return strain_qhist_dict, strain_lhist_dict

    @staticmethod
    def parse_quality_histogram(strain_qhist_dict):
        """
        Parse the quality histograms created by reformat.sh to calculate the average read quality as well as the
        percentage of reads with a Q-score greater than 30
        :param strain_qhist_dict: type: DICT: Dictionary of strain name: list of absolute paths to read set-specific
        quality histograms
        :return: strain_average_quality_dict: Dictionary of strain name: list of read set-specific average quality
        scores
        :return: strain_qual_over_thirty_dict: Dictionary of strain name: list of read set-specific percentage of
        reads with a Phred quality-score greater or equal to 30
        """
        # Initialise dictionaries to store the average read quality, and the percentage of reads with q-scores greater
        # than 30
        strain_average_quality_dict = dict()
        strain_qual_over_thirty_dict = dict()
        for strain_name, qual_histos in strain_qhist_dict.items():
            # Initialise the strain-specific list of outputs
            strain_average_quality_dict[strain_name] = list()
            strain_qual_over_thirty_dict[strain_name] = list()
            for qual_histo in sorted(qual_histos):
                # Read in the quality histogram
                with open(qual_histo, 'r') as histo:
                    # Skip the header line
                    next(histo)
                    # Initialise counts to store necessary integers
                    total_count = 0
                    total_read_quality = 0
                    qual_over_thirty_count = 0
                    for line in histo:
                        # Split each line on tabs into the quality score, the number of reads with that particular
                        # quality score, and the fraction of the total number reads these reads represent
                        quality, count, fraction = line.rstrip().split('\t')
                        # Manipulate the variables to integers
                        quality = int(quality)
                        count = int(count)
                        # Add read count * quality score to the cumulative read * quality score
                        total_read_quality += count * quality
                        # Add the current count to the total read count
                        total_count += count
                        # Determine if the read quality is >= 30. Add only those reads to the cumulative count
                        if quality >= 30:
                            qual_over_thirty_count += count
                    # Calculate the average quality: total quality count / total number of reads
                    average_qual = total_read_quality / total_count
                    # Calculate the % of reads with Q >= 30: number of reads with Q >= 30 / total number of reads
                    perc_reads_over_thirty = qual_over_thirty_count / total_count * 100
                    # Add the calculated values to the appropriate dictionaries
                    strain_average_quality_dict[strain_name].append(average_qual)
                    strain_qual_over_thirty_dict[strain_name].append(perc_reads_over_thirty)
        return strain_average_quality_dict, strain_qual_over_thirty_dict

    @staticmethod
    def parse_length_histograms(strain_lhist_dict):
        """
        Parse the length histogram created by reformat.sh to calculate the strain-specific average read length
        :param strain_lhist_dict: type DICT: Dictionary of strain name: list of absolute path to read set-specific
        length histograms
        :return: strain_avg_read_lengths: Dictionary of strain name: float of calculated strain-specific average
        read length
        """
        # Initialise a dictionary to store the strain-specific average read length
        strain_avg_read_lengths = dict()
        for strain_name, length_histos in strain_lhist_dict.items():
            # Initialise integers to store the total number of reads, as well as the total read count * length int
            total_count = 0
            total_count_length = 0
            # The average read quality is calculated on a per-sample, rather than a per-read set basis. So, the
            # variables are initialised outside of the histo loop
            for length_histo in length_histos:
                with open(length_histo, 'r') as histo:
                    # Skip the header
                    next(histo)
                    for line in histo:
                        # Extract the read length and the number of reads of that length from the current line
                        length, count = line.rstrip().split('\t')
                        # Set the length and count to be integers
                        length = int(length)
                        count = int(count)
                        # Increment the total count by the current count
                        total_count += count
                        # Increment the total length * count variable by the current length * count
                        total_count_length += length * count
            # The average read length is calculated by dividing the total number of bases (length * count) by the
            # total number of reads
            avg_read_length = total_count_length / total_count
            # Populate the dictionary with the calculate average read length
            strain_avg_read_lengths[strain_name] = avg_read_length
        return strain_avg_read_lengths

    @staticmethod
    def find_fastq_size(strain_fastq_dict):
        """
        Use os.path.getsize to extract the size of the FASTQ files. Convert the value in bytes to megabytes
        :param strain_fastq_dict: type DICT: Dictionary of strain name: strain-specific FASTQ files
        :return: strain_fastq_size_dict: Dictionary of strain name: list of sizes of FASTQ files in megabytes
        """
        # Initialise a dictionary to store the strain-specific FASTQ file sizes
        strain_fastq_size_dict = dict()
        for strain_name, fastq_files in strain_fastq_dict.items():
            # Get the strain-specific list ready to be populated
            strain_fastq_size_dict[strain_name] = list()
            for fastq_file in fastq_files:
                # Use os.path.getsize to get the filesize in bytes. Convert this to megabytes by dividing this number
                # 1024*1024.0 (.0 is included, so that the divisor will be a float)
                file_size = os.path.getsize(fastq_file) / (1024 * 1024.0)
                strain_fastq_size_dict[strain_name].append(file_size)
        return strain_fastq_size_dict

    @staticmethod
    def call_mash_sketch(strain_fastq_dict, strain_name_dict, logfile):
        """
        Run MASH sketch on the provided FASTQ files
        :param strain_fastq_dict: type DICT: Dictionary of strain name: list of absolute path(s) of FASTQ file(s)
        :param strain_name_dict: type DICT: Dictionary of base strain name: strain folder path
        :param logfile: type STR: Absolute path to logfile basename
        :return: fastq_sketch_dict: Dictionary of strain name: absolute path to MASH sketch file
        """
        # Initialise a dictionary to store the absolute path of the sketch file
        fastq_sketch_dict = dict()
        for strain_name, fastq_files in strain_fastq_dict.items():
            # Extract the strain-specific working directory
            strain_folder = strain_name_dict[strain_name]
            # Set the absolute paths of the sketch file with and without the .msh extension (used for calling MASH)
            fastq_sketch_no_ext = os.path.join(strain_folder, '{sn}_sketch'.format(sn=strain_name))
            fastq_sketch = fastq_sketch_no_ext + '.msh'
            # Create the system call - cat together the FASTQ files, and pipe them into MASH
            # -p requests the number of desired threads, -m sets the minimum copies of each k-mer required to pass
            # noise filter for reads to 2 (ignores single copy kmers), - indicates that MASH should use stdin
            # -o is the absolute path to the sketch output file
            mash_sketch_command = 'cat {fastq} | mash sketch -m 2 - -o {output_file}' \
                .format(fastq=' '.join(fastq_files),
                        output_file=fastq_sketch_no_ext)
            # Only make the system call if the output sketch file doesn't already exist
            if not os.path.isfile(fastq_sketch):
                out, err = run_subprocess(command=mash_sketch_command)
                # Write the stdout, and stderr to the main logfile, as well as to the strain-specific logs
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile,
                                 samplelog=os.path.join(strain_folder, 'log.out'),
                                 sampleerr=os.path.join(strain_folder, 'log.err'))
            # Populate the dictionary with the absolute path of the sketch file
            fastq_sketch_dict[strain_name] = fastq_sketch
        return fastq_sketch_dict

    @staticmethod
    def call_mash_dist(strain_fastq_dict, strain_name_dict, fastq_sketch_dict, ref_sketch_file, logfile):
        """
        Run a MASH dist of a pre-sketched set of FASTQ reads against the custom MASH sketch file of the reference
        genomes supported by vSNP
        :param strain_fastq_dict: type DICT: Dictionary of strain name: list of absolute path(s) of FASTQ file(s)
        :param strain_name_dict: type DICT: Dictionary of base strain name: strain folder path
        :param fastq_sketch_dict: type DICT: Dictionary of strain name: absolute path to MASH sketch file
        :param ref_sketch_file: type STR: Absolute path to the custom sketch file of reference sequences
        :param logfile: type STR: Absolute path to logfile basename
        :return: strain_mash_outputs: Dictionary of strain name: absolute path of MASH dist output table
        """
        # Initialise the dictionary to store the absolute path of the MASH dist output file
        strain_mash_outputs = dict()
        for strain_name in strain_fastq_dict:
            # Extract the absolute path of the strain-specific working directory
            strain_folder = strain_name_dict[strain_name]
            # Extract the absolute path of the strain-specific sketch file
            fastq_sketch_file = fastq_sketch_dict[strain_name]
            # Set the absolute path of the MASH dist output table
            out_tab = os.path.join(strain_folder, '{sn}_mash.tab'.format(sn=strain_name))
            # Create the system call: -p is the number of threads requested, -m sets the minimum copies of each k-mer
            # required to pass noise filter for reads to 2 (ignores single copy kmers). MASH outputs are piped to
            # the sort function, which sorts the data as follows: g: general numeric sort, K: keydef
            mash_dist_command = 'mash dist -m 2 {ref_sketch_file} {fastq_sketch} | sort -gk3 > {out}' \
                .format(ref_sketch_file=ref_sketch_file,
                        fastq_sketch=fastq_sketch_file,
                        out=out_tab)
            if not os.path.isfile(out_tab):
                out, err = run_subprocess(command=mash_dist_command)
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile,
                                 samplelog=os.path.join(strain_folder, 'log.out'),
                                 sampleerr=os.path.join(strain_folder, 'log.err'))
            strain_mash_outputs[strain_name] = out_tab
        return strain_mash_outputs

    @staticmethod
    def parse_mash_accession_species(mash_species_file):
        """
        Parse the reference genus accession: species code .csv file included in the mash dependencies path
        :param mash_species_file: type STR: Absolute path to file containing reference file name: species code
        :return: accession_species_dict: Dictionary of reference accession: species code
        """
        # Initialise a dictionary to store the species code
        accession_species_dict = dict()
        with open(mash_species_file, 'r') as species_file:
            for line in species_file:
                # Extract the accession and the species code pair from the line
                accession, species = line.rstrip().split(',')
                # Populate the dictionary with the accession: species pair
                accession_species_dict[accession] = species
        return accession_species_dict

    @staticmethod
    def mash_best_ref(mash_dist_dict, accession_species_dict, min_matches):
        """
        Parse the MASH dist output table to determine the closest reference sequence, as well as the total
        number of matching hashes the strain and that reference genome share
        :param mash_dist_dict: type DICT: Dictionary of strain name: absolute path of MASH dist output table
        :param accession_species_dict: type DICT: Dictionary of reference accession: species code
        :param min_matches: type INT: Minimum number of matching hashes required for a match to pass
        :return: strain_best_ref_dict: Dictionary of strain name: closest MASH-calculated reference genome
        :return: strain_ref_matches_dict: Dictionary of strain name: number of matching hashes between query and
        closest reference genome
        :return: strain_species_dict: Dictionary of strain name: species code
        """
        # Initialise dictionaries to store the strain-specific closest reference genome, number of matching hashes
        # between read sets and the reference genome, as well as the species code
        strain_best_ref_dict = dict()
        strain_ref_matches_dict = dict()
        strain_species_dict = dict()
        for strain_name, mash_dist_table in mash_dist_dict.items():
            with open(mash_dist_table, 'r') as mash_dist:
                # Extract all the data included on each line of the table outputs
                best_ref, query_id, mash_distance, p_value, matching_hashes = mash_dist.readline().rstrip().split('\t')
            # Split the total of matching hashes from the total number of hashes
            matching_hashes = int(matching_hashes.split('/')[0])
            # Populate the dictionaries appropriately
            if matching_hashes >= min_matches:
                strain_best_ref_dict[strain_name] = best_ref
                strain_ref_matches_dict[strain_name] = matching_hashes
                strain_species_dict[strain_name] = accession_species_dict[best_ref]
        return strain_best_ref_dict, strain_ref_matches_dict, strain_species_dict

    @staticmethod
    def reference_folder(strain_best_ref_dict, dependency_path):
        """
        Create a dictionary of base strain name to the folder containing all the closest reference genome dependency
        files
        :param dependency_path: type STR: Absolute path to dependency folder
        :param strain_best_ref_dict: type DICT: Dictionary of strain name: closest reference genome
        :return: reference_link_path_dict: Dictionary of strain name: relative path to symlinked reference genome
        :return: reference_link_dict: Dictionary of reference file.fasta: relative path to reference genome
        """
        # Initialise dictionaries
        reference_link_dict = dict()
        reference_link_path_dict = dict()
        # Read in the .csv file with reference file name: relative symbolic link information
        with open(os.path.join(dependency_path, 'reference_links.csv'), 'r') as reference_paths:
            for line in reference_paths:
                # Extract the link information
                reference, linked_file = line.rstrip().split(',')
                reference_link_dict[reference] = linked_file
        # Use the strain-specific best reference genome name to extract the relative symlink information
        for strain_name, best_ref in strain_best_ref_dict.items():
            reference_link_path_dict[strain_name] = reference_link_dict[best_ref]
        return reference_link_path_dict, reference_link_dict

    @staticmethod
    def index_ref_genome(reference_link_path_dict, dependency_path, logfile, reference_mapper):
        """
        Use bowtie2-build (or bwa index) to index the reference genomes
        :param reference_link_path_dict: type DICT: Dictionary of base strain name: reference folder path
        :param dependency_path: type STR: Absolute path to dependency folder
        :param logfile: type STR: Absolute path to logfile basename
        :param reference_mapper: type STR: Name of the reference mapping software to use. Choices are bwa and bowtie2
        :return: strain_mapper_index_dict: Dictionary of strain name: Absolute path to reference genome index
        :return: strain_reference_abs_path_dict: Dictionary of strain name: absolute path to reference file
        :return: strain_reference_dep_path_dict: Dictionary of strain name: absolute path to reference dependency folder
        """
        # Initialise a dictionary to store the absolute path to the bowtie2 index and reference genome
        strain_mapper_index_dict = dict()
        strain_reference_abs_path_dict = dict()
        strain_reference_dep_path_dict = dict()
        for strain_name, ref_link in reference_link_path_dict.items():
            # Set the absolute path, and strip off the file extension for use in the build call
            ref_abs_path = os.path.abspath(os.path.join(dependency_path, ref_link))
            base_name = os.path.splitext(ref_abs_path)[0]
            abs_ref_link = os.path.abspath(os.path.join(dependency_path, ref_link))
            if reference_mapper == 'bowtie2':
                build_cmd = 'bowtie2-build {ref_file} {base_name}'.format(ref_file=abs_ref_link,
                                                                          base_name=base_name)
                extension = '.1.bt2'
                strain_mapper_index_dict[strain_name] = base_name
            else:
                build_cmd = 'bwa index {ref_file}'.format(ref_file=abs_ref_link)
                extension = '.fasta.bwt'
                strain_mapper_index_dict[strain_name] = ref_abs_path
            # Only run the system call if the index files haven't already been created
            if not os.path.isfile('{base_name}{ext}'.format(base_name=base_name,
                                                            ext=extension)):
                out, err = run_subprocess(build_cmd)
                # Write the stdout and stderr to the log files
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile)
            # Populate the dictionaries
            strain_reference_abs_path_dict[strain_name] = abs_ref_link
            strain_reference_dep_path_dict[strain_name] = os.path.dirname(abs_ref_link)
        return strain_mapper_index_dict, strain_reference_abs_path_dict, strain_reference_dep_path_dict

    @staticmethod
    def map_ref_genome(strain_fastq_dict, strain_name_dict, strain_mapper_index_dict, threads, logfile,
                       reference_mapper):
        """
        Create a sorted BAM file by mapping the strain-specific FASTQ reads against the closest reference genome with
        bowtie2, converting the SAM outputs from bowtie2 to BAM format with samtools view, and sorting the BAM file
        with samtools sort. The individual commands are piped together to prevent the creation of unnecessary
        intermediate files
        :param strain_fastq_dict: type DICT: Dictionary of strain name: list of FASTQ files
        :param strain_name_dict: type DICT: Dictionary of strain name: strain-specific working folder
        :param strain_mapper_index_dict: type DICT: Dictionary of strain name: Absolute path to reference strain index
        :param threads: type INT: Number of threads to request for the analyses
        :param logfile: type STR: Absolute path to logfile basename
        :param reference_mapper: type STR: Name of the reference mapping software to use. Choices are bwa and bowtie2
        :return: strain_sorted_bam_dict: Dictionary of strain name: absolute path to sorted BAM files
        """
        # Initialise a dictionary to store the absolute path of the sorted BAM files
        strain_sorted_bam_dict = dict()
        for strain_name, fastq_files in strain_fastq_dict.items():
            try:
                # Extract the required variables from the appropriate dictionaries
                strain_folder = strain_name_dict[strain_name]
                reference_index = strain_mapper_index_dict[strain_name]
                # Set the absolute path of the sorted BAM file
                sorted_bam = os.path.join(strain_folder, '{sn}_sorted.bam'.format(sn=strain_name))
                if reference_mapper == 'bowtie2':
                    # Compound mapping command: bowtie2 (with read groups enabled: --rg-id  and --rg flags)|
                    map_cmd = 'bowtie2 --rg-id {sn} --rg SM:{sn} --rg PL:ILLUMINA --rg PI:250 -x {ref_index} ' \
                              '-U {fastq} -p {threads}'.format(sn=strain_name,
                                                               ref_index=reference_index,
                                                               fastq=','.join(fastq_files),
                                                               threads=threads)
                else:
                    # bwa mem mapping. Set the read group header to include the sample name in the ID and SM fields
                    map_cmd = 'bwa mem -M -R \"@RG\\tID:{sn}\\tSM:{sn}\\tPL:ILLUMINA\\tPI:250\" -t {threads} ' \
                              '{abs_ref_link} {fastq}'\
                        .format(sn=strain_name,
                                fastq=' '.join(fastq_files),
                                threads=threads,
                                abs_ref_link=reference_index)
                # Add the SAM-BAM conversion, duplicate read removal, and sorting commands to the mapping command
                # samtools view (-h: include headers, -b: out BAM, -T: target file)
                # samtools rmdup to remove duplicate reads
                # samtools sort
                map_cmd += ' | samtools view -@ {threads} -h -bT {abs_ref_link} -' \
                           ' | samtools rmdup - -S -' \
                           ' | samtools sort - -@ {threads} -o {sorted_bam}'\
                    .format(threads=threads,
                            abs_ref_link=reference_index,
                            sorted_bam=sorted_bam)
                # Only run the system call if the sorted BAM file doesn't already exist
                if not os.path.isfile(sorted_bam):
                    out, err = run_subprocess(map_cmd)
                    # Write STDOUT and STDERR to the logfile
                    write_to_logfile(out=out,
                                     err=err,
                                     logfile=logfile,
                                     samplelog=os.path.join(strain_folder, 'log.out'),
                                     sampleerr=os.path.join(strain_folder, 'log.err'))
                # Populate the dictionary with the absolute path to the sorted BAM file
                strain_sorted_bam_dict[strain_name] = sorted_bam
            except KeyError:
                pass
        return strain_sorted_bam_dict

    @staticmethod
    def extract_unmapped_reads(strain_sorted_bam_dict, strain_name_dict, threads, logfile):
        """
        Use samtools bam2fq to extract all unmapped reads from the sorted BAM file into a single FASTQ file
        :param strain_sorted_bam_dict: type DICT: Dictionary of strain name: absolute path to sorted BAM file
        :param strain_name_dict: type DICT: Dictionary of strain name: strain-specific working directory
        :param threads: type INT: Number of threads to request for the analyses
        :param logfile: type STR: Absolute path to the logfile basename
        :return: strain_unmapped_reads_dict: Dictionary of strain name: absolute path to unmapped reads FASTQ file
        """
        # Initialise a dictionary to store the absolute path of the unmapped reads file
        strain_unmapped_reads_dict = dict()
        for strain_name, sorted_bam in strain_sorted_bam_dict.items():
            # Extract the absolute path of the strain-specific working directory
            strain_folder = strain_name_dict[strain_name]
            # Set the absolute path of the unmapped reads FASTQ file
            unmapped_reads = os.path.join(strain_folder, '{sn}_unmapped.fastq.gz'.format(sn=strain_name))
            # Create the system call to samtools bam2fq. Use -f4 to specify unmapped reads. Pipe output to gzip
            unmapped_cmd = 'samtools bam2fq -@ {threads} -f4 {sorted_bam} | gzip > {unmapped_reads}' \
                .format(threads=threads,
                        sorted_bam=sorted_bam,
                        unmapped_reads=unmapped_reads)
            # Run the system call if the reads file does not exist
            if not os.path.isfile(unmapped_reads):
                out, err = run_subprocess(unmapped_cmd)
                # Write STDOUT and STDERR to the logfile
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile,
                                 samplelog=os.path.join(strain_folder, 'log.out'),
                                 sampleerr=os.path.join(strain_folder, 'log.err'))
            strain_unmapped_reads_dict[strain_name] = unmapped_reads
        return strain_unmapped_reads_dict

    @staticmethod
    def assemble_unmapped_reads(strain_unmapped_reads_dict, strain_name_dict, threads, logfile):
        """
        Run SKESA to attempt to assembled any unmapped reads
        :param strain_unmapped_reads_dict: type DICT: Dictionary of strain name: absolute path to unmapped reads
        FASTQ file
        :param strain_name_dict: type DICT: Dictionary of strain name: strain-specific working directory
        :param threads: type INT: Number of threads to request for the analyses
        :param logfile: type STR: Absolute path to the logfile basename
        :return: strain_skesa_output_fasta_dict: Dictionary of strain name: absolute path to SKESA assembly
        """
        # Initialise a dictionary to store the absolute path of the assembly
        strain_skesa_output_fasta_dict = dict()
        for strain_name, unmapped_reads in strain_unmapped_reads_dict.items():
            # Extract the strain-specific working directory
            strain_folder = strain_name_dict[strain_name]
            # Set the absolute path, and create the SKESA output directory
            skesa_output_dir = os.path.join(strain_folder, 'skesa')
            make_path(skesa_output_dir)
            # Set the absolute path of the contigs file
            skesa_assembly_file = os.path.join(skesa_output_dir, '{sn}_unmapped.fasta'.format(sn=strain_name))
            # Create the SKESA system call. Use a minimum contig size of 1000
            skesa_cmd = 'skesa --fastq {fastqfiles} --cores {threads} --use_paired_ends --min_contig 1000 ' \
                        '--vector_percent 1 --contigs_out {contigs}' \
                .format(fastqfiles=unmapped_reads,
                        threads=threads,
                        contigs=skesa_assembly_file)
            # Run the system call if the qualimap report does not exist
            if not os.path.isfile(skesa_assembly_file):
                out, err = run_subprocess(skesa_cmd)
                # Write STDOUT and STDERR to the logfile
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile,
                                 samplelog=os.path.join(strain_folder, 'log.out'),
                                 sampleerr=os.path.join(strain_folder, 'log.err'))
            # Populate the dictionary with the absolute path to the contigs (the file will exist, but may be empty)
            strain_skesa_output_fasta_dict[strain_name] = skesa_assembly_file
        return strain_skesa_output_fasta_dict

    @staticmethod
    def assembly_stats(strain_skesa_output_fasta_dict):
        """
        Use SeqIO to count the number of contigs that could be created from the unmapped reads
        :param strain_skesa_output_fasta_dict: type DICT: Dictionary of strain name: absolute path to skesa-created
        contigs FASTA file
        :return: strain_unmapped_contigs_dict: Dictionary of strain name: number of contigs in skesa-created contigs
        FASTA file
        """
        # Create a dictionary to store the number of contigs in the FASTA file
        strain_unmapped_contigs_dict = dict()
        for strain_name, assembly_file in strain_skesa_output_fasta_dict.items():
            # Initialise the strain-specific number of contigs as 0
            strain_unmapped_contigs_dict[strain_name] = 0
            # Ensure that the assembly file was created
            if os.path.isfile(assembly_file):
                # Check to see if the file is empty before using SeqIO to parse it
                if os.path.getsize(assembly_file) > 0:
                    # Use SeqIO to iterate through the FASTA file.
                    for _ in SeqIO.parse(assembly_file, 'fasta'):
                        # Increment the number of contigs for each sequence encountered
                        strain_unmapped_contigs_dict[strain_name] += 1
        return strain_unmapped_contigs_dict

    @staticmethod
    def samtools_index(strain_sorted_bam_dict, strain_name_dict, threads, logfile):
        """
        Index the sorted BAM file with samtools index
        :param strain_sorted_bam_dict: type DICT: Dictionary of strain name: absolute path to sorted BAM file
        :param strain_name_dict: type DICT: Dictionary of strain name: strain-specific working directory
        :param threads: type INT: Number of threads to request for the analyses
        :param logfile: type STR: Absolute path to the logfile basename
        """
        for strain_name, sorted_bam in strain_sorted_bam_dict.items():
            # Extract the folder name from the dictionary
            strain_folder = strain_name_dict[strain_name]
            # Set the system call for the samtools index command
            index_cmd = 'samtools index -@ {threads} {sorted_bam}'.format(threads=threads,
                                                                          sorted_bam=sorted_bam)
            # Only run the command if the .bai index file does not exist
            if not os.path.isfile(sorted_bam + '.bai'):
                out, err = run_subprocess(index_cmd)
                # Write STDOUT and STDERR to the logfile
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile,
                                 samplelog=os.path.join(strain_folder, 'log.out'),
                                 sampleerr=os.path.join(strain_folder, 'log.err'))

    @staticmethod
    def run_qualimap(strain_sorted_bam_dict, strain_name_dict, logfile):
        """
        Run qualimap on the sorted BAM files
        :param strain_sorted_bam_dict: type DICT: Dictionary of strain name: absolute path of sorted BAM file
        :param strain_name_dict: type DICT: Dictionary of strain name: absolute path of strain-specific working folder
        :param logfile: type STR: Absolute path of logfile basename
        :return: strain_qualimap_report_dict: Dictionary of strain name: absolute path of qualimap report
        """
        # Initialise the dictionary to store the absolute path of the qualimap report
        strain_qualimap_report_dict = dict()
        for strain_name, sorted_bam in strain_sorted_bam_dict.items():
            # Extract the absolute path of the working directory from the dictionary
            strain_folder = strain_name_dict[strain_name]
            # Set the path, and create a folder in which the qualimap results are to be stored
            qualimap_output_dir = os.path.join(strain_folder, 'qualimap')
            make_path(qualimap_output_dir)
            # Set the absolute path of the qualimap report to be parsed
            qualimap_report = os.path.join(qualimap_output_dir, 'genome_results.txt')
            # Create the qualimap system call
            qualimap_cmd = 'qualimap bamqc -bam {sorted_bam} -outdir {qualimap_out_dir}' \
                .format(sorted_bam=sorted_bam,
                        qualimap_out_dir=qualimap_output_dir)
            # Run the system call if the qualimap report does not exist
            if not os.path.isfile(qualimap_report):
                out, err = run_subprocess(qualimap_cmd)
                # Write STDOUT and STDERR to the logfile
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile,
                                 samplelog=os.path.join(strain_folder, 'log.out'),
                                 sampleerr=os.path.join(strain_folder, 'log.err'))
            # Populate the dictionary with the path to the report
            strain_qualimap_report_dict[strain_name] = qualimap_report
        return strain_qualimap_report_dict

    @staticmethod
    def parse_qualimap(strain_qualimap_report_dict):
        """
        Create a dictionary of the key: value pairs in the qualimap report
        :param strain_qualimap_report_dict: type DICT: Dictionary of strain name: absolute path of qualimap report
        :return: strain_qualimap_outputs_dict: Dictionary of strain name: dictionary of key: value from qualimap report
        """
        # Initialise a dictionary to store the qualimap outputs in dictionary format
        strain_qualimap_outputs_dict = dict()
        for strain_name, qualimap_report in strain_qualimap_report_dict.items():
            # Initialise a dictionary to hold the qualimap results - will be overwritten for each strain
            qualimap_dict = dict()
            with open(qualimap_report, 'r') as report:
                for line in report:
                    # Sanitise the keys and values using self.analyze
                    key, value = VCFMethods.analyze(line)
                    # If the keys and values exist, enter them into the dictionary
                    if (key, value) != (None, None):
                        # Populate the dictionary with the sanitised key: value pair. Strip of the 'X' from the depth
                        # values
                        qualimap_dict[key] = value.rstrip('X')
            # Populate the dictionary with the sanitised outputs
            strain_qualimap_outputs_dict[strain_name] = qualimap_dict
        return strain_qualimap_outputs_dict

    @staticmethod
    def analyze(line):
        """
        Parse lines in qualimap reports. Split lines into key, value pairs, and sanitise lines, so that these pairs
        can be added to a dictionary
        :param line: type STR: Current line from a qualimap report
        :return: Sanitised key: value pair
        """
        # Split lines on ' = '
        if ' = ' in line:
            key, value = line.split(' = ')
            # Replace occurrences of: "number of ", "'", and " " with empty strings
            key = key.replace('number of ', "").replace("'", "").title().replace(" ", "")
            # Remove commas
            value = value.replace(",", "").replace(" ", "").rstrip()
        # Extract the coverage data at a 1X threshold from the report
        elif 'coverageData >= 1X' in line:
            data = line.split()
            key = 'genome_coverage'
            value = data[3]
        # If '=' is absent, we are not interested in this line. Set the key and value to None
        else:
            key, value = None, None
        return key, value

    @staticmethod
    def deepvariant_make_examples(strain_sorted_bam_dict, strain_name_dict, strain_reference_abs_path_dict, vcf_path,
                                  home, threads, logfile, deepvariant_version, working_path=None):
        """
        Use make_examples from deepvariant to extract pileup images from sorted BAM files. Currently, deepvariant
        does not support Python 3, so it will be run in a Docker container. The make_examples command is multi-
        threaded with parallel
        :param strain_sorted_bam_dict: type DICT: Dictionary of strain name: absolute path to strain-specific
        sorted BAM file
        :param strain_name_dict: type DICT: Dictionary of strain name: absolute path to strain-specific working dir
        :param strain_reference_abs_path_dict: type DICT: Dictionary of strain name: absolute path to best reference
        genome
        :param vcf_path: type STR: Absolute path to folder in which all symlinks to .vcf files are to be created
        :param home: type STR: Absolute path to $HOME
        :param threads: type INT: Number of threads to use in the analyses
        :param logfile: type STR: Absolute path to logfile basename
        :param deepvariant_version: type STR: Version number of deepvariant docker image to use
        :param working_path: type STR: Absolute path to an additional volume to mount to docker container
        :return: strain_examples_dict: Dictionary of strain name: sorted list of deepvariant created example files
        :return: strain_variant_path: Dictionary of strain name: absolute path to deepvariant working dir
        :return: strain_gvcf_tfrecords_dict: Dictionary of strain name: absolute path to gVCF TFRecord file of
        Variant protocol buffers
        """
        # Initialise a dictionary to store the absolute paths of all the output example files
        strain_examples_dict = dict()
        strain_gvcf_tfrecords_dict = dict()
        strain_variant_path = dict()
        for strain_name, sorted_bam in strain_sorted_bam_dict.items():
            # Extract the necessary variables
            strain_folder = strain_name_dict[strain_name]
            ref_genome = strain_reference_abs_path_dict[strain_name]
            # Set the absolute path, and create the deepvariant working directory
            deepvariant_dir = os.path.join(strain_folder, 'deepvariant')
            strain_variant_path[strain_name] = deepvariant_dir
            make_path(deepvariant_dir)
            # Create the absolute path to the base name for the outputs. This will be used by parallel to create
            # all the output files
            output_example = '{output}_tfrecord'.format(output=os.path.join(deepvariant_dir, strain_name))
            gvcf_tfrecords = '{output}_gvcf'.format(output=os.path.join(deepvariant_dir, strain_name))
            strain_gvcf_tfrecords_dict[strain_name] = \
                '{gvcf_tfrecords}@{threads}.gz'.format(gvcf_tfrecords=gvcf_tfrecords,
                                                       threads=threads)
            # Create the string of volume to mount to the container. Add the working path if it has been provided
            volumes = '{home}:{home}'.format(home=home) if not working_path \
                else '{home}:{home} -v {working_path}:{working_path}'.format(home=home,
                                                                             working_path=working_path)
            # Create the system call. This consists of multiple parts:
            # 1) seq: generates range of numbers from start to end e.g. 0 to threads - 1
            # 2) parallel: executes commands in parallel. Use the following arguments:
            # --halt 2: kill all jobs if any job fails, --joblog: logfile of completed jobs, --res: store output
            # in the supplied folder
            # 3) docker run: use the deepvariant docker image to process the samples with the following arguments:
            # --rm: remove the docker container when finished, -v: mount the $HOME directory as a volume in the
            # container, --task: enables multi-processing by splitting the input, and generating sharded output
            make_example_cmd = 'seq 0 {threads_minus_1} | ' \
                               'parallel --halt 2 --joblog {logfile} --res {deepvariant_dir} ' \
                               'docker run --rm -v {volumes} ' \
                               'gcr.io/deepvariant-docker/deepvariant:{dvv} ' \
                               '/opt/deepvariant/bin/make_examples --mode calling --ref {ref} --reads {bam} ' \
                               '--examples {output_example}@{threads}.gz --gvcf {gvcf_tfrecords}@{threads}.gz ' \
                               '--task {{}}' \
                .format(threads_minus_1=threads - 1,
                        logfile=os.path.join(strain_folder, 'log.out'),
                        deepvariant_dir=deepvariant_dir,
                        dvv=deepvariant_version,
                        volumes=volumes,
                        ref=ref_genome,
                        bam=sorted_bam,
                        output_example=output_example,
                        threads=threads,
                        gvcf_tfrecords=gvcf_tfrecords)
            # Create a list of all the sharded output example files
            output_examples = glob(os.path.join(deepvariant_dir, '{strain_name}_tfrecord-*.gz'
                                                .format(strain_name=strain_name)))
            # Ensure that the final outputs don't already exist
            vcf_file_name = os.path.join(vcf_path, '{sn}.gvcf.gz'.format(sn=strain_name))
            if not os.path.isfile(vcf_file_name):
                # If there is only one thread, need to check to see if output_examples exists, and then check
                # the number of threads
                if not output_examples:
                    # If there are fewer output files than expected (when running multithreaded) or only one thread,
                    # run the system call
                    if len(output_examples) < threads - 1 or threads == 1:
                        out, err = run_subprocess(make_example_cmd)
                        write_to_logfile(out=out,
                                         err=err,
                                         logfile=logfile)
            # Populate the dictionary with the sorted list of all the sharded files
            strain_examples_dict[strain_name] = \
                sorted(glob(os.path.join(deepvariant_dir, '{strain_name}_tfrecord-*.gz'
                                         .format(strain_name=strain_name))))
        return strain_examples_dict, strain_variant_path, strain_gvcf_tfrecords_dict

    @staticmethod
    def deepvariant_call_variants(strain_variant_path_dict, strain_name_dict, dependency_path, vcf_path,
                                  home, threads, logfile, variant_caller, deepvariant_version, working_path=None):
        """
        Perform variant calling. Process deepvariant examples files with call_variant
        :param strain_variant_path_dict: type DICT: Dictionary of strain name: absolute path to deepvariant output dir
        :param strain_name_dict: type DICT: Dictionary of strain name: absolute path to strain-specific working dir
        :param dependency_path: type STR: Absolute path to dependencies folder
        :param vcf_path: type STR: Absolute path to folder in which all symlinks to .vcf files are to be created
        :param home: type STR: Absolute path to $HOME
        :param threads: type INT: Number of threads used in the analyses
        :param logfile: type STR: Absolute path to logfile basename
        :param variant_caller: type STR: Variant calling software to use. Choices are deepvariant, and deepvariant-gpu
        (has GPU support)
        :param deepvariant_version: type STR: Version number of deepvariant docker image to use
        :param working_path: type STR: Absolute path to an additional volume to mount to docker container
        :return: strain_call_variants_dict: Dictionary of strain name: absolute path to deepvariant call_variants
        outputs
        """
        # Initialise a dictionary to store the absolute path of the call_variants output file
        strain_call_variants_dict = dict()
        for strain_name in strain_variant_path_dict:
            # Extract the necessary variables from dictionaries
            deepvariant_dir = strain_variant_path_dict[strain_name]
            strain_folder = strain_name_dict[strain_name]
            # Set the absolute path of the call_variants output file
            call_variants_output = os.path.join(deepvariant_dir, '{sn}_call_variants_output_tfrecord.gz'
                                                .format(sn=strain_name))
            # Update the dictionary with the file path
            strain_call_variants_dict[strain_name] = call_variants_output
            output_example = '{output}_tfrecord'.format(output=os.path.join(deepvariant_dir, strain_name))
            # Create the string of volume to mount to the container. Add the working path if it has been provided
            volumes = '{home}:{home}'.format(home=home) if not working_path \
                else '{home}:{home} -v {working_path}:{working_path}'.format(home=home,
                                                                             working_path=working_path)
            # Set the absolute path to the deepvariant model to be used by call_variants
            if deepvariant_version == '0.8.0':
                model = '/opt/models/wgs/model.ckpt'
            else:
                model = os.path.join(dependency_path, 'deepvariant_model', 'model.ckpt')
            # Set the system call.
            if variant_caller == 'deepvariant-gpu':
                #  Use nvidia-docker to run call_variants with GPU support.
                call_variants_cmd = 'nvidia-docker run --rm -v {volumes} ' \
                                    'gcr.io/deepvariant-docker/deepvariant_gpu:{dvv} ' \
                                    '/opt/deepvariant/bin/call_variants --outfile {output_file} ' \
                                    '--examples {output_example}@{threads}.gz --checkpoint {model}'\
                    .format(volumes=volumes,
                            dvv=deepvariant_version,
                            output_file=call_variants_output,
                            output_example=output_example,
                            threads=threads,
                            model=model)
            else:
                # Use docker to run call_variants.
                call_variants_cmd = 'docker run --rm -v {volumes} gcr.io/deepvariant-docker/deepvariant:{dvv} ' \
                                    '/opt/deepvariant/bin/call_variants --outfile {output_file} ' \
                                    '--examples {output_example}@{threads}.gz --checkpoint {model}' \
                    .format(volumes=volumes,
                            dvv=deepvariant_version,
                            output_file=call_variants_output,
                            output_example=output_example,
                            threads=threads,
                            model=model)
            # Run the system call if the output file and the final outputs don't already exist
            vcf_file_name = os.path.join(vcf_path, '{sn}.gvcf.gz'.format(sn=strain_name))
            if not os.path.isfile(vcf_file_name) and not os.path.isfile(call_variants_output):
                out, err = run_subprocess(call_variants_cmd)
                # Write STDOUT and STDERR to the logfile
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile,
                                 samplelog=os.path.join(strain_folder, 'log.out'),
                                 sampleerr=os.path.join(strain_folder, 'log.err'))
        return strain_call_variants_dict

    @staticmethod
    def deepvariant_postprocess_variants_multiprocessing(strain_call_variants_dict, strain_variant_path_dict,
                                                         strain_name_dict, strain_reference_abs_path_dict,
                                                         strain_gvcf_tfrecords_dict, vcf_path, home, logfile, threads,
                                                         deepvariant_version, working_path=None):
        """
        Create .gvcf.gz outputs
        :param strain_call_variants_dict: type DICT: Dictionary of strain name: absolute path to deepvariant
        call_variants outputs
        :param strain_variant_path_dict: type DICT: Dictionary of strain name: absolute path to deepvariant output dir
        :param strain_name_dict: type DICT: Dictionary of strain name: absolute path to strain-specific working dir
        :param strain_reference_abs_path_dict: type DICT: Dictionary of strain name: absolute path to best reference
        genome
        :param strain_gvcf_tfrecords_dict: type DICT: strain_call_variants_dict: Dictionary of strain name:
        absolute path to deepvariant call_variants outputs
        :param vcf_path: type STR: Absolute path to folder in which all symlinks to .vcf files are to be created
        :param home: type STR: Absolute path to $HOME
        :param logfile: type STR: Absolute path to logfile basename
        :param threads: type INT: Number of concurrent processes to spawn
        :param deepvariant_version: type STR: Version number of deepvariant docker image to use
        :param working_path: type STR: Absolute path to an additional volume to mount to docker container
        :return: strain_vcf_dict: Dictionary of strain name: absolute path to deepvariant output VCF file
        """
        # Initialise a dictionary to store the absolute path of the .vcf.gz output files
        strain_vcf_dict = dict()
        # Create a multiprocessing pool. Limit the number of processes to the number of threads
        p = multiprocessing.Pool(processes=threads)
        # Create a list of all the strain names
        strain_list = [strain_name for strain_name in strain_call_variants_dict]
        # Determine the number of strains present in the analyses
        list_length = len(strain_list)
        # Use multiprocessing.Pool.starmap to process the samples in parallel
        # Supply the list of strains, as well as a list the length of the number of strains of each required variable
        for vcf_dict in p.starmap(VCFMethods.deepvariant_postprocess_variants,
                                  zip(strain_list,
                                      [strain_call_variants_dict] * list_length,
                                      [strain_variant_path_dict] * list_length,
                                      [strain_name_dict] * list_length,
                                      [strain_reference_abs_path_dict] * list_length,
                                      [strain_gvcf_tfrecords_dict] * list_length,
                                      [vcf_path] * list_length,
                                      [home] * list_length,
                                      [logfile] * list_length,
                                      [deepvariant_version] * list_length,
                                      [working_path] * list_length)):
            # Update the dictionaries
            strain_vcf_dict.update(vcf_dict)
        # Close and join the pool
        p.close()
        p.join()
        return strain_vcf_dict

    @staticmethod
    def deepvariant_postprocess_variants(strain_name, strain_call_variants_dict, strain_variant_path_dict,
                                         strain_name_dict, strain_reference_abs_path_dict, strain_gvcf_tfrecords_dict,
                                         vcf_path, home, logfile, deepvariant_version, working_path=None):
        """

        """
        # Initialise a dictionary to store the absolute path of the .vcf.gz output files
        strain_vcf_dict = dict()
        # for strain_name, call_variants_output in strain_call_variants_dict.items():
        call_variants_output = strain_call_variants_dict[strain_name]
        # Extract the require variables from the dictionaries
        strain_folder = strain_name_dict[strain_name]
        deepvariant_dir = strain_variant_path_dict[strain_name]
        ref_genome = strain_reference_abs_path_dict[strain_name]
        gvcf_records = strain_gvcf_tfrecords_dict[strain_name]
        # Set the absolute path to the output file
        vcf_file = os.path.join(deepvariant_dir, '{sn}.vcf.gz'.format(sn=strain_name))
        gvcf_file = os.path.join(deepvariant_dir, '{sn}.gvcf.gz'.format(sn=strain_name))
        # Update the dictionary with the path to the output file
        strain_vcf_dict[strain_name] = gvcf_file
        # Create the string of volume to mount to the container. Add the working path if it has been provided
        volumes = '{home}:{home}'.format(home=home) if not working_path \
            else '{home}:{home} -v {working_path}:{working_path}'.format(home=home,
                                                                         working_path=working_path)
        # Set the system call. Use docker to run postprocess_variants
        postprocess_variants_cmd = 'docker run --rm -v {volumes} gcr.io/deepvariant-docker/deepvariant:{dvv}' \
                                   ' /opt/deepvariant/bin/postprocess_variants --ref {ref} ' \
                                   '--nonvariant_site_tfrecord_path {gvcf_records} ' \
                                   '--infile {call_variants_output} --outfile {vcf_file} ' \
                                   '--gvcf_outfile {gvcf_file}'\
            .format(volumes=volumes,
                    dvv=deepvariant_version,
                    ref=ref_genome,
                    gvcf_records=gvcf_records,
                    call_variants_output=call_variants_output,
                    vcf_file=vcf_file,
                    gvcf_file=gvcf_file)
        # Ensure that the final outputs don't already exist
        vcf_file_name = os.path.join(vcf_path, '{sn}.gvcf.gz'.format(sn=strain_name))
        # Run the system call if the output file and the final output file don't exist
        if not os.path.isfile(vcf_file_name) and not os.path.isfile(gvcf_file):
            out, err = run_subprocess(postprocess_variants_cmd)
            # Write STDOUT and STDERR to the logfile
            write_to_logfile(out=out,
                             err=err,
                             logfile=logfile,
                             samplelog=os.path.join(strain_folder, 'log.out'),
                             sampleerr=os.path.join(strain_folder, 'log.err'))
        return strain_vcf_dict

    @staticmethod
    def parse_gvcf(strain_vcf_dict):
        """
        Determine the number of SNPs called that pass quality filters
        :param strain_vcf_dict: type DICT: Dictionary of strain name: absolute path to gVCF file
        :return: strain_num_high_quality_snps_dict: Dictionary of strain name: number of high quality SNPs present
        """
        # Initialise a dictionary to store the number of high quality SNPs
        strain_num_high_quality_snps_dict = dict()
        for strain_name, vcf_file in strain_vcf_dict.items():
            strain_num_high_quality_snps_dict[strain_name] = int()
            # Ensure that the gVCF file was created
            if os.path.isfile(vcf_file):
                # Use gzip to open the compressed gVCF file
                with gzip.open(vcf_file, 'r') as gvcf:
                    for line in gvcf:
                        # Convert the line to a string from bytes
                        line = line.decode()
                        # Skip the header section
                        if line.startswith('#CHROM'):
                            for subline in gvcf:
                                subline = subline.decode()
                                # Split the line based on the columns
                                ref_genome, pos, id_stat, ref, alt_string, qual, filter_stat, info_string, \
                                    format_stat, strain = subline.split('\t')
                                # Initialise a string to hold the clean 'alt_string'
                                alt = str()
                                # Matches will have the following alt_string format: <*>. For SNP calls, the alt_string
                                # will have the following format: G,<*>. While insertions will look like: TGCC,<*>.
                                # Replace the <*>, and split on the comma
                                alt_split = alt_string.replace('<*>', '').split(',')
                                # If alt_split has a length greater than one e.g. not a match, which will look like
                                # [''], while a SNP and an insertion will be ['G', ''] and ['TGCC', ''], respectively
                                if len(alt_split) > 1:
                                    # Iterate through the list, and ensure that only the 'G' or the 'TGCC' are examined
                                    # rather than the empty ''
                                    for sub_alt in alt_split:
                                        if sub_alt:
                                            # Set the alt string as the 'G' or the 'TGCC'
                                            alt = sub_alt
                                # Filter the lines to find the high quality SNPs
                                # They must have a 'PASS' in the filter column. As well both the reference and query
                                # base must be of length one (a SNP rather than an indel), and the quality must pass
                                # the threshold
                                if filter_stat == 'PASS' and len(ref) == 1 and len(alt) == 1 and float(qual) > 35:
                                    # Add the passing SNP to the dictionary
                                    strain_num_high_quality_snps_dict[strain_name] += 1
        return strain_num_high_quality_snps_dict

    @staticmethod
    def reference_regions(strain_reference_abs_path_dict, logfile, size=100000):
        """
        Create a regions file to be used by freebayes-parallel. This file is the base pair position of the reference
        genome in regions of a defined size (in this case 100000). The file contains the contig name: bp position range
        NC_002945.4:0-100000
        NC_002945.4:100000-200000
        :param strain_reference_abs_path_dict: type DICT: Dictionary of strain name: absolute path of reference genome
        :param logfile: type STR: Absolute path to logfile basename
        :param size: type INT: Size of regions to create from reference genome
        :return: strain_ref_regions_dict: Dictionary of strain name: regions file
        """
        # Initialise a dictionary to store the absolute path of the regions file
        strain_ref_regions_dict = dict()
        for strain_name, ref_genome in strain_reference_abs_path_dict.items():
            # Set the absolute path of the regions file
            regions_file = ref_genome + '.regions'
            # Create the system call to fasta_generate_regions.py (part of the freebayes package)
            regions_cmd = 'fasta_generate_regions.py {ref_genome}.fai {size} > {regions_file}' \
                .format(ref_genome=ref_genome,
                        size=size,
                        regions_file=regions_file)
            # Run the system call if the regions file does not exist
            if not os.path.isfile(regions_file):
                out, err = run_subprocess(regions_cmd)
                # Write STDOUT and STDERR to the logfile
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile)
            # Populate the dictionary with the path to the regions file
            strain_ref_regions_dict[strain_name] = regions_file
        return strain_ref_regions_dict

    @staticmethod
    def freebayes(strain_sorted_bam_dict, strain_name_dict, strain_reference_abs_path_dict, strain_ref_regions_dict,
                  threads, logfile):
        """
        Run freebayes-parallel on each sample
        :param strain_sorted_bam_dict: type DICT: Dictionary of strain name: absolute path of sorted BAM file
        :param strain_name_dict: type DICT: Dictionary of strain name: absolute path of strain-specific working folder
        :param strain_reference_abs_path_dict: type DICT: Dictionary of strain name: absolute path of reference genome
        :param strain_ref_regions_dict: type DICT: Dictionary of strain name: absolute path to reference genome
        regions file
        :param threads: type INT: Number of threads to request for the analyses
        :param logfile: type STR: Absolute path to logfile basename
        :return: strain_vcf_dict: Dictionary of strain name: freebayes-created .vcf file
        """
        # Initialise a dictionary to store the absolute path to the .vcf files
        strain_vcf_dict = dict()
        for strain_name, sorted_bam in strain_sorted_bam_dict.items():
            # Extract the paths to the strain-specific working directory, the reference genome, and the regions file
            strain_folder = strain_name_dict[strain_name]
            ref_genome = strain_reference_abs_path_dict[strain_name]
            ref_regions_file = strain_ref_regions_dict[strain_name]
            # Set the absolute path to, and create the freebayes working directory
            freebayes_out_dir = os.path.join(strain_folder, 'freebayes')
            make_path(freebayes_out_dir)
            # Set the name of the output .vcf file
            freebayes_out_vcf = os.path.join(freebayes_out_dir, '{sn}.gvcf'.format(sn=strain_name))
            # Create the system call to freebayes-parallel
            # Use the regions file to allow for parallelism
            # Output in gVCF format with --gvcf, and emit records for all bases with --gvcf-dont-use-chunk true
            freebayes_cmd = 'freebayes-parallel {ref_regions} {threads} --strict-vcf --gvcf ' \
                            '--gvcf-dont-use-chunk true --use-best-n-alleles 1 -f {ref_genome} {sorted_bam} ' \
                            '> {out_vcf}' \
                .format(ref_regions=ref_regions_file,
                        ref_genome=ref_genome,
                        threads=threads,
                        sorted_bam=sorted_bam,
                        out_vcf=freebayes_out_vcf)
            # Run the system call if the .vcf file does not exist
            if not os.path.isfile(freebayes_out_vcf):
                out, err = run_subprocess(freebayes_cmd)
                # Write STDOUT and STDERR to the logfile
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile,
                                 samplelog=os.path.join(strain_folder, 'log.out'),
                                 sampleerr=os.path.join(strain_folder, 'log.err'))
            if os.path.isfile(freebayes_out_vcf):
                # Populate the dictionary with the path to the .vcf file
                strain_vcf_dict[strain_name] = freebayes_out_vcf
        return strain_vcf_dict

    @staticmethod
    def parse_vcf(strain_vcf_dict):
        """
        Parse the .vcf file. Filter positions with QUAL < 150, and count the number of high
        quality SNPs (QUAL >= 150, and reference length = 1 (not an indel)). Also store indels and zero coverage
        regions. Overwrite the original file
        :param strain_vcf_dict: type DICT: Dictionary of strain name: absolute path to .vcf file
        :return: strain_num_high_quality_snps_dict: Dictionary of strain name: number of high quality SNPs
        """
        # Initialise dictionaries to store the number of high quality SNPs, and the absolute path to the filtered
        # .vcf file
        strain_num_high_quality_snps_dict = dict()
        for strain_name, vcf_file in strain_vcf_dict.items():
            try:
                # Set the absolute path of the filtered .vcf file (replace the .vcf extension with _filtered.vcf)
                filtered_vcf = vcf_file.replace('.gvcf', '_filtered.gvcf')
                # Initialise a count for the number of high quality SNPs
                strain_num_high_quality_snps_dict[strain_name] = 0
                # # Iterate through all the records in the .vcf file
                with open(vcf_file, 'r') as unfiltered:
                    with open(filtered_vcf, 'w') as filtered:
                        for line in unfiltered:
                            # Add the VCF file header information to the filtered file
                            if line.startswith('#'):
                                filtered.write(line)
                            else:
                                # Split the line based on the columns
                                ref_genome, pos, id_stat, ref, alt_string, qual, filter_stat, info_string, \
                                    format_stat, strain = line.rstrip().split('\t')
                                # Find the depth entry. e.g. DP=11
                                depth_group = re.search('(DP=[0-9]+)', info_string)
                                # Split the depth matching group on '=' and convert the depth to an int
                                depth = int(str(depth_group.group()).split('=')[1])
                                # Store the zero coverage entries
                                if depth == 0:
                                    filtered.write(line)
                                else:
                                    #
                                    if len(ref) == 1:
                                        # Only store SNPs with a quality score greater or equal to 150
                                        if float(qual) >= 150:
                                            # Populate the dictionaries with the number of high quality SNPs
                                            strain_num_high_quality_snps_dict[strain_name] += 1
                                            filtered.write(line)
                                    # Store all indels
                                    else:
                                        filtered.write(line)
                # Remove the giant unfiltered file
                os.remove(vcf_file)
                # Rename the filtered file with the original file name
                shutil.move(src=filtered_vcf,
                            dst=vcf_file)
            except FileNotFoundError:
                pass
        return strain_num_high_quality_snps_dict

    @staticmethod
    def copy_vcf_files(strain_vcf_dict, vcf_path):
        """
        Create a folder with copies of the .vcf files
        :param strain_vcf_dict: type DICT: Dictionary of strain name: absolute path to .vcf files
        :param vcf_path: type STR: Absolute path to folder in which all .gvcf.gz files are to be copied
        :return:
        """
        make_path(vcf_path)
        for strain_name, vcf_file in strain_vcf_dict.items():
            # Extract the file name of the gVCF file
            vcf_file_name = os.path.basename(vcf_file)
            if os.path.isfile(vcf_file):
                shutil.copyfile(src=vcf_file,
                                dst=os.path.join(vcf_path, vcf_file_name))

    @staticmethod
    def bait_spoligo(strain_fastq_dict, strain_name_dict, spoligo_file, threads, logfile, kmer=25):
        """
        Use bbduk.sh to bait reads matching the spacer sequences. Output a file with the number of matches to each
        spacer sequence
        :param strain_fastq_dict: type DICT: Dictionary of strain name: list of FASTQ files
        :param strain_name_dict: type DICT: Dictionary of strain name: strain-specific working folder
        :param spoligo_file: type STR: Absolute path to FASTA-formatted file of spacer sequences
        :param threads: type INT: Number of threads to request for the analyses
        :param logfile: type STR: Absolute path to the logfile basename
        :param kmer: type INT: kmer size to use for read baiting. Default value of 25 is used, as the spacer sequences
        are all 25 bp long
        :return: strain_spoligo_stats_dict: Dictionary of strain name: absolute path to bbduk-created stats file
        """
        # Initialise a dictionary to store the absolute path to the bbduk-created stats file
        strain_spoligo_stats_dict = dict()
        for strain_name, fastq_files in strain_fastq_dict.items():
            # Extract the strain-specific working directory from the dictionary
            strain_folder = strain_name_dict[strain_name]
            # Set the absolute path, and create a directory to store the spoligotyping outputs
            spoligo_path = os.path.join(strain_folder, 'spoligotyping')
            make_path(spoligo_path)
            # Set the absolute path to the bbduk-outputted stats file
            baited_spoligo_stats = os.path.join(spoligo_path, '{sn}_stats.txt'.format(sn=strain_name))
            # Single-end reads are treated differently
            if len(fastq_files) == 1:
                # Create the system call to bbduk.sh. Use the desired kmer size. Set maskmiddle to False
                # (middle base of a kmer is NOT treated as a wildcard). Allow one mismatch
                bait_cmd = 'dedupe.sh in={in1} out=stdout.fq | bbduk.sh ref={ref} in=stdin.fq int=f k={kmer} ' \
                           'hdist=1 threads={threads} maskmiddle=f ' \
                           'stats={stats_file}'.format(ref=spoligo_file,
                                                       in1=fastq_files[0],
                                                       kmer=kmer,
                                                       threads=threads,
                                                       stats_file=baited_spoligo_stats)
            else:
                bait_cmd = 'dedupe.sh in={in1} in2={in2} out=stdout.fq | bbduk.sh ref={ref} in=stdin.fq ' \
                           'int=t k={kmer} threads={threads} ' \
                           'maskmiddle=f hdist=1 stats={stats_file}' \
                    .format(ref=spoligo_file,
                            in1=fastq_files[0],
                            in2=fastq_files[1],
                            kmer=kmer,
                            threads=threads,
                            stats_file=baited_spoligo_stats)
            # Run the system call if the stats file does not exist
            if not os.path.isfile(baited_spoligo_stats):
                out, err = run_subprocess(bait_cmd)
                # Write STDOUT and STDERR to the logfile
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=logfile,
                                 samplelog=os.path.join(strain_folder, 'log.out'),
                                 sampleerr=os.path.join(strain_folder, 'log.err'))
            # Populate the dictionary with the absolute path to the stats file
            strain_spoligo_stats_dict[strain_name] = baited_spoligo_stats
        return strain_spoligo_stats_dict

    @staticmethod
    def parse_spoligo(strain_spoligo_stats_dict):
        """
        Parse the bbduk-created spacer match stats file to create binary, octal, and hexadecimal code for the strain
        :param strain_spoligo_stats_dict: type DICT: Dictionary of strain name: absolute path to stats file
        :return: strain_binary_code_dict: Dictionary of strain name: string of presence/absence of all spacer sequences
        :return: strain_octal_code_dict: Dictionary of strain name: string of octal code converted from binary string
        :return: strain_hexadecimal_code_dict: Dictionary of strain name: string of hexadecimal code converted
        from binary string
        """
        # Initialise dictionaries to store the calculated codes
        strain_binary_code_dict = dict()
        strain_octal_code_dict = dict()
        strain_hexadecimal_code_dict = dict()
        for strain_name, spoligo_stats_file in strain_spoligo_stats_dict.items():
            # Initialise a dictionary to store the spacer counts
            stats_dict = dict()
            with open(spoligo_stats_file, 'r') as stats_file:
                for line in stats_file:
                    # Ignore all headers
                    if '#Name' in line:
                        for subline in stats_file:
                            # Split the results on tabs into its constituent spacer, reads containing this spacer, and
                            # the total percent of reads from the read set, which contain this spacer
                            # e.g. spacer2	13	0.00325%
                            spacer, reads, reads_percent = subline.rstrip().split('\t')
                            # Populate the dictionary with the spacer name, and the number of reads
                            stats_dict[spacer] = reads
            # Convert the dictionary to a string of presence/absence for each spacer
            binary_string = VCFMethods.create_binary_code(stats_dict=stats_dict)
            # Create the octal code string from the binary string
            octal_string = VCFMethods.binary_to_octal(binary_code=binary_string)
            # Create the hexadecimal string from the binary string
            hexadecimal_string = VCFMethods.binary_to_hexadecimal(binary_code=binary_string)
            # Populate the dictionaries with the appropriate variables
            strain_binary_code_dict[strain_name] = binary_string
            strain_octal_code_dict[strain_name] = octal_string
            strain_hexadecimal_code_dict[strain_name] = hexadecimal_string
        return strain_binary_code_dict, strain_octal_code_dict, strain_hexadecimal_code_dict

    @staticmethod
    def create_binary_code(stats_dict):
        """
        Create a binary string of presence/absence of each spacer sequence (1: present, 0: absent)
        :param stats_dict: type DICT: Dictionary of spacer name: number of reads
        :return: binary_string: A string of presence/absence for each of the 43 spacer sequences
        """
        # Initialise a string to store the calculated binary string
        binary_string = str()
        # There are 43 spacer sequences, named spacer1 - spacer43. Will create a list of 1:43
        for i in range(1, 44):
            # Use the iterator to create the current spacer name e.g. spacer + 1
            spacer_name = 'spacer{num}'.format(num=i)
            # If the spacer name is in the dictionary, count this spacer as present
            if spacer_name in stats_dict:
                binary_hits = '1'
            # Otherwise, the spacer is absent
            else:
                binary_hits = '0'
            # Add the present/absence result to the growing binary code string
            binary_string += binary_hits
        return binary_string

    @staticmethod
    def binary_to_octal(binary_code):
        """
        Convert a supplied binary string to an octal code
        for example, 1101000000000010111111111111111101111100000 becomes 640013777767600
        :param binary_code: type STR: 43 character binary string of spacer presence/absence
        :return: octal_code: Converted octal string
        """
        # Initialise the string to store the octal code
        octal_code = str()
        # Iterate through the binary string in blocks of three (binary triplet)
        # e.g. 1101000000000010111111111111111101111100000 treated as: 110 100 000 000 001 011... etc.
        for i in range(0, len(binary_code), 3):
            # Convert the current binary triplet to an integer using int() with base 2 (e.g. 110 becomes 6)
            # Append the str() of the integer to the octal code string
            octal_code += str(int(binary_code[i:i + 3], 2))
        return octal_code

    @staticmethod
    def binary_to_hexadecimal(binary_code):
        """
        Convert a supplied binary string to a hexadecimal code
        for example, 1101000000000010111111111111111101111100000 becomes 68-0-5F-7F-F7-60
        :param binary_code: type STR: 43 character binary string of spacer presence/absence
        :return: hex_code: Converted hexadecimal string
        """
        # Initialise a string to store the hexadecimal string
        hex_code = str()
        # Iterate through the binary string in blocks of seven four times, and blocks of eight twice (the binary
        # string is 43 characters long, yielding ranges of 0:7, 7:14, 14:21, 21:28, 28:36, 36:43
        # e.g. 1101000000000010111111111111111101111100000 becomes 1101000 0000000 1011111 1111111 11110111 1100000
        # These fragments are converted to hexadecimal:              0x68    0x0     0x5f    0x7f    0xf7     0x60
        for i in range(0, len(binary_code), 7):
            # The first four blocks are all treated the same
            if i < 28:
                # Convert the block of seven digits with to int(), base 2, and then to hexadecimal
                hex_section = hex(int(binary_code[i:i + 7], 2))
                # Remove the '0x' hexadecimal designation, and convert the string to uppercase. Add a dash for
                # formatting reasons. Append this string to the growing hex_code string
                hex_code += str(hex_section.replace('0x', '').upper()) + '-'
            # The penultimate block is eight characters long, so the range of the block is i: i+8
            elif i < 35:
                hex_section = hex(int(binary_code[i:i + 8], 2))
                hex_code += (hex_section.replace('0x', '').upper()) + '-'
            # The final block is also eight characters long, but additionally, since the previous block was longer than
            # the step size, i must be incremented
            else:
                # Increment i to reflect the longer size of the previous block
                i += 1
                hex_section = hex(int(binary_code[i:i + 8], 2))
                hex_code += (hex_section.replace('0x', '').upper())
                # Break the loop here, as it will attempt to iterate one more time, but will encounter an empty string
                # due to the incrementing of i
                break
        return hex_code

    @staticmethod
    def extract_sbcode(strain_reference_dep_path_dict, strain_octal_code_dict):
        """
        Query the reference spoligotype_db.txt file using the calculated octal code to extract the sbcode
        :param strain_reference_dep_path_dict: type DICT: Dictionary of strain name: path to reference dependency folder
        :param strain_octal_code_dict: type DICT: Dictionary of strain name: calculated strain octal code
        :return: strain_sbcode_dict: Dictionary of strain name: extracted sbcode
        """
        # Initialise the dictionary to store the extracted sbcode
        strain_sbcode_dict = dict()
        for strain_name, reference_abs_path in strain_reference_dep_path_dict.items():
            # Extract the octal code from the dictionary
            strain_octal_code = strain_octal_code_dict[strain_name]
            # Set the absolute path of the spoligotype db file
            spoligo_db_file = os.path.join(reference_abs_path, 'spoligotype_db.txt')
            # Create a dictionary to store the octal code: sbcode pairs extracted from the file
            spoligo_dict = dict()
            if os.path.isfile(spoligo_db_file):
                with open(spoligo_db_file, 'r') as spoligo_db:
                    for line in spoligo_db:
                        octal_code, sbcode, binary_code = line.split()
                        spoligo_dict[octal_code] = sbcode
            # Add the sbcode value for the strain-specific octal code key to the dictionary
            if strain_octal_code in spoligo_dict:
                strain_sbcode_dict[strain_name] = spoligo_dict[strain_octal_code]
            # If the key is absent populate the dictionary with 'Not Detected' ('ND')
            else:
                strain_sbcode_dict[strain_name] = 'ND'
        return strain_sbcode_dict

    @staticmethod
    def brucella_mlst(seqpath, mlst_db_path, logfile):
        """
        Run MLST analyses on the strains
        :param seqpath: type STR: Absolute path to folder containing FASTQ files
        :param mlst_db_path: type STR: Absolute path to folder containing Brucella MLST database files
        :param logfile: type STR: Absolute path to the logfile basename
        """
        # Set the system call to the MLST python package in sipprverse
        mlst_cmd = 'python -m genemethods.MLSTsippr.mlst -s {seqpath} -t {targetpath} -a mlst {seqpath}' \
            .format(seqpath=seqpath,
                    targetpath=mlst_db_path)
        # Run the system call - don't worry about checking if there are outputs, the package will parse these reports
        # rather than re-running the analyses
        out, err = run_subprocess(mlst_cmd)
        # Write STDOUT and STDERR to the logfile
        write_to_logfile(out=out,
                         err=err,
                         logfile=logfile)

    @staticmethod
    def parse_mlst_report(strain_name_dict, mlst_report):
        """
        Parse the MLST report to create a dictionary with the calculated sequence type and the number of exact matches
        per strain to the sequence type
        :param strain_name_dict: type DICT: Dictionary of strain name: absolute path to strain working directory
        :param mlst_report: type STR: Absolute path to MLST report
        :return: strain_mlst_dict: Dictionary of strain name: sequence type and number of matches to the sequence type
        """
        # Initialise a dictionary to store the parsed MLST results
        strain_mlst_dict = dict()
        # Open the MLST report file
        with open(mlst_report, 'r') as report:
            # Skip the header line
            next(report)
            for line in report:
                # Split the line on commas
                data = line.rstrip().split(',')
                # Extract the sequence type and the number of matches to the sequence type from the line. Populate the
                # dictionary with these values
                strain_mlst_dict[data[0]] = {
                    'sequence_type': data[2],
                    'matches': data[3],
                }
        # If the strain did not have MLST outputs, populate negative 'ND' values for the sequence type and number
        # of matches
        for strain in strain_name_dict:
            # Only populate negative values for strains absent from the outputs
            if strain not in strain_mlst_dict:
                strain_mlst_dict[strain] = {
                    'sequence_type': 'ND',
                    'matches': 'ND',
                }
        return strain_mlst_dict

    @staticmethod
    def create_vcf_report(start_time, strain_species_dict, strain_best_ref_dict, strain_fastq_size_dict,
                          strain_average_quality_dict, strain_qual_over_thirty_dict, strain_qualimap_outputs_dict,
                          strain_avg_read_lengths, strain_unmapped_contigs_dict, strain_num_high_quality_snps_dict,
                          strain_mlst_dict, strain_octal_code_dict, strain_sbcode_dict, strain_hexadecimal_code_dict,
                          strain_binary_code_dict, report_path):
        """
        Create an Excel report of the vcf outputs
        :param start_time: type datetime.now(): Datetime object
        :param strain_species_dict: type DICT: Dictionary of strain name: species code
        :param strain_best_ref_dict: type DICT: Dictionary of strain name: closest reference genome
        :param strain_fastq_size_dict: type DICT: Dictionary of strain name: list of sizes of FASTQ files in megabytes
        :param strain_average_quality_dict: type DICT: Dictionary of strain name: list of read set-specific average
        quality scores
        :param strain_qual_over_thirty_dict: type DICT: Dictionary of strain name: list of read set-specific percentage
        of reads with a Phred quality-score greater or equal to 30
        :param strain_qualimap_outputs_dict: type DICT: Dictionary of strain name: dictionary of key: value from
        qualimap report
        :param strain_avg_read_lengths: type DICT: Dictionary of strain name: float of calculated strain-specific
        average read length
        :param strain_unmapped_contigs_dict: type DICT: Dictionary of strain name: number of contigs in skesa-created
        contigs FASTA file
        :param strain_num_high_quality_snps_dict: type DICT: Dictionary of strain name: number of high quality SNPs
        :param strain_mlst_dict: type DICT: Dictionary of strain name: sequence type and number of matches to the
        sequence type
        :param strain_octal_code_dict: type DICT: Dictionary of strain name: calculated strain octal code
        :param strain_sbcode_dict: type DICT: Dictionary of strain name: extracted sbcode
        :param strain_hexadecimal_code_dict: type DICT: Dictionary of strain name: string of hexadecimal code converted
        from binary string
        :param strain_binary_code_dict: type DICT: Dictionary of strain name: string of presence/absence of all spacer
        sequences
        :param report_path: type STR: Absolute path to path in which reports are to be created
        :return: vcf_report: Absolute path to the Excel report
        """
        # Create a date string consistent with classic vSNP
        start = '{:%Y-%m-%d_%H-%M-%S}'.format(start_time)
        # Initialise a string to store the absolute path to the Excel report
        vcf_report = os.path.join(os.path.join(report_path, 'stat_alignment_summary_{start}.xlsx'
                                               .format(start=start)))
        # Set the list of the headers
        header_list = ['time_stamp', 'sample_name', 'species', 'reference_sequence_name', 'R1size', 'R2size',
                       'Q_ave_R1', 'Q_ave_R2', 'Q30_R1', 'Q30_R2', 'allbam_mapped_reads', 'genome_coverage',
                       'ave_coverage', 'ave_read_length', 'unmapped_reads', 'unmapped_assembled_contigs',
                       'good_snp_count', 'mlst_type', 'octalcode', 'sbcode', 'hexadecimal_code', 'binarycode']
        # Create a workbook to store the report using xlsxwriter.
        workbook = xlsxwriter.Workbook(vcf_report)
        # New worksheet to store the data
        worksheet = workbook.add_worksheet()
        # Add a bold format for header cells. Using a monotype font size 10
        bold = workbook.add_format({'bold': True, 'font_name': 'Courier New', 'font_size': 10})
        # Format for data cells. Monotype, size 10, top vertically justified
        courier = workbook.add_format({'font_name': 'Courier New', 'font_size': 10})
        courier.set_align('top')
        # Initialise the position within the worksheet to be (0,0)
        row = 0
        # Set the column to zero
        col = 0
        # Write the header to the spreadsheet
        for header in header_list:
            worksheet.write(row, col, header, bold)
            col += 1
        for strain_name, fastq_sizes in strain_fastq_size_dict.items():
            # Increment the row and reset the column to zero in preparation of writing results
            row += 1
            col = 0
            # Extract all the required entries from the dictionaries

            # Set all the floats to have two decimal places
            forward_size = '{:.2f}'.format(fastq_sizes[0])
            forward_avg_quality = '{:.2f}'.format(strain_average_quality_dict[strain_name][0])
            forward_perc_reads_over_thirty = '{:.2f}%'.format(strain_qual_over_thirty_dict[strain_name][0])
            # Allow strains that do not have a match to be added to the report
            try:
                strain_species = strain_species_dict[strain_name]
                best_ref = os.path.splitext(strain_best_ref_dict[strain_name])[0]
                genome_coverage = strain_qualimap_outputs_dict[strain_name]['genome_coverage']
                avg_cov_depth = '{:.2f}'.format(float(strain_qualimap_outputs_dict[strain_name]['MeanCoveragedata']))
                avg_read_length = '{:.2f}'.format(strain_avg_read_lengths[strain_name])
                mapped_reads = strain_qualimap_outputs_dict[strain_name]['MappedReads'].split('(')[0]
                # Subtract the number of mapped reads from the total number of reads to determine the number of
                # unmapped reads
                unmapped_reads = int(strain_qualimap_outputs_dict[strain_name]['Reads']) - int(mapped_reads)
                num_unmapped_contigs = strain_unmapped_contigs_dict[strain_name]
                high_quality_snps = strain_num_high_quality_snps_dict[strain_name]
                ml_seq_type = strain_mlst_dict[strain_name]['sequence_type']
                octal_code = strain_octal_code_dict[strain_name]
                sbcode = strain_sbcode_dict[strain_name]
                hex_code = strain_hexadecimal_code_dict[strain_name]
                binary_code = strain_binary_code_dict[strain_name]
                # Brucella will not have a 'real' octal code. Find this string and replace it with 'ND'. Set
                # the hex_code and binary codes to for this Brucella strain to 'ND'
                octal_code = octal_code if octal_code != '000000000000000' else 'ND'
                hex_code = hex_code if octal_code != 'ND' else 'ND'
                binary_code = binary_code if octal_code != 'ND' else 'ND'
            except KeyError:
                strain_species = 'ND'
                best_ref = 'ND'
                genome_coverage = 'ND'
                avg_cov_depth = 'ND'
                avg_read_length = 'ND'
                mapped_reads = 'ND'
                unmapped_reads = 'ND'
                num_unmapped_contigs = 'ND'
                high_quality_snps = 'ND'
                ml_seq_type = 'ND'
                octal_code = 'ND'
                sbcode = 'ND'
                hex_code = 'ND'
                binary_code = 'ND'
            # If there are no reverse reads, populate the variables with 'ND'
            try:
                reverse_size = '{:.2f}'.format(fastq_sizes[1])
                reverse_avg_quality = '{:.2f}'.format(strain_average_quality_dict[strain_name][1])
                reverse_perc_reads_over_thirty = '{:.2f}%'.format(strain_qual_over_thirty_dict[strain_name][1])
            except IndexError:
                reverse_size = 'ND'
                reverse_avg_quality = 'ND'
                reverse_perc_reads_over_thirty = 'ND'
            # Populate the list with the required data
            data_list = [start, strain_name, strain_species, best_ref, forward_size, reverse_size, forward_avg_quality,
                         reverse_avg_quality, forward_perc_reads_over_thirty, reverse_perc_reads_over_thirty,
                         mapped_reads,
                         genome_coverage, avg_cov_depth, avg_read_length, unmapped_reads, num_unmapped_contigs,
                         high_quality_snps, ml_seq_type, octal_code, sbcode, hex_code, binary_code]
            # Write out the data to the spreadsheet
            for results in data_list:
                worksheet.write(row, col, results, courier)
                col += 1
        # Close the workbook
        workbook.close()
        return vcf_report
