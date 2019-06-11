#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import MetadataObject, GenObject, make_path, write_to_logfile, \
    run_subprocess
from genemethods.sipprCommon.objectprep import Objectprep
from genemethods.sipprCommon.sippingmethods import Sippr
from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC
from Bio.Seq import Seq
import Bio.Application
from Bio import SeqIO
from argparse import ArgumentParser
from click import progressbar
from subprocess import Popen
from threading import Thread
from subprocess import PIPE
from csv import DictReader
from queue import Queue
import multiprocessing
from glob import glob
import operator
import logging
import time
import os

__author__ = 'adamkoziol'


class SixteenSBait(Sippr):

    def main(self):
        """
        Run the required methods in the appropriate order
        """
        self.targets()
        self.bait(k=49)
        self.reversebait(maskmiddle='t', k=19)
        self.subsample_reads()

    def targets(self):
        """
        Create the GenObject for the analysis type, create the hash file for baiting (if necessary)
        """
        for sample in self.runmetadata:
            setattr(sample, self.analysistype, GenObject())
            if sample.general.bestassemblyfile != 'NA':
                sample[self.analysistype].runanalysis = True
                sample[self.analysistype].targetpath = self.targetpath
                baitpath = os.path.join(self.targetpath, 'bait')
                sample[self.analysistype].baitfile = glob(os.path.join(baitpath, '*.fa'))[0]
                try:
                    sample[self.analysistype].outputdir = os.path.join(sample.run.outputdirectory, self.analysistype)
                except AttributeError:
                    sample[self.analysistype].outputdir = \
                        os.path.join(sample.general.outputdirectory, self.analysistype)
                    sample.run.outputdirectory = sample.general.outputdirectory
                sample[self.analysistype].logout = os.path.join(sample[self.analysistype].outputdir, 'logout.txt')
                sample[self.analysistype].logerr = os.path.join(sample[self.analysistype].outputdir, 'logerr.txt')
                sample[self.analysistype].baitedfastq = os.path.join(sample[self.analysistype].outputdir,
                                                                     '{at}_targetMatches.fastq'
                                                                     .format(at=self.analysistype))
                sample[self.analysistype].complete = False


class SixteenSSipper(Sippr):

    def main(self):
        """
        Run the required methods in the appropriate order
        """
        self.targets()
        self.bait()
        # If desired, use bbduk to bait the target sequences with the previously baited FASTQ files
        if self.revbait:
            self.reversebait()
        # Run the bowtie2 read mapping module
        self.mapping()
        # Use samtools to index the sorted bam file
        self.indexing()
        # Parse the results
        self.parsebam()

    def targets(self):
        """
        Using the data from the BLAST analyses, set the targets folder, and create the 'mapping file'. This is the
        genera-specific FASTA file that will be used for all the reference mapping; it replaces the 'bait file' in the
        code
        """
        logging.info('Performing analysis with {at} targets folder'.format(at=self.analysistype))
        for sample in self.runmetadata:
            if sample.general.bestassemblyfile != 'NA':
                sample[self.analysistype].targetpath = \
                    os.path.join(self.targetpath, 'genera', sample[self.analysistype].genus)
                # There is a relatively strict databasing scheme necessary for the custom targets. Eventually,
                # there will be a helper script to combine individual files into a properly formatted combined file
                try:
                    sample[self.analysistype].mappingfile = glob(os.path.join(sample[self.analysistype].targetpath,
                                                                              '*.fa'))[0]
                # If the fasta file is missing, raise a custom error
                except IndexError as e:
                    # noinspection PyPropertyAccess
                    e.args = ['Cannot find the combined fasta file in {target_path}. '
                              'Please note that the file must have a .fasta extension'
                                  .format(target_path=sample[self.analysistype].targetpath)]
                    if os.path.isdir(sample[self.analysistype].targetpath):
                        raise
                    else:
                        sample.general.bestassemblyfile = 'NA'


class SixteenS(object):

    def runner(self):
        """
        Run the necessary methods in the correct order
        """
        logging.info('Starting {} analysis pipeline'.format(self.analysistype))
        if not self.pipeline:
            # If the metadata has been passed from the method script, self.pipeline must still be false in order to
            # get Sippr() to function correctly, but the metadata shouldn't be recreated
            try:
                _ = vars(self.runmetadata)['samples']
            except AttributeError:
                # Create the objects to be used in the analyses
                objects = Objectprep(self)
                objects.objectprep()
                self.runmetadata = objects.samples

        else:
            for sample in self.runmetadata.samples:
                setattr(sample, self.analysistype, GenObject())
                sample.run.outputdirectory = sample.general.outputdirectory
        self.threads = int(self.cpus / len(self.runmetadata.samples)) \
            if self.cpus / len(self.runmetadata.samples) > 1 \
            else 1
        # Use a custom sippr method to use the full reference database as bait, and run mirabait against the FASTQ
        # reads - do not perform reference mapping yet
        SixteenSBait(self, self.cutoff)
        # Subsample 1000 reads from the FASTQ files
        self.subsample()
        # Convert the subsampled FASTQ files to FASTA format
        self.fasta()
        # Create BLAST databases if required
        self.makeblastdb()
        # Run BLAST analyses of the subsampled FASTA files against the NCBI 16S reference database
        self.blast()
        # Parse the BLAST results
        self.blastparse()
        # Feed the BLAST results into a modified sippr method to perform reference mapping using the calculated
        # genus of the sample as the mapping file
        SixteenSSipper(self, self.cutoff)
        # Create reports
        self.reporter()

    def subsample(self):
        """
        Subsample 1000 reads from the baited files
        """
        # Create the threads for the analysis
        logging.info('Subsampling FASTQ reads')
        for _ in range(self.cpus):
            threads = Thread(target=self.subsamplethreads, args=())
            threads.setDaemon(True)
            threads.start()
        with progressbar(self.runmetadata.samples) as bar:
            for sample in bar:
                if sample.general.bestassemblyfile != 'NA':
                    # Set the name of the subsampled FASTQ file
                    sample[self.analysistype].subsampledfastq = \
                        os.path.splitext(sample[self.analysistype].baitedfastq)[0] + '_subsampled.fastq'
                    # Set the system call
                    sample[self.analysistype].seqtkcall = 'reformat.sh in={baited} out={subsampled} ' \
                                                          'samplereadstarget=1000'\
                        .format(baited=sample[self.analysistype].baitedfastq,
                                subsampled=sample[self.analysistype].subsampledfastq)
                    # Add the sample to the queue
                    self.samplequeue.put(sample)
        self.samplequeue.join()

    def subsamplethreads(self):
        while True:
            sample = self.samplequeue.get()
            # Check to see if the subsampled FASTQ file has already been created
            if not os.path.isfile(sample[self.analysistype].subsampledfastq):
                # Run the system call
                out, err = run_subprocess(sample[self.analysistype].seqtkcall)
                write_to_logfile(sample[self.analysistype].seqtkcall,
                                 sample[self.analysistype].seqtkcall,
                                 self.logfile, sample.general.logout, sample.general.logerr,
                                 sample[self.analysistype].logout, sample[self.analysistype].logerr)
                write_to_logfile(out,
                                 err,
                                 self.logfile, sample.general.logout, sample.general.logerr,
                                 sample[self.analysistype].logout, sample[self.analysistype].logerr)
            self.samplequeue.task_done()

    def fasta(self):
        """
        Convert the subsampled reads to FASTA format using reformat.sh
        """
        logging.info('Converting FASTQ files to FASTA format')
        # Create the threads for the analysis
        for _ in range(self.cpus):
            threads = Thread(target=self.fastathreads, args=())
            threads.setDaemon(True)
            threads.start()
        with progressbar(self.runmetadata.samples) as bar:
            for sample in bar:
                if sample.general.bestassemblyfile != 'NA':
                    # Set the name as the FASTA file - the same as the FASTQ, but with .fa file extension
                    sample[self.analysistype].fasta = \
                        os.path.splitext(sample[self.analysistype].subsampledfastq)[0] + '.fa'
                    # Set the system call
                    sample[self.analysistype].reformatcall = 'reformat.sh in={fastq} out={fasta}'\
                        .format(fastq=sample[self.analysistype].subsampledfastq,
                                fasta=sample[self.analysistype].fasta)
                    # Add the sample to the queue
                    self.fastaqueue.put(sample)
        self.fastaqueue.join()

    def fastathreads(self):
        while True:
            sample = self.fastaqueue.get()
            # Check to see if the FASTA file already exists
            if not os.path.isfile(sample[self.analysistype].fasta):
                # Run the system call
                out, err = run_subprocess(sample[self.analysistype].reformatcall)
                write_to_logfile(sample[self.analysistype].reformatcall,
                                 sample[self.analysistype].reformatcall,
                                 self.logfile, sample.general.logout, sample.general.logerr,
                                 sample[self.analysistype].logout, sample[self.analysistype].logerr)
                write_to_logfile(out,
                                 err,
                                 self.logfile, sample.general.logout, sample.general.logerr,
                                 sample[self.analysistype].logout, sample[self.analysistype].logerr)
            self.fastaqueue.task_done()

    def makeblastdb(self):
        """
        Makes blast database files from targets as necessary
        """
        # Iterate through the samples to set the bait file.
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                # Remove the file extension
                db = os.path.splitext(sample[self.analysistype].baitfile)[0]
                # Add '.nhr' for searching below
                nhr = '{db}.nhr'.format(db=db)
                # Check for already existing database files
                if not os.path.isfile(str(nhr)):
                    # Create the databases
                    command = 'makeblastdb -in {bait} -parse_seqids -max_file_sz 2GB -dbtype nucl -out {out}'\
                        .format(bait=sample[self.analysistype].baitfile,
                                out=db)
                    out, err = run_subprocess(command)
                    write_to_logfile(out=command,
                                     err=command,
                                     logfile=self.logfile,
                                     samplelog=sample.general.logout,
                                     sampleerr=sample.general.logerr,
                                     analysislog=sample[self.analysistype].logout,
                                     analysiserr=sample[self.analysistype].logerr)
                    write_to_logfile(out=out,
                                     err=err,
                                     logfile=self.logfile,
                                     samplelog=sample.general.logout,
                                     sampleerr=sample.general.logerr,
                                     analysislog=sample[self.analysistype].logout,
                                     analysiserr=sample[self.analysistype].logerr)

    def blast(self):
        """
        Run BLAST analyses of the subsampled FASTQ reads against the NCBI 16S reference database
        """
        logging.info('BLASTing FASTA files against {at} database'.format(at=self.analysistype))
        for _ in range(self.cpus):
            threads = Thread(target=self.blastthreads, args=())
            threads.setDaemon(True)
            threads.start()
        with progressbar(self.runmetadata.samples) as bar:
            for sample in bar:
                if sample.general.bestassemblyfile != 'NA':
                    # Set the name of the BLAST report
                    sample[self.analysistype].blastreport = os.path.join(
                        sample[self.analysistype].outputdir,
                        '{sn}_{at}_blastresults.csv'.format(sn=sample.name,
                                                            at=self.analysistype))
                    # Use the NCBI BLASTn command line wrapper module from BioPython to set the parameters of the search
                    blastn = NcbiblastnCommandline(query=sample[self.analysistype].fasta,
                                                   db=os.path.splitext(sample[self.analysistype].baitfile)[0],
                                                   max_target_seqs=1,
                                                   num_threads=self.threads,
                                                   outfmt="'6 qseqid sseqid positive mismatch gaps evalue "
                                                          "bitscore slen length qstart qend qseq sstart send sseq'",
                                                   out=sample[self.analysistype].blastreport)
                    # Add a string of the command to the metadata object
                    sample[self.analysistype].blastcall = str(blastn)
                    # Add the object and the command to the BLAST queue
                    self.blastqueue.put((sample, blastn))
        self.blastqueue.join()

    def blastthreads(self):
        while True:
            sample, blastn = self.blastqueue.get()
            if not os.path.isfile(sample[self.analysistype].blastreport):
                # Ensure that the query file exists; this can happen with very small .fastq files
                if os.path.isfile(sample[self.analysistype].fasta):
                    # Perform the BLAST analysis
                    try:
                        blastn()
                    except Bio.Application.ApplicationError:
                        sample[self.analysistype].blastreport = str()
            self.blastqueue.task_done()

    def blastparse(self):
        """
        Parse the blast results, and store necessary data in dictionaries in sample object
        """
        logging.info('Parsing BLAST results')
        # Load the NCBI 16S reference database as a dictionary
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                # Load the NCBI 16S reference database as a dictionary
                dbrecords = SeqIO.to_dict(SeqIO.parse(sample[self.analysistype].baitfile, 'fasta'))
                # Allow for no BLAST results
                if os.path.isfile(sample[self.analysistype].blastreport):
                    # Initialise a dictionary to store the number of times a genus is the best hit
                    sample[self.analysistype].frequency = dict()
                    # Open the sequence profile file as a dictionary
                    blastdict = DictReader(open(sample[self.analysistype].blastreport),
                                           fieldnames=self.fieldnames, dialect='excel-tab')
                    recorddict = dict()
                    for record in blastdict:
                        # Create the subject id. It will look like this: gi|1018196593|ref|NR_136472.1|
                        subject = record['subject_id']
                        # Extract the genus name. Use the subject id as a key in the dictionary of the reference db.
                        # It will return the full record e.g. gi|1018196593|ref|NR_136472.1| Escherichia marmotae
                        # strain HT073016 16S ribosomal RNA, partial sequence
                        # This full description can be manipulated to extract the genus e.g. Escherichia
                        genus = dbrecords[subject].description.split('|')[-1].split()[0]
                        # Increment the number of times this genus was found, or initialise the dictionary with this
                        # genus the first time it is seen
                        try:
                            sample[self.analysistype].frequency[genus] += 1
                        except KeyError:
                            sample[self.analysistype].frequency[genus] = 1
                        try:
                            recorddict[dbrecords[subject].description] += 1
                        except KeyError:
                            recorddict[dbrecords[subject].description] = 1
                    # Sort the dictionary based on the number of times a genus is seen
                    sample[self.analysistype].sortedgenera = sorted(sample[self.analysistype].frequency.items(),
                                                                    key=operator.itemgetter(1), reverse=True)
                    try:
                        # Extract the top result, and set it as the genus of the sample
                        sample[self.analysistype].genus = sample[self.analysistype].sortedgenera[0][0]
                        # Previous code relies on having the closest refseq genus, so set this as above
                        # sample.general.closestrefseqgenus = sample[self.analysistype].genus
                    except IndexError:
                        # Populate attributes with 'ND'
                        sample[self.analysistype].sortedgenera = 'ND'
                        sample[self.analysistype].genus = 'ND'
                else:
                    # Populate attributes with 'ND'
                    sample[self.analysistype].sortedgenera = 'ND'
                    sample[self.analysistype].genus = 'ND'
            else:
                # Populate attributes with 'ND'
                sample[self.analysistype].sortedgenera = 'ND'
                sample[self.analysistype].genus = 'ND'

    def reporter(self):
        """
        Creates a report of the results
        """
        # Create the path in which the reports are stored
        make_path(self.reportpath)
        logging.info('Creating {at} report'.format(at=self.analysistype))
        # Initialise the header and data strings
        header = 'Strain,Gene,PercentIdentity,Genus,FoldCoverage\n'
        data = ''
        with open(self.sixteens_report, 'w') as report:
            with open(os.path.join(self.reportpath, self.analysistype + '_sequences.fa'), 'w') as sequences:
                for sample in self.runmetadata.samples:
                    # Initialise
                    sample[self.analysistype].sixteens_match = 'ND'
                    sample[self.analysistype].species = 'ND'
                    try:
                        # Select the best hit of all the full-length 16S genes mapped - for 16S use the hit with the
                        # fewest number of SNPs rather than the highest percent identity
                        sample[self.analysistype].besthit = sorted(sample[self.analysistype].resultssnp.items(),
                                                                   key=operator.itemgetter(1))[0][0]
                        # Parse the baited FASTA file to pull out the the description of the hit
                        for record in SeqIO.parse(sample[self.analysistype].baitfile, 'fasta'):
                            # If the best hit e.g. gi|631251361|ref|NR_112558.1| is present in the current record,
                            # gi|631251361|ref|NR_112558.1| Escherichia coli strain JCM 1649 16S ribosomal RNA ...,
                            # extract the match and the species
                            if sample[self.analysistype].besthit in record.id:
                                # Set the best match and species from the records
                                sample[self.analysistype].sixteens_match = record.description.split(' 16S')[0]
                                sample[self.analysistype].species = \
                                    sample[self.analysistype].sixteens_match.split('|')[-1].split()[1]
                        # Add the sample name to the data string
                        data += sample.name + ','
                        # Find the record that matches the best hit, and extract the necessary values to be place in the
                        # data string
                        for name, identity in sample[self.analysistype].results.items():
                            if name == sample[self.analysistype].besthit:
                                data += '{gene},{id},{genus},{depth}\n'.format(gene=sample[self.analysistype]
                                                                               .sixteens_match,
                                                                               id=identity,
                                                                               genus=sample[self.analysistype].genus,
                                                                               depth=sample[self.analysistype]
                                                                               .avgdepth[name])
                                # Create a FASTA-formatted sequence output of the 16S sequence
                                record = SeqRecord(Seq(sample[self.analysistype].sequences[name],
                                                       IUPAC.unambiguous_dna),
                                                   id='{sn}_16S'.format(sn=sample.name),
                                                   description='')
                                SeqIO.write(record, sequences, 'fasta')
                    except (AttributeError, IndexError):
                        data += '{sn}\n'.format(sn=sample.name)
            # Write the results to the report
            report.write(header)
            report.write(data)

    def report_parse(self):
        """
        Rather than re-performing analyses, parse the report, and populate metadata objects
        """
        test = SixteenSBait(self)
        test.targets()
        with open(self.sixteens_report, 'r') as report:
            for line in report:
                try:
                    strain, sixteens, pid, genus, fold_coverage = line.split(',')
                except ValueError:
                    strain = line.rstrip()
                    genus = 'NA'
                    sixteens = str()
                    pid = '0'
                    fold_coverage = '0'
                for sample in self.runmetadata.samples:
                    if sample.name == strain:
                        if not hasattr(sample.general, 'closestrefseqgenus'):
                            sample.general.closestrefseqgenus = genus
                        if not hasattr(sample.general, 'referencegenus'):
                            sample.general.referencegenus = genus
                        sample[self.analysistype].genus = genus
                        sample[self.analysistype].avgdepth = dict()
                        sample[self.analysistype].avgdepth[sixteens] = fold_coverage.rstrip()
                        sample[self.analysistype].sixteens_match = sixteens
                        if genus != 'NA':
                            sample[self.analysistype].results = {sixteens: pid}
                        else:
                            sample[self.analysistype].results = dict()
        sequences = SeqIO.parse(self.sixteens_sequences, 'fasta')
        for record in sequences:
            name = record.id.split('_16S')[0]
            for sample in self.runmetadata.samples:
                if name == sample.name:
                    sample[self.analysistype].sequences = dict()
                    for sixteens in sample[self.analysistype].avgdepth:
                        sample[self.analysistype].sequences[sixteens] = str(record.seq)
        for sample in self.runmetadata.samples:
            if not hasattr(sample[self.analysistype], 'sequences'):
                sample[self.analysistype].sequences = dict()
            if not hasattr(sample[self.analysistype], 'sixteens_match') or not sample[self.analysistype].sixteens_match:
                sample[self.analysistype].sixteens_match = 'ND'

    def __init__(self, args, pipelinecommit, startingtime, scriptpath, analysistype, cutoff):
        """
        :param args: command line arguments
        :param pipelinecommit: pipeline commit or version
        :param startingtime: time the script was started
        :param scriptpath: home path of the script
        :param analysistype: name of the analysis being performed - allows the program to find databases
        :param cutoff: percent identity cutoff for matches
        """
        # Initialise variables
        self.commit = str(pipelinecommit)
        self.starttime = startingtime
        self.homepath = scriptpath
        self.analysistype = analysistype
        # Define variables based on supplied arguments
        try:
            self.path = os.path.join(args.outputpath)
        except AttributeError:
            self.path = os.path.join(args.path)
        assert os.path.isdir(self.path), 'Supplied path is not a valid directory {0!r:s}'.format(self.path)
        try:
            self.sequencepath = os.path.join(args.sequencepath)
        except AttributeError:
            self.sequencepath = self.path
        assert os.path.isdir(self.sequencepath), 'Sequence path  is not a valid directory {0!r:s}' \
            .format(self.sequencepath)
        try:
            self.targetpath = os.path.join(args.referencefilepath, self.analysistype)
        except AttributeError:
            self.targetpath = os.path.join(args.reffilepath, self.analysistype)
        try:
            self.reportpath = args.reportpath
        except AttributeError:
            self.reportpath = os.path.join(self.path, 'reports')
        assert os.path.isdir(self.targetpath), 'Target path is not a valid directory {0!r:s}' \
            .format(self.targetpath)
        try:
            self.bcltofastq = args.bcltofastq
        except AttributeError:
            self.bcltofastq = False
        try:
            self.miseqpath = args.miseqpath
        except AttributeError:
            self.miseqpath = str()
        try:
            self.miseqfolder = args.miseqfolder
        except AttributeError:
            self.miseqfolder = str()
        try:
            self.portallog = args.portallog
        except AttributeError:
            self.portallog = os.path.join(self.path, 'portal.log')
        try:
            self.fastqdestination = args.fastqdestination
        except AttributeError:
            self.fastqdestination = str()
        self.logfile = args.logfile
        try:
            self.forwardlength = args.forwardlength
        except AttributeError:
            self.forwardlength = 'full'
        try:
            self.reverselength = args.reverselength
        except AttributeError:
            self.reverselength = 'full'
        self.numreads = 2 if self.reverselength != 0 else 1
        try:
            self.customsamplesheet = args.customsamplesheet
        except AttributeError:
            self.customsamplesheet = False
        # Set the custom cutoff value
        self.cutoff = cutoff
        # Use the argument for the number of threads to use, or default to the number of cpus in the system
        self.cpus = int(args.cpus if args.cpus else multiprocessing.cpu_count())
        self.threads = int()
        self.runmetadata = args.runmetadata
        self.pipeline = args.pipeline
        try:
            self.copy = args.copy
        except AttributeError:
            self.copy = False
        self.revbait = True
        self.devnull = open(os.path.devnull, 'w')
        self.samplequeue = Queue(maxsize=self.cpus)
        self.fastaqueue = Queue(maxsize=self.cpus)
        self.blastqueue = Queue(maxsize=self.cpus)
        self.baitfile = str()
        self.taxonomy = {'Escherichia': 'coli', 'Listeria': 'monocytogenes', 'Salmonella': 'enterica'}
        # Fields used for custom outfmt 6 BLAST output:
        self.fieldnames = ['query_id', 'subject_id', 'positives', 'mismatches', 'gaps',
                           'evalue', 'bit_score', 'subject_length', 'alignment_length',
                           'query_start', 'query_end', 'query_sequence',
                           'subject_start', 'subject_end', 'subject_sequence']
        #
        self.sixteens_report = os.path.join(self.reportpath, self.analysistype + '.csv')
        self.sixteens_sequences = os.path.join(self.reportpath, self.analysistype + '_sequences.fa')
        if not os.path.isfile(self.sixteens_report):
            # Run the analyses
            self.runner()
        else:
            self.report_parse()


if __name__ == '__main__':
    # Argument parser for user-inputted values, and a nifty help menu

    # Get the current commit of the pipeline from git
    # Extract the path of the current script from the full path + file name
    homepath = os.path.split(os.path.abspath(__file__))[0]
    # Find the commit of the script by running a command to change to the directory containing the script and run
    # a git command to return the short version of the commit hash
    commit = Popen('cd {} && git rev-parse --short HEAD'.format(homepath),
                   shell=True, stdout=PIPE).communicate()[0].rstrip()
    # Parser for arguments
    parser = ArgumentParser(description='Perform modelling of parameters for GeneSipping')
    parser.add_argument('-o', '--outputpath',
                        required=True,
                        help='Path to directory in which report folder is to be created')
    parser.add_argument('-s', '--sequencepath',
                        required=True,
                        help='Path of .fastq(.gz) files to process.')
    parser.add_argument('-r', '--referencefilepath',
                        help='Provide the location of the folder containing the pipeline accessory files (reference '
                             'genomes, MLST data, etc.')
    parser.add_argument('-n', '--cpus',
                        help='Number of threads. Default is the number of cores in the system')
    parser.add_argument('-b', '--bcltofastq',
                        action='store_true',
                        help='Optionally run bcl2fastq on an in-progress Illumina MiSeq run. Must include:'
                             'miseqpath, and miseqfolder arguments, and optionally readlengthforward, '
                             'readlengthreverse, and projectName arguments.')
    parser.add_argument('-m', '--miseqpath',
                        help='Path of the folder containing MiSeq run data folder')
    parser.add_argument('-f', '--miseqfolder',
                        help='Name of the folder containing MiSeq run data')
    parser.add_argument('-d', '--fastqdestination',
                        help='Optional folder path to store .fastq files created using the fastqCreation module. '
                             'Defaults to path/miseqfolder')
    parser.add_argument('-r1', '--forwardlength',
                        default='full',
                        help='Length of forward reads to use. Can specify "full" to take the full length of '
                             'forward reads specified on the SampleSheet')
    parser.add_argument('-r2', '--reverselength',
                        default='full',
                        help='Length of reverse reads to use. Can specify "full" to take the full length of '
                             'reverse reads specified on the SampleSheet')
    parser.add_argument('-c', '--customsamplesheet',
                        help='Path of folder containing a custom sample sheet (still must be named "SampleSheet.csv")')
    parser.add_argument('-P', '--projectName',
                        help='A name for the analyses. If nothing is provided, then the "Sample_Project" field '
                             'in the provided sample sheet will be used. Please note that bcl2fastq creates '
                             'subfolders using the project name, so if multiple names are provided, the results '
                             'will be split as into multiple projects')
    parser.add_argument('-D', '--detailedReports',
                        action='store_true',
                        help='Provide detailed reports with percent identity and depth of coverage values '
                             'rather than just "+" for positive results')
    parser.add_argument('-u', '--cutoff',
                        default=0.8,
                        help='Custom cutoff values')
    parser.add_argument('-C', '--copy',
                        action='store_true',
                        help='Normally, the program will create symbolic links of the files into the sequence path, '
                             'however, the are occasions when it is necessary to copy the files instead')
    # Get the arguments into an object
    arguments = parser.parse_args()
    arguments.pipeline = False
    arguments.runmetadata.samples = MetadataObject()
    arguments.logfile = os.path.join(arguments.path, 'logfile')
    arguments.analysistype = 'sixteens_full'
    # Define the start time
    start = time.time()

    # Run the script
    SixteenS(arguments, commit, start, homepath, arguments.analysistype, arguments.cutoff)

    # Print a bold, green exit statement
    print('\033[92m' + '\033[1m' + "\nElapsed Time: %0.2f seconds" % (time.time() - start) + '\033[0m')
