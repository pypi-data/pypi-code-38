#!/usr/bin/python3
from olctools.accessoryFunctions.accessoryFunctions import make_path, MetadataObject, SetupLogging
from olctools.accessoryFunctions.metadataprinter import MetadataPrinter
from genemethods.typingclasses.typingclasses import Resistance, Virulence
from genemethods.sixteenS.sixteens_full import SixteenS as SixteensFull
from genemethods.MLSTsippr.mlst import GeneSippr as MLSTSippr
from genemethods.customsippr.customsippr import CustomGenes
from genemethods.pointsippr.pointsippr import PointSippr
from genemethods.sipprverse_reporter.reports import Reports
from genemethods.sipprCommon.objectprep import Objectprep
from genemethods.sipprCommon.sippingmethods import Sippr
from genemethods.serosippr.serosippr import SeroSippr
import genemethods.MASHsippr.mash as mash
from argparse import ArgumentParser
import multiprocessing
import subprocess
import logging
import time
import os

__author__ = 'adamkoziol'


class Sipprverse(object):

    def main(self):
        """
        Run the necessary methods in the correct order
        """
        logging.info('Starting {at} analysis pipeline'.format(at=self.analysistype))
        # Create the objects to be used in the analyses
        objects = Objectprep(self)
        objects.objectprep()
        self.runmetadata = objects.samples
        self.threads = int(self.cpus / len(self.runmetadata.samples)) if self.cpus / len(self.runmetadata.samples) > 1 \
            else 1
        if self.genesippr:
            # Run the genesippr analyses
            self.analysistype = 'genesippr'
            self.targetpath = os.path.join(self.reffilepath, self.analysistype)
            Sippr(inputobject=self,
                  cutoff=0.90,
                  averagedepth=self.averagedepth)
            # Create the reports
            self.reports = Reports(self)
            Reports.reporter(self.reports)
        if self.sixteens:
            # Run the 16S analyses
            SixteensFull(args=self,
                         pipelinecommit=self.commit,
                         startingtime=self.starttime,
                         scriptpath=self.homepath,
                         analysistype='sixteens_full',
                         cutoff=0.985)
        if self.closestreference:
            self.pipeline = True
            mash.Mash(inputobject=self,
                      analysistype='mash')
        if self.rmlst:
            rmlst = MLSTSippr(args=self,
                              pipelinecommit=self.commit,
                              startingtime=self.starttime,
                              scriptpath=self.homepath,
                              analysistype='rMLST',
                              cutoff=1.0,
                              pipeline=True)
            rmlst.runner()
        if self.resistance:
            # ResFinding
            res = Resistance(args=self,
                             pipelinecommit=self.commit,
                             startingtime=self.starttime,
                             scriptpath=self.homepath,
                             analysistype='resfinder',
                             cutoff=0.7,
                             pipeline=False,
                             revbait=True)
            res.main()
        if self.virulence:
            self.genus_specific()
            Virulence(args=self,
                      pipelinecommit=self.commit,
                      startingtime=self.starttime,
                      scriptpath=self.homepath,
                      analysistype='virulence',
                      cutoff=0.95,
                      pipeline=False,
                      revbait=True)
        if self.gdcs:
            self.genus_specific()
            # Run the GDCS analysis
            self.analysistype = 'GDCS'
            self.targetpath = os.path.join(self.reffilepath, self.analysistype)
            Sippr(inputobject=self,
                  cutoff=0.95,
                  k=self.gdcs_kmer_size,
                  averagedepth=self.averagedepth,)
            # Create the reports
            self.reports = Reports(self)
            Reports.gdcsreporter(self.reports)
        if self.mlst:
            self.genus_specific()
            mlst = MLSTSippr(args=self,
                             pipelinecommit=self.commit,
                             startingtime=self.starttime,
                             scriptpath=self.homepath,
                             analysistype='MLST',
                             cutoff=1.0,
                             pipeline=True)
            mlst.runner()
        # Serotyping
        if self.serotype:
            self.genus_specific()
            SeroSippr(args=self,
                      pipelinecommit=self.commit,
                      startingtime=self.starttime,
                      scriptpath=self.homepath,
                      analysistype='serosippr',
                      cutoff=0.90,
                      pipeline=True)
        # Point mutation detection
        if self.pointfinder:
            self.genus_specific()
            PointSippr(args=self,
                       pipelinecommit=self.commit,
                       startingtime=self.starttime,
                       scriptpath=self.homepath,
                       analysistype='pointfinder',
                       cutoff=0.85,
                       pipeline=True,
                       revbait=True)
        if self.user_genes:
            custom = CustomGenes(args=self,
                                 cutoff=self.cutoff,
                                 kmer_size=self.kmer_size,
                                 allow_soft_clips=self.allow_soft_clips)
            custom.main()
        # Print the metadata
        MetadataPrinter(self)

    def genus_specific(self):
        """
        For genus-specific targets, MLST and serotyping, determine if the closest refseq genus is known - i.e. if 16S
        analyses have been performed. Perform the analyses if required
        """
        # Initialise a variable to store whether the necessary analyses have already been performed
        closestrefseqgenus = False
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                try:
                    closestrefseqgenus = sample.general.closestrefseqgenus
                except AttributeError:
                    pass
        # Perform the 16S analyses as required
        if not closestrefseqgenus:
            logging.info('Must perform MASH analyses to determine genera of samples')
            self.pipeline = True
            # Run the analyses
            mash.Mash(self, 'mash')

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
        self.args = args
        # Define variables based on supplied arguments
        self.path = os.path.abspath(os.path.join(args.outputpath))
        assert os.path.isdir(self.path), u'Supplied path is not a valid directory {0!r:s}'.format(self.path)
        self.sequencepath = os.path.abspath(os.path.join(args.sequencepath))
        self.seqpath = self.sequencepath
        self.targetpath = os.path.abspath(os.path.join(args.referencefilepath))
        # ref file path is used to work with submodule code with a different naming scheme
        self.reffilepath = self.targetpath
        self.reportpath = os.path.join(self.path, 'reports')
        make_path(self.reportpath)
        assert os.path.isdir(self.targetpath), 'Target path is not a valid directory {0!r:s}' \
            .format(self.targetpath)
        # Set the custom cutoff value
        self.cutoff = args.customcutoffs
        # Use the argument for the number of threads to use, or default to the number of cpus in the system
        self.cpus = int(args.numthreads)
        self.closestreference = args.closestreference
        self.gdcs = args.gdcs
        self.genesippr = args.genesippr
        self.mlst = args.mlst
        self.pointfinder = args.pointfinder
        self.resistance = args.resistance
        self.rmlst = args.rmlst
        self.serotype = args.serotype
        self.sixteens = args.sixteens
        self.virulence = args.virulence
        self.averagedepth = args.averagedepth
        self.gdcs_kmer_size = args.gdcs_kmer_size
        self.kmer_size = args.kmer_size
        self.allow_soft_clips = args.allow_soft_clips
        try:
            self.user_genes = os.path.join(args.user_genes)
            assert os.path.isfile(self.user_genes), 'Cannot find user-supplied target file: {targets}. Please ' \
                                                    'double-check name and path of file'\
                .format(targets=self.user_genes)
        except TypeError:
            self.user_genes = args.user_genes
        # Set all the analyses to True if the full_suite option was selected
        if args.full_suite:
            self.closestreference = True
            self.gdcs = True
            self.genesippr = True
            self.mlst = True
            self.pointfinder = True
            self.resistance = True
            self.rmlst = True
            self.serotype = True
            self.sixteens = True
            self.virulence = True
        self.reports = str()
        self.threads = int()
        self.runmetadata = MetadataObject()
        self.taxonomy = {'Escherichia': 'coli', 'Listeria': 'monocytogenes', 'Salmonella': 'enterica'}
        self.analysistype = 'GeneSippr'
        self.pipeline = False
        self.logfile = os.path.join(self.path, 'log')


if __name__ == '__main__':
    # Get the current commit of the pipeline from git
    # Extract the path of the current script from the full path + file name
    homepath = os.path.split(os.path.abspath(__file__))[0]
    # Find the commit of the script by running a command to change to the directory containing the script and run
    # a git command to return the short version of the commit hash
    commit = subprocess.Popen('cd {} && git rev-parse --short HEAD'.format(homepath),
                              shell=True, stdout=subprocess.PIPE).communicate()[0].rstrip()
    # Parser for arguments
    parser = ArgumentParser(description='Performs GeneSipping on folder of FASTQ files')
    parser.add_argument('-o', '--outputpath',
                        required=True,
                        help='Path to directory in which report folder is to be created')
    parser.add_argument('-s', '--sequencepath',
                        required=True,
                        help='Path of .fastq(.gz) files to process.')
    parser.add_argument('-r', '--referencefilepath',
                        required=True,
                        help='Provide the location of the folder containing reference database')
    parser.add_argument('-a', '--averagedepth',
                        default=5,
                        type=int,
                        help='Cutoff value for mapping depth to use when parsing BAM files.')
    parser.add_argument('-n', '--numthreads',
                        default=multiprocessing.cpu_count(),
                        help='Number of threads. Default is the number of cores in the system')
    parser.add_argument('-c', '--customcutoffs',
                        default=0.90,
                        type=float,
                        help='Custom cutoff values')
    parser.add_argument('-gk', '--gdcs_kmer_size',
                        default=1,
                        help='Kmer size to use for baiting GDCS sequences. Defaults to 15, set lower to increase '
                             'sensitivity.')
    parser.add_argument('-k', '--kmer_size',
                        default=15,
                        help='Kmer size to use for baiting sequences. Defaults to 15, set lower to increase '
                             'sensitivity.')
    parser.add_argument('-sc', '--allow_soft_clips',
                        action='store_true',
                        default=False,
                        help='Do not discard sequences if internal soft clips are present. Default is False, as this '
                             'is usually best for removing false positive matches, but sometimes it is necessary to '
                             'disable this functionality')
    parser.add_argument('-F', '--full_suite',
                        action='store_true',
                        default=False,
                        help='Perform all the built-in GeneSippr analyses (AMR, GDCS, Genesippr, MASH, MLST, '
                             'rMLST, Serotype, SixteenS, and Virulence')
    parser.add_argument('-A', '--resistance',
                        action='store_true',
                        default=False,
                        help='Perform AMR analysis on samples')
    parser.add_argument('-C', '--closestreference',
                        action='store_true',
                        default=False,
                        help='Determine closest RefSeq match with mash')
    parser.add_argument('-G', '--genesippr',
                        action='store_true',
                        default=False,
                        help='Perform GeneSippr analysis on samples')
    parser.add_argument('-M', '--mlst',
                        action='store_true',
                        default=False,
                        help='Perform MLST analysis on samples')
    parser.add_argument('-P', '--pointfinder',
                        action='store_true',
                        default=False,
                        help='Perform PointFinder analyses')
    parser.add_argument('-Q', '--gdcs',
                        action='store_true',
                        default=False,
                        help='Perform GDCS Quality analysis on samples')
    parser.add_argument('-R', '--rmlst',
                        action='store_true',
                        default=False,
                        help='Perform rMLST analysis on samples')
    parser.add_argument('-S', '--serotype',
                        action='store_true',
                        default=False,
                        help='Perform serotype analysis on samples determined to be Escherichia')
    parser.add_argument('-U', '--user_genes',
                        default=False,
                        help='Name and path of user provided (multi-)FASTA file of genes to run against samples')
    parser.add_argument('-V', '--virulence',
                        action='store_true',
                        default=False,
                        help='Perform virulence analysis on samples')
    parser.add_argument('-X', '--sixteens',
                        action='store_true',
                        default=False,
                        help='Perform 16S typing of samples')
    # Get the arguments into an object
    arguments = parser.parse_args()
    SetupLogging()
    # Define the start time
    start = time.time()

    # Run the script
    sippr = Sipprverse(args=arguments,
                       pipelinecommit=commit,
                       startingtime=start,
                       scriptpath=homepath)
    sippr.main()
