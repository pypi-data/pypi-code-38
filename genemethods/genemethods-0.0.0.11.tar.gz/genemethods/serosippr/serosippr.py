#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import MetadataObject, make_path, SetupLogging
import olctools.accessoryFunctions.metadataprinter as metadataprinter
from genemethods.sipprCommon.objectprep import Objectprep
from genemethods.sipprCommon.sippingmethods import Sippr
import operator
import subprocess
import logging
import time
import os
__author__ = 'adamkoziol'


class SeroSippr(object):

    def runner(self):
        """
        Run the necessary methods in the correct order
        """
        logging.info('Starting {} analysis pipeline'.format(self.analysistype))
        # Run the analyses
        Sippr(self, self.cutoff)
        self.serotype_escherichia()
        self.serotype_salmonella()
        # Create the reports
        self.reporter()
        # Print the metadata
        metadataprinter.MetadataPrinter(self)

    def reporter(self):
        """
        Creates a report of the results
        """
        logging.info('Creating {} report'.format(self.analysistype))
        # Create the path in which the reports are stored
        make_path(self.reportpath)
        header = 'Strain,Serotype\n'
        data = ''
        with open(os.path.join(self.reportpath, '{}.csv'.format(self.analysistype)), 'w') as report:
            for sample in self.runmetadata.samples:
                if sample.general.bestassemblyfile != 'NA':
                    data += sample.name + ','
                    if sample[self.analysistype].results:
                        # Set the O-type as either the appropriate attribute, or O-untypable
                        if ';'.join(sample.serosippr.o_set) == '-':
                            otype = 'O-untypeable'
                        else:
                            otype = '{oset} ({opid})'.format(oset=';'.join(sample.serosippr.o_set),
                                                             opid=sample.serosippr.best_o_pid)
                        # Same as above, but for the H-type
                        if ';'.join(sample.serosippr.h_set) == '-':
                            htype = 'H-untypeable'

                        else:
                            htype = '{hset} ({hpid})'.format(hset=';'.join(sample.serosippr.h_set),
                                                             hpid=sample.serosippr.best_h_pid)
                        serotype = '{otype}:{htype}'.format(otype=otype,
                                                            htype=htype)
                        # Populate the data string
                        data += serotype if serotype != 'O-untypeable:H-untypeable' else 'ND'
                        data += '\n'
                    else:
                        data += '\n'
            report.write(header)
            report.write(data)

    def serotype_escherichia(self):
        """
        Create attributes storing the best results for the O and H types
        """
        for sample in self.runmetadata.samples:
            # Initialise negative results to be overwritten when necessary
            sample[self.analysistype].best_o_pid = '-'
            sample[self.analysistype].o_genes = ['-']
            sample[self.analysistype].o_set = ['-']
            sample[self.analysistype].best_h_pid = '-'
            sample[self.analysistype].h_genes = ['-']
            sample[self.analysistype].h_set = ['-']
            if sample.general.bestassemblyfile != 'NA':
                if sample.general.closestrefseqgenus == 'Escherichia':
                    o = dict()
                    h = dict()
                    for result, percentid in sample[self.analysistype].results.items():
                        if 'O' in result.split('_')[-1]:
                            o.update({result: float(percentid)})
                        if 'H' in result.split('_')[-1]:
                            h.update({result: float(percentid)})
                    # O
                    try:
                        sorted_o = sorted(o.items(), key=operator.itemgetter(1), reverse=True)
                        sample[self.analysistype].best_o_pid = str(sorted_o[0][1])

                        sample[self.analysistype].o_genes = [gene for gene, pid in o.items()
                                                             if str(pid) == sample[self.analysistype].best_o_pid]
                        sample[self.analysistype].o_set = \
                            list(set(gene.split('_')[-1] for gene in sample[self.analysistype].o_genes))
                    except (KeyError, IndexError):
                        pass
                    # H
                    try:
                        sorted_h = sorted(h.items(), key=operator.itemgetter(1), reverse=True)
                        sample[self.analysistype].best_h_pid = str(sorted_h[0][1])
                        sample[self.analysistype].h_genes = [gene for gene, pid in h.items()
                                                             if str(pid) == sample[self.analysistype].best_h_pid]
                        sample[self.analysistype].h_set = \
                            list(set(gene.split('_')[-1] for gene in sample[self.analysistype].h_genes))
                    except (KeyError, IndexError):
                        pass

    def serotype_salmonella(self):
        """

        """
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                if sample.general.closestrefseqgenus == 'Salmonella':
                    pass
                    # print('Salmonella', sample.name, sample[self.analysistype].datastore)

    def __init__(self, args, pipelinecommit, startingtime, scriptpath, analysistype, cutoff, pipeline):
        """
        :param args: command line arguments
        :param pipelinecommit: pipeline commit or version
        :param startingtime: time the script was started
        :param scriptpath: home path of the script
        :param analysistype: name of the analysis being performed - allows the program to find databases
        :param cutoff: percent identity cutoff for matches
        :param pipeline: boolean of whether this script needs to run as part of a particular assembly pipeline
        """
        import multiprocessing
        # Initialise variables
        self.commit = str(pipelinecommit)
        self.starttime = startingtime
        self.homepath = scriptpath
        # Define variables based on supplied arguments
        self.path = os.path.join(args.path, '')
        assert os.path.isdir(self.path), u'Supplied path is not a valid directory {0!r:s}'.format(self.path)
        try:
            self.sequencepath = os.path.join(args.sequencepath, '')
        except AttributeError:
            self.sequencepath = self.path
        assert os.path.isdir(self.sequencepath), u'Sequence path  is not a valid directory {0!r:s}' \
            .format(self.sequencepath)
        try:
            self.targetpath = os.path.join(args.reffilepath)
        except AttributeError:
            self.targetpath = os.path.join(args.targetpath)
        self.reportpath = os.path.join(self.path, 'reports')
        assert os.path.isdir(self.targetpath), u'Target path is not a valid directory {0!r:s}' \
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
            self.fastqdestination = args.fastqdestination
        except AttributeError:
            self.fastqdestination = str()
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
            self.customsamplesheet = str()
        self.taxonomy = {'Escherichia': 'coli', 'Listeria': 'monocytogenes', 'Salmonella': 'enterica'}
        self.logfile = args.logfile
        # Set the custom cutoff value
        self.cutoff = float(cutoff)
        try:
            self.averagedepth = int(args.averagedepth)
        except AttributeError:
            self.averagedepth = 10
        try:
            self.copy = args.copy
        except AttributeError:
            self.copy = False
        self.pipeline = pipeline
        if not self.pipeline:
            self.runmetadata = MetadataObject()
            # Create the objects to be used in the analyses
            objects = Objectprep(self)
            objects.objectprep()
            self.runmetadata = objects.samples
        else:
            self.runmetadata = args.runmetadata
        # Use the argument for the number of threads to use, or default to the number of cpus in the system
        try:
            self.cpus = int(args.cpus)
        except AttributeError:
            self.cpus = multiprocessing.cpu_count()
        try:
            self.threads = int(self.cpus / len(self.runmetadata.samples)) if self.cpus / len(
                self.runmetadata.samples) > 1 else 1
        except TypeError:
            self.threads = self.cpus
        self.analysistype = analysistype
        self.threads = int(self.cpus / len(self.runmetadata.samples)) if self.cpus / len(self.runmetadata.samples) > 1 \
            else 1
        # Run the analyses
        self.runner()


if __name__ == '__main__':
    # Argument parser for user-inputted values, and a nifty help menu
    from argparse import ArgumentParser
    # Get the current commit of the pipeline from git
    # Extract the path of the current script from the full path + file name
    homepath = os.path.split(os.path.abspath(__file__))[0]
    # Find the commit of the script by running a command to change to the directory containing the script and run
    # a git command to return the short version of the commit hash
    commit = subprocess.Popen('cd {} && git rev-parse --short HEAD'.format(homepath),
                              shell=True, stdout=subprocess.PIPE).communicate()[0].rstrip()
    # Parser for arguments
    parser = ArgumentParser(description='Perform modelling of parameters for SeroSipping')
    parser.add_argument('path',
                        help='Specify input directory')
    parser.add_argument('-s', '--sequencepath',
                        required=True,
                        help='Path of .fastq(.gz) files to process.')
    parser.add_argument('-t', '--targetpath',
                        required=True,
                        help='Path of target files to process.')
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
    SetupLogging()
    # Get the arguments into an object
    arguments = parser.parse_args()
    arguments.pipeline = False
    arguments.logfile = os.path.join(arguments.path, 'logfile')
    # Define the start time
    start = time.time()

    # Run the script
    SeroSippr(arguments, commit, start, homepath, 'serosippr', arguments.cutoff, arguments.pipeline)

    # Print a bold, green exit statement
    print('\033[92m' + '\033[1m' + "\nElapsed Time: %0.2f seconds" % (time.time() - start) + '\033[0m')
