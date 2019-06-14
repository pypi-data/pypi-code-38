#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import combinetargets
from genemethods.sipprCommon.sippingmethods import Sippr
from Bio import SeqIO
import logging
import os

__author__ = 'adamkoziol'


class CustomGenes(object):

    def main(self):
        """
        Run the necessary methods in the correct order
        """
        self.target_validate()
        self.gene_names()
        Sippr(inputobject=self,
              k=self.kmer_size,
              cutoff=self.cutoff,
              allow_soft_clips=self.allow_soft_clips)
        self.report()

    def target_validate(self):
        """
        Validate the user-supplied targets by running the (multi-)FASTA file through the method that combines the
        targets. Will also be useful for the downstream analyses
        """
        logging.info('Validating user-supplied targets')
        combinetargets([self.targets], self.targetpath)

    def gene_names(self):
        """
        Extract the names of the user-supplied targets
        """
        # Iterate through all the target names in the formatted targets file
        for record in SeqIO.parse(self.targets, 'fasta'):
            # Append all the gene names to the list of names
            self.genes.append(record.id)

    def report(self):
        """
        Create the report for the user-supplied targets
        """
        # Add all the genes to the header
        header = 'Sample,'
        data = str()
        with open(os.path.join(self.reportpath, '{at}.csv'.format(at=self.analysistype)), 'w') as report:
            write_header = True
            for sample in self.runmetadata:
                data += sample.name + ','
                # Iterate through all the user-supplied target names
                for target in sorted(self.genes):
                    write_results = False
                    # There was an issue with 'target' not matching 'name' due to a dash being replaced by an underscore
                    # only in 'name'. This will hopefully address this issue
                    target = target.replace('-', '_')
                    if write_header:
                        header += '{target}_match_details,{target},'.format(target=target)
                    for name, identity in sample[self.analysistype].results.items():
                        # Ensure that all dashes are replaced with underscores
                        name = name.replace('-', '_')
                        # If the current target matches the target in the header, add the data to the string
                        if name == target:
                            write_results = True
                            gene_results = '{percent_id}% ({avgdepth} +/- {stddev}),{record},'\
                                .format(percent_id=identity,
                                        avgdepth=sample[self.analysistype].avgdepth[name],
                                        stddev=sample[self.analysistype].standarddev[name],
                                        record=sample[self.analysistype].sequences[target])
                            # Populate the data string appropriately
                            data += gene_results
                    # If the target is not present, write dashes to represent the results and sequence
                    if not write_results:
                        data += '-,-,'
                data += ' \n'
                write_header = False
            header += '\n'
            # Write the strings to the report
            report.write(header)
            report.write(data)

    def __init__(self, args, cutoff=0.9, kmer_size=15, allow_soft_clips=False):
        self.targets = os.path.abspath(os.path.join(args.user_genes))
        self.targetpath = os.path.split(self.targets)[0]
        self.path = args.path
        self.reportpath = args.reportpath
        self.runmetadata = args.runmetadata.samples
        self.start = args.starttime
        self.analysistype = 'custom'
        self.cpus = args.cpus
        self.threads = args.threads
        self.homepath = args.homepath
        self.sequencepath = args.sequencepath
        self.pipeline = False
        self.taxonomy = False
        self.logfile = args.logfile
        self.genes = list()
        self.cutoff = cutoff
        self.kmer_size = kmer_size
        self.allow_soft_clips = allow_soft_clips
