#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import GenObject
from genemethods.sipprCommon.sippingmethods import Sippr
from glob import glob
import logging
import os
__author__ = 'adamkoziol'


class MLSTmap(Sippr):

    def targets(self):
        logging.info('Finding {} target files'.format(self.analysistype))
        #
        alleleset = set()
        for sample in self.runmetadata:
            setattr(sample, self.analysistype, GenObject())
            if sample.general.bestassemblyfile != 'NA':
                sample[self.analysistype].runanalysis = True
                if not self.pipeline:
                    try:
                        sample[self.analysistype].profile = glob(os.path.join(self.targetpath, '*.txt'))[0]
                        sample[self.analysistype].combinedalleles = glob(os.path.join(self.targetpath, '*.fasta'))[0]
                        sample[self.analysistype].targetpath = self.targetpath
                        sample[self.analysistype].alleledir = self.targetpath
                    except IndexError:
                        print('Cannot find the profile and/or the combined allele file in the designated target path '
                              '({}) please ensure that those files exist'.format(self.targetpath))
                        quit()
                else:

                    try:
                        if self.analysistype.lower() == 'rmlst':
                            targetdir = self.targetpath
                        else:
                            targetdir = os.path.join(self.targetpath, sample.general.closestrefseqgenus)
                        sample[self.analysistype].profile = glob(os.path.join(targetdir, '*.txt'))[0]
                        sample[self.analysistype].combinedalleles = glob(os.path.join(targetdir, '*.fasta'))[0]
                        sample[self.analysistype].targetpath = targetdir
                        sample[self.analysistype].alleledir = targetdir
                    except IndexError:
                        sample[self.analysistype].profile = 'NA'
                        sample[self.analysistype].combinedalleles = 'NA'
                        sample[self.analysistype].runanalysis = False
                if os.path.isfile(sample[self.analysistype].combinedalleles):
                    alleleset.add(sample[self.analysistype].combinedalleles)
                else:
                    sample[self.analysistype].runanalysis = False
        #
        genedict = dict()
        for combinedfile in alleleset:
            # Find all the gene names from the combined alleles files
            gene_files = glob(os.path.join(os.path.dirname(combinedfile), '*.tfa'))
            # Create a set of the allele names
            allele_names = set([os.path.splitext(os.path.basename(allele_name))[0] for allele_name in gene_files])
            # Add the set to the dictionary
            genedict[combinedfile] = allele_names
        for sample in self.runmetadata:
            if sample.general.bestassemblyfile != 'NA':
                # Add the combined alleles to the profile set
                self.profileset.add(sample[self.analysistype].combinedalleles)
                try:
                    sample[self.analysistype].alleles = \
                        sorted(list(genedict[sample[self.analysistype].combinedalleles]))
                    sample[self.analysistype].allelenames = \
                        sorted([os.path.splitext(os.path.split(x)[1])[0] for x in sample[self.analysistype].alleles])
                except KeyError:
                    sample[self.analysistype].alleles = 'NA'
                    sample[self.analysistype].allelenames = 'NA'
                #
                sample[self.analysistype].analysistype = self.analysistype
                sample[self.analysistype].reportdir = os.path.join(sample.general.outputdirectory, self.analysistype)
                sample[self.analysistype].baitfile = sample[self.analysistype].combinedalleles

        logging.info('Indexing {} target file'.format(self.analysistype))
        # Ensure that the hash file was successfully created
        # Populate the appropriate attributes
        for sample in self.runmetadata:
            if sample.general.bestassemblyfile != 'NA':
                # Set the necessary attributes
                sample[self.analysistype].outputdir = os.path.join(sample.general.outputdirectory,
                                                                   self.analysistype)
                sample[self.analysistype].logout = os.path.join(sample[self.analysistype].outputdir, 'logout.txt')
                sample[self.analysistype].logerr = os.path.join(sample[self.analysistype].outputdir, 'logerr.txt')
                sample[self.analysistype].baitedfastq = os.path.join(sample[self.analysistype].outputdir,
                                                                     '{}_targetMatches.fastq.gz'
                                                                     .format(self.analysistype))

    def __init__(self, inputobject, analysistype, cutoff):
        self.analysistype = analysistype
        self.targetpath = inputobject.targetpath
        self.profileset = set()
        self.runmetadata = inputobject.runmetadata.samples
        self.pipeline = inputobject.pipeline
        self.copy = inputobject.copy
        self.logfile = inputobject.logfile
        Sippr.__init__(self, inputobject, cutoff)
