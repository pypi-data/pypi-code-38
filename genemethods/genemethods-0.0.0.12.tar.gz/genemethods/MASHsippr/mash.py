#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import make_path, GenObject, run_subprocess, write_to_logfile
from click import progressbar
from threading import Thread
from queue import Queue
import logging
import os
__author__ = 'adamkoziol'


class Mash(object):
    def sketching(self):
        logging.info('Indexing files for {} analysis'.format(self.analysistype))
        # Create the threads for the analysis
        for i in range(self.cpus):
            threads = Thread(target=self.sketch, args=())
            threads.setDaemon(True)
            threads.start()
        # Populate threads for each gene, genome combination
        for sample in self.metadata:
            # Create the analysis type-specific GenObject
            setattr(sample, self.analysistype, GenObject())
            # Set attributes
            sample[self.analysistype].reportdir = os.path.join(sample.general.outputdirectory, self.analysistype)
            make_path(sample[self.analysistype].reportdir)
            sample[self.analysistype].targetpath = self.referencefilepath if not self.pipeline else os.path.join(
                self.referencefilepath, self.analysistype)
            sample[self.analysistype].refseqsketch = os.path.join(sample[self.analysistype].targetpath,
                                                                  'RefSeqSketchesDefaults.msh')
            sample[self.analysistype].sketchfilenoext = os.path.join(sample[self.analysistype].reportdir, sample.name)
            sample[self.analysistype].sketchfile = sample[self.analysistype].sketchfilenoext + '.msh'
            # Make the mash output directory if necessary
            make_path(sample[self.analysistype].reportdir)
            # Create a file containing the path/name of the filtered, corrected fastq files
            sample[self.analysistype].filelist = os.path.join(sample[self.analysistype].reportdir,
                                                              '{sn}_fastqfiles.txt'.format(sn=sample.name))
            with open(sample[self.analysistype].filelist, 'w') as filelist:
                filelist.write('\n'.join(sample.general.trimmedcorrectedfastqfiles))

            # Create the system call
            try:
                if sample.general.trimmedcorrectedfastqfiles[0].endswith('.fasta'):
                    sample.commands.sketch = 'mash sketch -l {file_list} -o {output_file}' \
                        .format(file_list=sample[self.analysistype].filelist,
                                output_file=sample[self.analysistype].sketchfilenoext)
                # IF the inputs are FASTQ files, add the -m flag: Minimum copies of each k-mer required to pass noise
                # filter for reads
                else:
                    sample.commands.sketch = 'mash sketch -m 2 -r -l {file_list} -o {output_file}' \
                        .format(file_list=sample[self.analysistype].filelist,
                                output_file=sample[self.analysistype].sketchfilenoext)
            except IndexError:
                sample.commands.sketch = str()

            # Add each sample to the threads
            try:
                self.sketchqueue.put(sample)
            except (KeyboardInterrupt, SystemExit):
                logging.info('Received keyboard interrupt, quitting threads')
                quit()
        # Join the threads
        self.sketchqueue.join()
        self.mashing()

    def sketch(self):
        while True:
            sample = self.sketchqueue.get()
            if not os.path.isfile(sample[self.analysistype].sketchfile):
                # Run the command
                out, err = run_subprocess(sample.commands.sketch)
                write_to_logfile(out=sample.commands.sketch,
                                 err=sample.commands.sketch,
                                 logfile=self.logfile,
                                 samplelog=sample.general.logout,
                                 sampleerr=sample.general.logerr,
                                 analysislog=None,
                                 analysiserr=None)
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=self.logfile,
                                 samplelog=sample.general.logout,
                                 sampleerr=sample.general.logerr,
                                 analysislog=None,
                                 analysiserr=None)
            self.sketchqueue.task_done()

    def mashing(self):
        logging.info('Performing {} analyses'.format(self.analysistype))
        # Create the threads for the analysis
        for i in range(self.cpus):
                threads = Thread(target=self.mash, args=())
                threads.setDaemon(True)
                threads.start()
        # Populate threads for each gene, genome combination
        with progressbar(self.metadata) as bar:
            for sample in bar:
                sample[self.analysistype].mashresults = os.path.join(sample[self.analysistype].reportdir, '{}.tab'
                                                                     .format(sample.name))

                sample.commands.mash = \
                    'mash dist {refseq_sketch} {sample_sketch} | sort -gk3 > {results}'\
                    .format(refseq_sketch=sample[self.analysistype].refseqsketch,
                            sample_sketch=sample[self.analysistype].sketchfile,
                            results=sample[self.analysistype].mashresults)
                try:
                    self.mashqueue.put(sample)
                except (KeyboardInterrupt, SystemExit):
                    logging.error('Received keyboard interrupt, quitting threads')
                    quit()
        # Join the threads
        self.mashqueue.join()
        self.parse()

    def mash(self):
        while True:
            sample = self.mashqueue.get()
            #
            if not os.path.isfile(sample[self.analysistype].mashresults):
                # Run the command
                out, err = run_subprocess(sample.commands.mash)
                write_to_logfile(out=sample.commands.mash,
                                 err=sample.commands.mash,
                                 logfile=self.logfile,
                                 samplelog=sample.general.logout,
                                 sampleerr=sample.general.logerr,
                                 analysislog=None,
                                 analysiserr=None)
                write_to_logfile(out=out,
                                 err=err,
                                 logfile=self.logfile,
                                 samplelog=sample.general.logout,
                                 sampleerr=sample.general.logerr,
                                 analysislog=None,
                                 analysiserr=None)
            self.mashqueue.task_done()

    def parse(self):
        logging.info('Determining closest refseq genome')
        # Create a dictionary to store the accession: taxonomy id of refseq genomes
        refdict = dict()
        # Set the name of the file storing the assembly summaries
        referencefile = os.path.join(self.referencefilepath, self.analysistype, 'assembly_summary_refseq.txt')
        # Extract the accession: genus species key: value pairs from the refseq summary file
        # UTF-8 encoding since some special chars in the assembly_summary
        with open(referencefile, encoding='utf-8') as reffile:
            for line in reffile:
                # Ignore the first couple of lines
                if line.startswith('# assembly_accession'):
                    # Iterate through all the lines with data
                    for accessionline in reffile:
                        # Replace commas with semicolons
                        accessionline = accessionline.replace(',', ';')
                        # Split the lines on tabs
                        data = accessionline.split('\t')
                        # Populate the dictionary with the accession: tax id e.g. GCF_001298055: Helicobacter pullorum
                        refdict[data[0].split('.')[0]] = data[7]
        for sample in self.metadata:
            # Initialise a list to store all the MASH results
            mashdata = list()
            # Open the results and extract the data
            with open(sample[self.analysistype].mashresults, 'r') as results:
                for line in results:
                    mashdata.append(line.rstrip())
            # Ensure that there is at least a single result
            if mashdata:
                # Iterate through the data
                for linedata in mashdata:
                    try:
                        # Split on tabs
                        data = linedata.split('\t')
                        # Extract the components of the line
                        referenceid, queryid, sample[self.analysistype].mashdistance, sample[self.analysistype]. \
                            pvalue, sample[self.analysistype].nummatches = data
                        # Extract the name of the refseq assembly from the mash outputs, and split as necessary e.g.
                        # GCF_000008865.1_ASM886v1_genomic.fna.gz becomes GCF_000008865
                        refid = referenceid.split('.')[0]
                        # Find the genus and species of the sample using the dictionary of refseq summaries
                        sample[self.analysistype].closestrefseq = refdict[refid]
                        sample[self.analysistype].closestrefseqgenus = \
                            sample[self.analysistype].closestrefseq.split()[0]
                        sample[self.analysistype].closestrefseqspecies = \
                            sample[self.analysistype].closestrefseq.split()[1]
                        # Set the closest refseq genus - will be used for all typing that requires the genus to be known
                        sample.general.referencegenus = sample[self.analysistype].closestrefseqgenus
                        sample.general.closestrefseqgenus = sample[self.analysistype].closestrefseqgenus
                        break
                    except ValueError:
                        sample[self.analysistype].closestrefseq = 'ND'
                        sample[self.analysistype].closestrefseqgenus = 'ND'
                        sample[self.analysistype].closestrefseqspecies = 'ND'
                        sample[self.analysistype].mashdistance = 'ND'
                        sample[self.analysistype].pvalue = 'ND'
                        sample[self.analysistype].nummatches = 'ND'
                        sample.general.referencegenus = 'ND'
                        sample.general.closestrefseqgenus = 'ND'
                        break
                    # I have encountered a strain that has a best match with the RefSeq database provided by the
                    # developers of MASH that doesn't have a corresponding entry in the assembly_summary_refseq.txt
                    # file downloaded from NCBI. Simply pass on this and look for the next best hit
                    except KeyError:
                        pass
            else:
                sample[self.analysistype].closestrefseq = 'ND'
                sample[self.analysistype].closestrefseqgenus = 'ND'
                sample[self.analysistype].closestrefseqspecies = 'ND'
                sample[self.analysistype].mashdistance = 'ND'
                sample[self.analysistype].pvalue = 'ND'
                sample[self.analysistype].nummatches = 'ND'
                sample.general.referencegenus = 'ND'
                sample.general.closestrefseqgenus = 'ND'
        self.reporter()

    def reporter(self):
        """
        Create the MASH report
        """
        logging.info('Creating {} report'.format(self.analysistype))
        make_path(self.reportpath)
        header = 'Strain,ReferenceGenus,ReferenceFile,ReferenceGenomeMashDistance,Pvalue,NumMatchingHashes\n'
        data = ''
        for sample in self.metadata:
            try:
                data += '{},{},{},{},{},{}\n'.format(sample.name,
                                                     sample[self.analysistype].closestrefseqgenus,
                                                     sample[self.analysistype].closestrefseq,
                                                     sample[self.analysistype].mashdistance,
                                                     sample[self.analysistype].pvalue,
                                                     sample[self.analysistype].nummatches)
            except AttributeError:
                data += '{}\n'.format(sample.name)
        # Create the report file
        reportfile = os.path.join(self.reportpath, 'mash.csv')
        with open(reportfile, 'w') as report:
            report.write(header)
            report.write(data)

    def __init__(self, inputobject, analysistype):
        self.metadata = inputobject.runmetadata.samples
        self.referencefilepath = inputobject.reffilepath
        self.starttime = inputobject.starttime
        self.reportpath = inputobject.reportpath
        self.cpus = inputobject.cpus
        self.sketchqueue = Queue(maxsize=self.cpus)
        self.mashqueue = Queue(maxsize=self.cpus)
        self.analysistype = analysistype
        self.pipeline = inputobject.pipeline
        self.logfile = inputobject.logfile
        self.sketching()
