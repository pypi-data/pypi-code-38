#!/usr/bin/env python3
from genewrappers.biotools import mash
from Bio.SeqUtils import GC
import multiprocessing
from Bio import SeqIO
from glob import glob
import subprocess
import shutil
import click
import time
import os
__author__ = 'adamkoziol', 'andrewlow'


def main(sequencepath, report, refseq_database, num_threads=12):
    """
    Run the appropriate functions in order
    :param sequencepath: path of folder containing FASTA genomes
    :param report: boolean to determine whether a report is to be created
    :param refseq_database: Path to reduced refseq database sketch
    :param num_threads: Number of threads to run mash/other stuff on
    :return: gc_dict, contig_dist_dict, longest_contig_dict, genome_length_dict, num_contigs_dict, n50_dict, n75_dict, \
        n90_dict, l50_dict, l75_dict, l90_dict, orf_dist_dict
    """
    files = find_files(sequencepath)
    file_dict = filer(files)
    print('Using MASH to determine genera of samples')
    genus_dict = find_genus(files=file_dict,
                            database=refseq_database,
                            sequencepath=sequencepath,
                            threads=num_threads)
    file_records = fasta_records(file_dict)
    print('Collecting basic quality metrics')
    contig_len_dict, gc_dict = fasta_stats(file_dict, file_records)
    contig_dist_dict = find_contig_distribution(contig_len_dict)
    longest_contig_dict = find_largest_contig(contig_len_dict)
    genome_length_dict = find_genome_length(contig_len_dict)
    num_contigs_dict = find_num_contigs(contig_len_dict)
    n50_dict = find_n50(contig_len_dict, genome_length_dict)
    n75_dict = find_n75(contig_len_dict, genome_length_dict)
    n90_dict = find_n90(contig_len_dict, genome_length_dict)
    l50_dict = find_l50(contig_len_dict, genome_length_dict)
    l75_dict = find_l75(contig_len_dict, genome_length_dict)
    l90_dict = find_l90(contig_len_dict, genome_length_dict)
    print('Using prodigal to calculate number of ORFs in each sample')
    orf_file_dict = predict_orfs(file_dict, num_threads=num_threads)
    orf_dist_dict = find_orf_distribution(orf_file_dict)
    if report:
        reporter(gc_dict, contig_dist_dict, longest_contig_dict, genome_length_dict, num_contigs_dict, n50_dict,
                 n75_dict, n90_dict, l50_dict, l75_dict, l90_dict, orf_dist_dict, genus_dict, sequencepath)
    print('Features extracted!')
    return gc_dict, contig_dist_dict, longest_contig_dict, genome_length_dict, num_contigs_dict, n50_dict, n75_dict, \
        n90_dict, l50_dict, l75_dict, l90_dict, orf_dist_dict


def find_files(sequencepath):
    """
    Use glob to find all FASTA files in the provided sequence path. NOTE: FASTA files must have an extension such as
    .fasta, .fa, or .fas. Extensions of .fsa, .tfa, ect. are not currently supported
    :param sequencepath: path of folder containing FASTA genomes
    :return: list of FASTA files
    """
    # Create a sorted list of all the FASTA files in the sequence path
    files = sorted(glob(os.path.join(sequencepath, '*.fa*')))
    return files


def filer(filelist):
    """
    Helper script that creates a dictionary of the stain name: /sequencepath/strain_name.extension)
    :param filelist: list of files to parse
    :return filedict: dictionary of stain name: /sequencepath/strain_name.extension
    """
    # Initialise the dictionary
    filedict = dict()
    for seqfile in filelist:
        # Split off the file extension and remove the path from the name
        strainname = os.path.splitext(os.path.basename(seqfile))[0]
        # Populate the dictionary
        filedict[strainname] = seqfile
    return filedict


def fasta_records(files):
    """
    Use SeqIO to create dictionaries of all records for each FASTA file
    :param files: dictionary of stain name: /sequencepath/strain_name.extension
    :return: file_records: dictionary of all contig records for all strains
    """
    # Initialise the dictionary
    file_records = dict()
    for file_name, fasta in files.items():
        # Create a dictionary of records for each file
        record_dict = SeqIO.to_dict(SeqIO.parse(fasta, "fasta"))
        # Set the records dictionary as the value for file_records
        file_records[file_name] = record_dict
    return file_records


def find_genus(files, database, sequencepath, threads=12):
    """
    Uses MASH to find the genus of fasta files.
    :param files: File dictionary returned by filer method.
    :param database: Path to reduced refseq database sketch.
    :param sequencepath: Path to sequences
    :param threads: Number of threads to run mash with.
    :return: genus_dict: Dictionary of genus for each sample. Will return NA if genus could not be found.
    """
    genus_dict = dict()
    tmpdir = os.path.join(sequencepath, str(time.time()).split('.')[-1])
    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)
    for file_name, fasta in files.items():
        mash.screen(database, fasta,
                    threads=threads,
                    w='',
                    i=0.95,
                    output_file=os.path.join(tmpdir, 'screen.tab'))
        screen_output = mash.read_mash_screen(os.path.join(tmpdir, 'screen.tab'))
        try:
            os.remove(os.path.join(tmpdir, 'screen.tab'))
        except IOError:
            pass
        try:
            genus = screen_output[0].query_id.split('/')[-3]
            if genus == 'Shigella':
                genus = 'Escherichia'
            genus_dict[file_name] = genus
        except IndexError:
            genus_dict[file_name] = 'NA'

    shutil.rmtree(tmpdir)
    return genus_dict


def fasta_stats(files, records):
    """
    Parse the lengths of all contigs for each sample, as well as the total GC%
    :param files: dictionary of stain name: /sequencepath/strain_name.extension
    :param records: Dictionary of strain name: SeqIO records
    :return: contig_len_dict, gc_dict: dictionaries of list of all contig length, and total GC% for all strains
    """
    # Initialise dictionaries
    contig_len_dict = dict()
    gc_dict = dict()
    for file_name in files:
        # Initialise variables to store appropriate values parsed from contig records
        contig_lengths = list()
        fasta_sequence = str()
        for contig, record in records[file_name].items():
            # Append the length of the contig to the list
            contig_lengths.append(len(record.seq))
            # Add the contig sequence to the string
            fasta_sequence += record.seq
        # Set the reverse sorted (e.g. largest to smallest) list of contig sizes as the value
        contig_len_dict[file_name] = sorted(contig_lengths, reverse=True)
        # Calculate the GC% of the total genome sequence using GC - format to have two decimal places
        gc_dict[file_name] = float('{:0.2f}'.format(GC(fasta_sequence)))
    return contig_len_dict, gc_dict


def find_contig_distribution(contig_lengths_dict):
    """
    Determine the frequency of different contig size ranges for each strain
    :param contig_lengths_dict:
    :return: contig_len_dist_dict: dictionary of strain name: tuple of contig size range frequencies
    """
    # Initialise the dictionary
    contig_len_dist_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        # Initialise integers to store the number of contigs that fall into the different bin sizes
        over_1000000 = 0
        over_500000 = 0
        over_100000 = 0
        over_50000 = 0
        over_10000 = 0
        over_5000 = 0
        other = 0
        for contig_length in contig_lengths:
            # Depending on the size of the contig, increment the appropriate integer
            if contig_length > 1000000:
                over_1000000 += 1
            elif contig_length > 500000:
                over_500000 += 1
            elif contig_length > 100000:
                over_100000 += 1
            elif contig_length > 50000:
                over_50000 += 1
            elif contig_length > 10000:
                over_10000 += 1
            elif contig_length > 5000:
                over_5000 += 1
            else:
                other += 1
        # Populate the dictionary with a tuple of each of the size range frequencies
        contig_len_dist_dict[file_name] = (over_1000000,
                                           over_500000,
                                           over_100000,
                                           over_50000,
                                           over_10000,
                                           over_5000,
                                           other)
    return contig_len_dist_dict


def find_largest_contig(contig_lengths_dict):
    """
    Determine the largest contig for each strain
    :param contig_lengths_dict: dictionary of strain name: reverse-sorted list of all contig lengths
    :return: longest_contig_dict: dictionary of strain name: longest contig
    """
    # Initialise the dictionary
    longest_contig_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        # As the list is sorted in descending order, the largest contig is the first entry in the list
        longest_contig_dict[file_name] = contig_lengths[0]
    return longest_contig_dict


def find_genome_length(contig_lengths_dict):
    """
    Determine the total length of all the contigs for each strain
    :param contig_lengths_dict: dictionary of strain name: reverse-sorted list of all contig lengths
    :return: genome_length_dict: dictionary of strain name: total genome length
    """
    # Initialise the dictionary
    genome_length_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        # Use the sum() method to add all the contig lengths in the list
        genome_length_dict[file_name] = sum(contig_lengths)
    return genome_length_dict


def find_num_contigs(contig_lengths_dict):
    """
    Count the total number of contigs for each strain
    :param contig_lengths_dict: dictionary of strain name: reverse-sorted list of all contig lengths
    :return: num_contigs_dict: dictionary of strain name: total number of contigs
    """
    # Initialise the dictionary
    num_contigs_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        # Use the len() method to count the number of entries in the list
        num_contigs_dict[file_name] = len(contig_lengths)
    return num_contigs_dict


def find_n50(contig_lengths_dict, genome_length_dict):
    """
    Calculate the N50 for each strain. N50 is defined as the largest contig such that at least half of the total
    genome size is contained in contigs equal to or larger than this contig
    :param contig_lengths_dict: dictionary of strain name: reverse-sorted list of all contig lengths
    :param genome_length_dict: dictionary of strain name: total genome length
    :return: n50_dict: dictionary of strain name: N50
    """
    # Initialise the dictionary
    n50_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        # Initialise a variable to store a running total of contig lengths
        currentlength = 0
        for contig_length in contig_lengths:
            # Increment the current length with the length of the current contig
            currentlength += contig_length
            # If the current length is now greater than the total genome / 2, the current contig length is the N50
            if currentlength >= genome_length_dict[file_name] * 0.5:
                # Populate the dictionary, and break the loop
                n50_dict[file_name] = contig_length
                break
    return n50_dict


def find_n75(contig_lengths_dict, genome_length_dict):
    """
    Calculate the N75 for each strain. N75 is defined as the largest contig such that at least 3/4 of the total
    genome size is contained in contigs equal to or larger than this contig
    :param contig_lengths_dict: dictionary of strain name: reverse-sorted list of all contig lengths
    :param genome_length_dict: dictionary of strain name: total genome length
    :return: n75_dict: dictionary of strain name: N75
    """
    # Initialise the dictionary
    n75_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        currentlength = 0
        for contig_length in contig_lengths:
            currentlength += contig_length
            # If the current length is now greater than the 3/4 of the total genome length, the current contig length
            # is the N75
            if currentlength >= genome_length_dict[file_name] * 0.75:
                n75_dict[file_name] = contig_length
                break
    return n75_dict


def find_n90(contig_lengths_dict, genome_length_dict):
    """
    Calculate the N90 for each strain. N90 is defined as the largest contig such that at least 9/10 of the total
    genome size is contained in contigs equal to or larger than this contig
    :param contig_lengths_dict: dictionary of strain name: reverse-sorted list of all contig lengths
    :param genome_length_dict: dictionary of strain name: total genome length
    :return: n75_dict: dictionary of strain name: N90
    """
    # Initialise the dictionary
    n90_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        currentlength = 0
        for contig_length in contig_lengths:
            currentlength += contig_length
            # If the current length is now greater than the 3/4 of the total genome length, the current contig length
            # is the N75
            if currentlength >= genome_length_dict[file_name] * 0.95:
                n90_dict[file_name] = contig_length
                break
    return n90_dict


def find_l50(contig_lengths_dict, genome_length_dict):
    """
    Calculate the L50 for each strain. L50 is defined as the number of contigs required to achieve the N50
    :param contig_lengths_dict: dictionary of strain name: reverse-sorted list of all contig lengths
    :param genome_length_dict: dictionary of strain name: total genome length
    :return: l50_dict: dictionary of strain name: L50
    """
    # Initialise the dictionary
    l50_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        currentlength = 0
        # Initialise a variable to count how many contigs have been added to the currentlength variable
        currentcontig = 0
        for contig_length in contig_lengths:
            currentlength += contig_length
            # Increment :currentcontig each time a contig is added to the current length
            currentcontig += 1
            # Same logic as with the N50, but the contig number is added instead of the length of the contig
            if currentlength >= genome_length_dict[file_name] * 0.5:
                l50_dict[file_name] = currentcontig
                break
    return l50_dict


def find_l75(contig_lengths_dict, genome_length_dict):
    """
    Calculate the L50 for each strain. L75 is defined as the number of contigs required to achieve the N75
    :param contig_lengths_dict: dictionary of strain name: reverse-sorted list of all contig lengths
    :param genome_length_dict: dictionary of strain name: total genome length
    :return: l50_dict: dictionary of strain name: L75
    """
    # Initialise the dictionary
    l75_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        currentlength = 0
        currentcontig = 0
        for contig_length in contig_lengths:
            currentlength += contig_length
            currentcontig += 1
            # Same logic as with the L75, but the contig number is added instead of the length of the contig
            if currentlength >= genome_length_dict[file_name] * 0.75:
                l75_dict[file_name] = currentcontig
                break
    return l75_dict


def find_l90(contig_lengths_dict, genome_length_dict):
    """
    Calculate the L90 for each strain. L90 is defined as the number of contigs required to achieve the N90
    :param contig_lengths_dict: dictionary of strain name: reverse-sorted list of all contig lengths
    :param genome_length_dict: dictionary of strain name: total genome length
    :return: l90_dict: dictionary of strain name: L90
    """
    # Initialise the dictionary
    l90_dict = dict()
    for file_name, contig_lengths in contig_lengths_dict.items():
        currentlength = 0
        # Initialise a variable to count how many contigs have been added to the currentlength variable
        currentcontig = 0
        for contig_length in contig_lengths:
            currentlength += contig_length
            # Increment :currentcontig each time a contig is added to the current length
            currentcontig += 1
            # Same logic as with the N50, but the contig number is added instead of the length of the contig
            if currentlength >= genome_length_dict[file_name] * 0.9:
                l90_dict[file_name] = currentcontig
                break
    return l90_dict


def predict_orfs(file_dict, num_threads=1):
    """
    Use prodigal to predict the number of open reading frames (ORFs) in each strain
    :param file_dict: dictionary of strain name: /sequencepath/strain_name.extension
    :param num_threads: number of threads to use in the pool of prodigal processes
    :return: orf_file_dict: dictionary of strain name: /sequencepath/prodigal results.sco
    """
    # Initialise the dictionary
    orf_file_dict = dict()
    prodigallist = list()
    for file_name, file_path in file_dict.items():
        # Set the name of the output .sco results file
        results = os.path.splitext(file_path)[0] + '.sco'
        # Create the command for prodigal to execute - use sco output format
        prodigal = ['prodigal', '-i', file_path, '-o', results,  '-f',  'sco']
        # Only run prodigal if the output file doesn't already exist
        if not os.path.isfile(results):
            prodigallist.append(prodigal)
        # Populate the dictionary with the name of the results file
        orf_file_dict[file_name] = results
    # Setup the multiprocessing pool.
    pool = multiprocessing.Pool(processes=num_threads)
    pool.map(run_prodigal, prodigallist)
    pool.close()
    pool.join()
    return orf_file_dict


def run_prodigal(prodigal_command):
    with open(os.devnull, 'w') as f:  # No need to make the use see prodigal output, send it to devnull
        subprocess.call(prodigal_command, stdout=f, stderr=f)


def find_orf_distribution(orf_file_dict):
    """
    Parse the prodigal outputs to determine the frequency of ORF size ranges for each strain
    :param orf_file_dict: dictionary of strain name: /sequencepath/prodigal results.sco
    :return: orf_dist_dict: dictionary of strain name: tuple of ORF size range distribution frequencies
    """
    # Initialise the dictionary
    orf_dist_dict = dict()
    for file_name, orf_report in orf_file_dict.items():
        # Initialise variable to store the frequency of the different ORF size ranges
        total_orfs = 0
        over_3000 = 0
        over_1000 = 0
        over_500 = 0
        other = 0
        # Open the strain-specific report
        with open(orf_report, 'r') as orfreport:
            for line in orfreport:
                # The report has a header section that can be ignored - only parse lines beginning with '>'
                if line.startswith('>'):
                    # Split the line on '_' characters e.g. >1_345_920_- yields contig: >1, start: 345, stop: 920,
                    # direction: -
                    contig, start, stop, direction = line.split('_')
                    # The size of the ORF is the end position minus the start position e.g. 920 - 345 = 575
                    size = int(stop) - int(start)
                    # Increment the total number of ORFs before binning based on ORF size
                    total_orfs += 1
                    # Increment the appropriate integer based on ORF size
                    if size > 3000:
                        over_3000 += 1
                    elif size > 1000:
                        over_1000 += 1
                    elif size > 500:
                        over_500 += 1
                    else:
                        other += 1
        # Populate the dictionary with a tuple of the ORF size range frequencies
        orf_dist_dict[file_name] = (total_orfs,
                                    over_3000,
                                    over_1000,
                                    over_500,
                                    other)
        # Clean-up the prodigal reports
        try:
            os.remove(orf_report)
        except IOError:
            pass
    return orf_dist_dict


def reporter(gc_dict, contig_dist_dict, longest_contig_dict, genome_length_dict, num_contigs_dict, n50_dict, n75_dict,
             n90_dict, l50_dict, l75_dict, l90_dict, orf_dist_dict, genus_dict, sequencepath):
    """
    Create a report of all the extracted features
    :param gc_dict: dictionary of strain name: GC%
    :param contig_dist_dict: dictionary of strain: tuple of contig distribution frequencies
    :param longest_contig_dict: dictionary of strain name: longest contig
    :param genome_length_dict: dictionary of strain name: total genome length
    :param num_contigs_dict: dictionary of strain name: total number of contigs
    :param n50_dict: dictionary of strain name: N50
    :param n75_dict: dictionary of strain name: N75
    :param n90_dict: dictionary of strain name: N90
    :param l50_dict: dictionary of strain name: L50
    :param l75_dict: dictionary of strain name: L75
    :param l90_dict: dictionary of strain name: L90
    :param orf_dist_dict: dictionary of strain name: tuple of ORF length frequencies
    :param genus_dict: dictionary of strain name: genus
    :param sequencepath: path of folder containing FASTA genomes
    """
    # Initialise string with header information
    data = 'SampleName,TotalLength,NumContigs,LongestContig,Contigs>1000000,Contigs>500000,Contigs>100000,' \
           'Contigs>50000,Contigs>10000,Contigs>5000,Contigs<5000,TotalORFs,ORFs>3000,ORFs>1000,ORFs>500,' \
           'ORFs<500,N50,N75,N90,L50,L75,L90,GC%,Genus\n'
    # Create and open the report for writign
    with open(os.path.join(sequencepath, 'extracted_features.csv'), 'w') as feature_report:
        for file_name in sorted(longest_contig_dict):
            # Populate the data string with the appropriate values
            data += '{name},{totlen},{numcontigs},{longestcontig},{over_106},{over_56},{over_105},{over_55},' \
                    '{over_104},{over_54},{under_54},{tORFS},{ORF33},{ORF13},{ORF52}, {ORF11},{n50},{n75},{n90},' \
                    '{l50},{l75},{l90},{gc},{genus}\n'\
                .format(name=file_name,
                        totlen=genome_length_dict[file_name],
                        numcontigs=num_contigs_dict[file_name],
                        longestcontig=longest_contig_dict[file_name],
                        over_106=contig_dist_dict[file_name][0],
                        over_56=contig_dist_dict[file_name][1],
                        over_105=contig_dist_dict[file_name][2],
                        over_55=contig_dist_dict[file_name][3],
                        over_104=contig_dist_dict[file_name][4],
                        over_54=contig_dist_dict[file_name][5],
                        under_54=contig_dist_dict[file_name][6],
                        tORFS=orf_dist_dict[file_name][0],
                        ORF33=orf_dist_dict[file_name][1],
                        ORF13=orf_dist_dict[file_name][2],
                        ORF52=orf_dist_dict[file_name][3],
                        ORF11=orf_dist_dict[file_name][4],
                        n50=n50_dict[file_name],
                        n75=n75_dict[file_name],
                        n90=n90_dict[file_name],
                        l50=l50_dict[file_name],
                        l75=l75_dict[file_name],
                        l90=l90_dict[file_name],
                        gc=gc_dict[file_name],
                        genus=genus_dict[file_name])
        # Write the string to file
        feature_report.write(data)


# Initialise the click decorator
@click.command()
@click.option('-s', '--sequencepath',
              type=click.Path(exists=True),
              required=True,
              help='Path of folder containing multi-FASTA files')
@click.option('-d', '--refseq_database',
              type=click.Path(exists=True),
              required=True,
              help='Path to reduced mash sketch of RefSeq.')
@click.option('-r', '--report',
              is_flag=True,
              default=True,
              help='By default, a report of the extracted features is created. Include this flag if you do not want '
                   'a report created')
def cli(sequencepath, report, refseq_database):
    """
    Pass command line arguments to, and run the feature extraction functions
    """
    main(sequencepath, report, refseq_database, num_threads=multiprocessing.cpu_count())


if __name__ == '__main__':
    cli()
