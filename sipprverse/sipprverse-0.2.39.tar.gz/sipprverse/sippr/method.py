#!/usr/bin/python3
from olctools.accessoryFunctions.accessoryFunctions import MetadataObject, make_path, printtime, SetupLogging
from olctools.accessoryFunctions.metadataprinter import MetadataPrinter
from genemethods.sixteenS.sixteens_full import SixteenS as SixteensFull
from genemethods.sipprverse_reporter.reports import Reports, ReportImage
from genemethods.typingclasses.typingclasses import GDCS
import genemethods.assemblypipeline.quality as quality
from genemethods.sipprCommon.create_sample_sheet import SampleSheet
from genemethods.sipprCommon.objectprep import Objectprep
from genemethods.genesippr.genesippr import GeneSippr
import genemethods.MASHsippr.mash as mash
from argparse import ArgumentParser
import multiprocessing
from time import sleep
from glob import glob
import subprocess
import logging
import time
import os
__author__ = 'adamkoziol'


class Method(object):

    def main(self):
        """
        Run the analyses using the inputted values for forward and reverse read length. However, if not all strains
        pass the quality thresholds, continue to periodically run the analyses on these incomplete strains until either
        all strains are complete, or the sequencing run is finished
        """
        logging.info('Starting {} analysis pipeline'.format(self.analysistype))
        self.createobjects()
        # Run the genesipping analyses
        self.methods()
        # Determine if the analyses are complete
        self.complete()
        self.additionalsipping()
        # Update the report object
        self.reports = Reports(self)
        # Once all the analyses are complete, create reports for each sample
        Reports.methodreporter(self.reports)
        # Print the metadata
        printer = MetadataPrinter(self)
        printer.printmetadata()

    def createobjects(self):
        # Set the name of the folders in which to store the current analysis based on the length of reads
        reads = '{}_{}'.format(self.forwardlength, self.reverselength)
        # Update the necessary variables to allow for the custom naming of folders based on the length forward and
        # reverse reads used to create the .fastq files
        self.fastqdestination = os.path.join(self.path, self.miseqfolder, reads)
        self.sequencepath = os.path.join(self.seqpath, reads)
        self.reportpath = os.path.join(self.reportpath, reads)
        self.samplesheetpath = os.path.join(self.path, 'SampleSheets', reads)
        # Create the objects to be used in the analyses
        objects = Objectprep(self)
        objects.objectprep()
        # Set the metadata
        self.runmetadata = objects.samples
        self.threads = int(self.cpus / len(self.runmetadata.samples)) if self.cpus / len(self.runmetadata.samples) > 1 \
            else 1
        # Pull the full length of the forward and reverse reads, as well as the indices
        self.forward = int(objects.forward)
        self.reverse = int(objects.reverse)
        self.index = objects.index
        self.index_length = objects.index_length
        self.forwardlength = int(objects.forwardlength)
        self.reverselength = int(objects.reverselength)
        # Store data from the sample sheet header and body
        self.header = objects.header
        self.rundata = objects.run
        # Set the list of all the sample names in the analysis
        self.samples = [sample.name for sample in self.runmetadata.samples]
        # If a custom sample sheet isn't specified, create one with all the samples
        if not self.customsamplesheet:
            for sample in self.runmetadata.samples:
                self.incomplete.append(sample.name)
            # Create the sample sheet
            samplesheet = SampleSheet(self)
            samplesheet.samplesheet()
        # Set self.bcltofastq to False, as the call to Sippr() in self.methods will attempt to create the files again
        self.bcltofastq = False

    def additionalsipping(self):
        # If the analyses are not complete, continue to run the analyses until either all the strains pass the quality
        # thresholds, or until the sequencing run is complete
        while not self.analysescomplete:
            # Calculate the total number of reads needed for the run (forward + index1 + index2 + reverse). As the index
            # is the modified index used for the bcl2fastq its format is something like: AGGCAGAA-GCGTAAGA. Count only
            # the alphanumeric characters.
            self.sum = self.forwardlength + self.index_length + self.reverselength
            # Ensuring that the forward length is set to full - for testing only. In a real analysis, the forward length
            # has to be full due to the way that the sequencing is performed
            self.forwardlength = 'full'
            # Determine the number of completed cycles
            cycles = glob(
                os.path.join(self.miseqpath, self.miseqfolder, 'Data', 'Intensities', 'BaseCalls', 'L001', 'C*'))
            # If the run is complete, process the data one final time
            if len(cycles) == self.sum:
                printtime(
                    'Certain strains did not pass the quality thresholds. Final attempt of the pipeline. Using '
                    'the full reads'.format(self.forwardlength, self.reverselength, ),
                    self.starttime, output=self.portallog)
                # Set the boolean for the final iteration of the pipeline to true - this will allow all samples - even
                # ones considered incomplete to be entered into the final reports
                self.final = True
                # If the run is finished, then the reverse reads will be fully sequenced
                self.reverselength = 'full'
                # Set the name of the folders in which to store the current analysis based on the length of reads
                reads = '{}_{}'.format(self.forwardlength, self.reverselength)
                # Update the necessary variables to allow for the custom naming of folders based on the length forward
                # and reverse reads used to create the .fastq files
                self.fastqdestination = os.path.join(self.path, self.miseqfolder, reads)
                make_path(self.fastqdestination)
                self.sequencepath = os.path.join(self.seqpath, reads)
                make_path(self.sequencepath)
                self.reportpath = os.path.join(self.path, 'reports', reads)
                make_path(self.reportpath)
                self.samplesheetpath = os.path.join(self.path, 'SampleSheets', reads)
                # Create the sample sheet with only the samples that still need to be processed
                samplesheet = SampleSheet(self)
                samplesheet.samplesheet()
                # Reset booleans
                self.analysescomplete = True
                self.bcltofastq = True
                # Create the objects to be used in the final analysis
                objects = Objectprep(self)
                objects.objectprep()
                # Set the metadata
                self.runmetadata = objects.samples
                self.bcltofastq = False
                # Run the analyses
                self.methods()
                self.complete()
            # If the sequencing run is not yet complete, continue to pull data from the MiSeq as it is created
            else:
                # Determine the length of reverse reads that can be used
                self.reverselength = str(len(cycles) - self.forwardlength - self.index_length)
                printtime(
                    'Certain strains did not pass the quality thresholds. Attempting the pipeline with the following '
                    'read lengths: forward {}, reverse {}'.format(self.forwardlength, self.reverselength),
                    self.starttime,
                    output=self.portallog)
                # Set the name of the folders in which to store the current analysis based on the length of reads
                reads = '{}_{}'.format(self.forwardlength, self.reverselength)
                # Update the necessary variables to allow for the custom naming of folders based on the length forward
                # and reverse reads used to create the .fastq files
                self.fastqdestination = os.path.join(self.path, self.miseqfolder, reads)
                make_path(self.fastqdestination)
                self.sequencepath = os.path.join(self.seqpath, reads)
                make_path(self.sequencepath)
                self.reportpath = os.path.join(self.path, 'reports', reads)
                make_path(self.reportpath)
                self.samplesheetpath = os.path.join(self.path, 'SampleSheets', reads)
                samplesheet = SampleSheet(self)
                samplesheet.samplesheet()
                self.bcltofastq = True
                # Create the objects to be used in the analyses
                objects = Objectprep(self)
                objects.objectprep()
                # Set the metadata
                self.runmetadata = objects.samples
                self.methods()
                self.complete()
                # Allow the sequencer to complete approximately five cycles (~300 seconds per cycle) plus
                # however long it takes to run the analyses before trying again
                sleep(1500)

    def methods(self):
        """
        Run the typing methods
        """
        self.contamination_detection()
        ReportImage(self, 'confindr')
        self.run_genesippr()
        ReportImage(self, 'genesippr')
        self.run_sixteens()
        self.run_mash()
        self.run_gdcs()
        ReportImage(self, 'gdcs')

    def contamination_detection(self):
        """
        Calculate the levels of contamination in the reads
        """
        self.qualityobject = quality.Quality(self)
        self.qualityobject.contamination_finder(input_path=self.sequencepath,
                                                report_path=self.reportpath)

    def run_genesippr(self):
        """
        Run the genesippr analyses
        """
        GeneSippr(args=self,
                  pipelinecommit=self.commit,
                  startingtime=self.starttime,
                  scriptpath=self.homepath,
                  analysistype='genesippr',
                  cutoff=0.95,
                  pipeline=False,
                  revbait=False)

    def run_sixteens(self):
        """
        Run the 16S analyses using the filtered database
        """
        SixteensFull(args=self,
                     pipelinecommit=self.commit,
                     startingtime=self.starttime,
                     scriptpath=self.homepath,
                     analysistype='sixteens_full',
                     cutoff=0.985)

    def run_mash(self):
        """
        Run MASH to determine the closest refseq genomes
        """
        self.pipeline = True
        mash.Mash(inputobject=self,
                  analysistype='mash')

    def run_gdcs(self):
        """
        Run the GDCS analysis
        """
        GDCS(inputobject=self)

    def complete(self):
        """
        Determine if the analyses of the strains are complete e.g. there are no missing GDCS genes, and the 
        sample.general.bestassemblyfile != 'NA'
        """
        # Boolean to store the completeness of the analyses
        allcomplete = True
        # Clear the list of samples that still require more sequence data
        self.incomplete = list()
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                try:
                    # If the sample has been tagged as incomplete, only add it to the complete metadata list if the
                    # pipeline is on its final iteration
                    if sample.general.incomplete:
                        if self.final:
                            self.completemetadata.append(sample)
                        else:
                            sample.general.complete = False
                            allcomplete = False
                            self.incomplete.append(sample.name)
                except AttributeError:
                    sample.general.complete = True
                    self.completemetadata.append(sample)
            else:
                if self.final:
                    self.completemetadata.append(sample)
                else:
                    sample.general.complete = False
                    allcomplete = False
                    self.incomplete.append(sample.name)
        # If all the samples are complete, set the global variable for run completeness to True
        if allcomplete:
            self.analysescomplete = True

    def __init__(self, args, pipelinecommit, startingtime, scriptpath):
        """
        :param args: command line arguments
        :param pipelinecommit: pipeline commit or version
        :param startingtime: time the script was started
        :param scriptpath: home path of the script
        """
        # Initialise variables
        self.commit = str(pipelinecommit)
        self.starttime = startingtime
        self.homepath = scriptpath
        # Define variables based on supplied arguments
        if args.outputpath.startswith('~'):
            self.path = os.path.expanduser(args.outputpath)
        else:
            self.path = os.path.abspath(os.path.join(args.outputpath))
        make_path(self.path)
        assert os.path.isdir(self.path), 'Supplied path is not a valid directory {0!r:s}'.format(self.path)
        try:
            self.portallog = args.portallog
        except AttributeError:
            self.portallog = os.path.join(self.path, 'portal.log')
        try:
            os.remove(self.portallog)
        except FileNotFoundError:
            pass
        self.sequencepath = os.path.join(self.path, 'sequences')
        self.seqpath = self.sequencepath
        if args.referencefilepath.startswith('~'):
            self.targetpath = os.path.expanduser(args.referencefilepath)
        else:
            self.targetpath = os.path.abspath(os.path.join(args.referencefilepath))
        # ref file path is used to work with sub module code with a different naming scheme
        self.reffilepath = self.targetpath
        self.reportpath = os.path.join(self.path, 'reports')
        make_path(self.reportpath)
        assert os.path.isdir(self.targetpath), 'Target path is not a valid directory {0!r:s}' \
            .format(self.targetpath)
        self.bcltofastq = True
        if args.miseqpath.startswith('~'):
            self.miseqpath = os.path.expanduser(args.miseqpath)
        else:
            self.miseqpath = os.path.abspath(args.miseqpath)
        self.miseqfolder = args.miseqfolder
        self.fastqdestination = str()
        self.forwardlength = args.readlengthforward
        self.reverselength = args.readlengthreverse
        self.numreads = 2 if self.reverselength != 0 else 1
        try:
            if args.customsamplesheet.startswith('~'):
                self.customsamplesheet = os.path.expanduser(args.customsamplesheet)
            else:
                self.customsamplesheet = os.path.abspath(os.path.join(args.customsamplesheet))
        except AttributeError:
            self.customsamplesheet = None
        # Set the custom cutoff value
        self.cutoff = float()
        # Use the argument for the number of threads to use, or default to the number of cpus in the system
        try:
            self.cpus = int(args.numthreads)
        except (AttributeError, TypeError):
            self.cpus = multiprocessing.cpu_count()
        self.threads = int()
        self.runmetadata = MetadataObject()
        self.qualityobject = MetadataObject()
        self.taxonomy = {'Escherichia': 'coli', 'Listeria': 'monocytogenes', 'Salmonella': 'enterica'}
        self.analysistype = 'GeneSipprMethod'
        self.copy = args.copy
        try:
            self.debug = args.debug
        except AttributeError:
            self.debug = False
        self.demultiplex = args.demultiplex
        self.pipeline = False
        self.forward = str()
        self.reverse = str()
        self.index = str()
        self.index_length = int()
        self.header = dict()
        self.rundata = dict()
        self.completed = list()
        self.incomplete = list()
        self.analysescomplete = False
        self.final = False
        self.sum = int()
        self.completemetadata = list()
        self.samplesheetpath = str()
        self.samples = list()
        self.logfile = os.path.join(self.path, 'log')
        self.reports = str()


if __name__ == '__main__':
    # Get the current commit of the pipeline from git
    # Extract the path of the current script from the full path + file name
    homepath = os.path.split(os.path.abspath(__file__))[0]
    # Find the commit of the script by running a command to change to the directory containing the script and run
    # a git command to return the short version of the commit hash
    commit = subprocess.Popen('cd {} && git rev-parse --short HEAD'.format(homepath),
                              shell=True, stdout=subprocess.PIPE).communicate()[0].rstrip()
    # Parser for arguments
    parser = ArgumentParser(description='Perform FASTQ creation and typing')
    parser.add_argument('-o', '--outputpath',
                        required=True,
                        help='Path to directory in which report folder is to be created')
    parser.add_argument('-r', '--referencefilepath',
                        required=True,
                        help='Provide the location of the folder containing the target files')
    parser.add_argument('-m', '--miseqpath',
                        required=True,
                        help='Path of the folder containing MiSeq run data folder')
    parser.add_argument('-f', '--miseqfolder',
                        required=True,
                        help='Name of the folder containing MiSeq run data')
    parser.add_argument('-n', '--numthreads',
                        help='Number of threads. Default is the number of cores in the system')
    parser.add_argument('-r1', '--readlengthforward',
                        default='full',
                        help='Length of forward reads to use. Can specify "full" to take the full length of '
                             'forward reads specified on the SampleSheet. Default value is "full"')
    parser.add_argument('-r2', '--readlengthreverse',
                        default='full',
                        help='Length of reverse reads to use. Can specify "full" to take the full length of '
                             'reverse reads specified on the SampleSheet. Default value is "full"')
    parser.add_argument('-c', '--customsamplesheet',
                        help='Path of folder containing a custom sample sheet (still must be named "SampleSheet.csv")')
    parser.add_argument('-P', '--projectName',
                        help='A name for the analyses. If nothing is provided, then the "Sample_Project" field '
                             'in the provided sample sheet will be used. Please note that bcl2fastq creates '
                             'subfolders using the project name, so if multiple names are provided, the results '
                             'will be split into multiple projects')
    parser.add_argument('-C', '--copy',
                        action='store_true',
                        default=True,
                        help='Normally, the program will create symbolic links of the files into the sequence path, '
                             'however, the are occasions when it is necessary to copy the files instead')
    parser.add_argument('-D', '--demultiplex',
                        action='store_false',
                        default=True,
                        help='Optionally disable demultiplexing by bcl2fastq if there is a single sample in the run')
    # Get the arguments into an object
    arguments = parser.parse_args()
    arguments.portallog = os.path.join(arguments.outputpath, 'portal.log')
    # Define the start time
    start = time.time()
    SetupLogging()
    # Run the script
    method = Method(arguments, commit, start, homepath)
    method.main()

    # Print a bold, green exit statement
    printtime('Analyses complete', start, option='\033[1;92m', output=arguments.portallog)
