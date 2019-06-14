#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import GenObject, make_path, MetadataObject, relative_symlink, \
    run_subprocess, SetupLogging
from genewrappers.biotools import bbtools
from argparse import ArgumentParser
from Bio import SeqIO
from glob import glob
from time import time
import logging
import psutil
import json
import os
__author__ = 'adamkoziol'


class ReadPrep(object):
    
    def main(self):
        self.strains()
        self.sequence_prep()
        self.assembly_length()
        self.simulate_reads()
        self.read_length_adjust('simulated')
        self.link_reads('simulated')
        self.read_quality_trim()
        self.sample_reads()
        self.read_length_adjust('sampled')
        self.link_reads('sampled')
        self.run_genesippr()
        # self.parse_genesippr()
        # self.run_cowbat()
    
    def strains(self):
        """
        Create a dictionary of SEQID: OLNID from the supplied
        """
        with open(os.path.join(self.path, 'strains.csv')) as strains:
            next(strains)
            for line in strains:
                oln, seqid = line.split(',')
                self.straindict[oln] = seqid.rstrip()
                self.strainset.add(oln)
                logging.debug(oln)
                if self.debug:
                    break

    def sequence_prep(self):
        """
        Create metadata objects for all PacBio assembly FASTA files in the sequencepath. 
        Create individual subdirectories for each sample. 
        Relative symlink the original FASTA file to the appropriate subdirectory
        """
        # Create a sorted list of all the FASTA files in the sequence path
        strains = sorted(glob(os.path.join(self.fastapath, '*.fa*'.format(self.fastapath))))
        for sample in strains:
            # Create the object
            metadata = MetadataObject()
            # Set the sample name to be the file name of the sequence by removing the path and file extension
            sample_name = os.path.splitext(os.path.basename(sample))[0]
            if sample_name in self.strainset:
                # Extract the OLNID from the dictionary using the SEQID
                samplename = self.straindict[sample_name]
                # samplename = sample_name
                # Set and create the output directory
                outputdir = os.path.join(self.path, samplename)
                make_path(outputdir)
                # Set the name of the JSON file
                json_metadata = os.path.join(outputdir, '{name}.json'.format(name=samplename))
                if not os.path.isfile(json_metadata):
                    # Create the name and output directory attributes
                    metadata.name = samplename
                    metadata.seqid = sample_name
                    metadata.outputdir = outputdir
                    metadata.jsonfile = json_metadata
                    # Set the name of the FASTA file to use in the analyses
                    metadata.bestassemblyfile = os.path.join(metadata.outputdir,
                                                             '{name}.fasta'.format(name=metadata.name))
                    # Symlink the original file to the output directory
                    relative_symlink(sample, outputdir, '{sn}.fasta'.format(sn=metadata.name))
                    # Associate the corresponding FASTQ files with the assembly
                    metadata.fastqfiles = sorted(glob(os.path.join(self.fastqpath,
                                                                   '{name}*.gz'.format(name=metadata.name))))
                    metadata.forward_fastq, metadata.reverse_fastq = metadata.fastqfiles
                    # Write the object to file
                    self.write_json(metadata)
                else:
                    metadata = self.read_json(json_metadata)
                # Add the metadata object to the list of objects
                self.metadata.append(metadata)

    @staticmethod
    def write_json(metadata):
        """
        Write the metadata object to file
        :param metadata: Metadata object
        """
        # Open the metadata file to write
        with open(metadata.jsonfile, 'w') as metadatafile:
            # Write the json dump of the object dump to the metadata file
            json.dump(metadata.dump(), metadatafile, sort_keys=True, indent=4, separators=(',', ': '))
    
    @staticmethod
    def read_json(json_metadata):
        """
        Read the metadata object from file
        :param json_metadata: Path and file name of JSON-formatted metadata object file
        :return: metadata object
        """
        # Load the metadata object from the file
        with open(json_metadata) as metadatareport:
            jsondata = json.load(metadatareport)
        # Create the metadata objects
        metadata = MetadataObject()
        # Initialise the metadata categories as GenObjects created using the appropriate key
        for attr in jsondata:
            if not isinstance(jsondata[attr], dict):
                setattr(metadata, attr, jsondata[attr])
            else:
                setattr(metadata, attr, GenObject(jsondata[attr]))
        return metadata
    
    def assembly_length(self):
        """
        Use SeqIO.parse to extract the total number of bases in each assembly file
        """
        for sample in self.metadata:
            # Only determine the assembly length if is has not been previously calculated
            if not GenObject.isattr(sample, 'assembly_length'):
                # Create the assembly_length attribute, and set it to 0
                sample.assembly_length = 0
                for record in SeqIO.parse(sample.bestassemblyfile, 'fasta'):
                    # Update the assembly_length attribute with the length of the current contig
                    sample.assembly_length += len(record.seq)
                # Write the updated object to file
                self.write_json(sample)

    def simulate_reads(self):
        """
        Use the PacBio assembly FASTA files to generate simulated reads of appropriate forward and reverse lengths
        at different depths of sequencing using randomreads.sh from the bbtools suite
        """
        logging.info('Read simulation')
        for sample in self.metadata:
            # Create the simulated_reads GenObject
            sample.simulated_reads = GenObject()
            # Iterate through all the desired depths of coverage
            for depth in self.read_depths:
                # Create the depth GenObject
                setattr(sample.simulated_reads, depth, GenObject())
                # Set the depth and output directory attributes for the depth GenObject
                sample.simulated_reads[depth].depth = depth
                sample.simulated_reads[depth].depth_dir = os.path.join(sample.outputdir, 'simulated', depth)
                # Create the output directory
                make_path(sample.simulated_reads[depth].depth_dir)
                # Iterate through all the desired forward and reverse read pair lengths
                for read_pair in self.read_lengths:
                    # Create the read_pair GenObject within the depth GenObject
                    setattr(sample.simulated_reads[depth], read_pair, GenObject())
                    # Set and create the output directory
                    sample.simulated_reads[depth][read_pair].outputdir = \
                        os.path.join(sample.simulated_reads[depth].depth_dir, read_pair)
                    make_path(sample.simulated_reads[depth][read_pair].outputdir)
                    # Create both forward_reads and reverse_reads sub-GenObjects
                    sample.simulated_reads[depth][read_pair].forward_reads = GenObject()
                    sample.simulated_reads[depth][read_pair].reverse_reads = GenObject()
                    # Extract the forward and reverse reads lengths from the read_pair variable
                    sample.simulated_reads[depth][read_pair].forward_reads.length, \
                        sample.simulated_reads[depth][read_pair].reverse_reads.length = read_pair.split('_')
                    # Set the name of the forward reads - include the depth and read length information
                    sample.simulated_reads[depth][read_pair].forward_reads.fastq = \
                        os.path.join(sample.simulated_reads[depth][read_pair].outputdir,
                                     '{name}_{depth}_{read_pair}_R1.fastq.gz'
                                     .format(name=sample.name,
                                             depth=depth,
                                             read_pair=read_pair))
                    # Reverse reads
                    sample.simulated_reads[depth][read_pair].reverse_reads.fastq = \
                        os.path.join(sample.simulated_reads[depth][read_pair].outputdir,
                                     '{name}_{depth}_{read_pair}_R2.fastq.gz'
                                     .format(name=sample.name,
                                             depth=depth,
                                             read_pair=read_pair))
                    # Create the trimmed output directory attribute
                    sample.simulated_reads[depth][read_pair].simulated_trimmed_outputdir \
                        = os.path.join(sample.simulated_reads[depth][read_pair].outputdir,
                                       'simulated_trimmed')
                    # Set the name of the forward trimmed reads - include the depth and read length information
                    # This is set now, as the untrimmed files will be removed, and a check is necessary
                    sample.simulated_reads[depth][read_pair].forward_reads.trimmed_simulated_fastq = \
                        os.path.join(sample.simulated_reads[depth][read_pair].simulated_trimmed_outputdir,
                                     '{name}_simulated_{depth}_{read_pair}_R1.fastq.gz'
                                     .format(name=sample.name,
                                             depth=depth,
                                             read_pair=read_pair))
                    # Reverse reads
                    sample.simulated_reads[depth][read_pair].reverse_reads.trimmed_simulated_fastq = \
                        os.path.join(sample.simulated_reads[depth][read_pair].simulated_trimmed_outputdir,
                                     '{name}_simulated_{depth}_{read_pair}_R2.fastq.gz'
                                     .format(name=sample.name,
                                             depth=depth,
                                             read_pair=read_pair))
                    # Calculate the number of reads required for the forward and reverse reads to yield the
                    # desired coverage depth e.g. 5Mbp genome at 20X coverage: 100Mbp in reads. 50bp forward reads
                    # 150bp reverse reads: forward proportion is 50 / (150 + 50) = 0.25 (and reverse is 0.75).
                    # Forward total reads is 25Mbp (75Mbp reverse). Number of reads required = 25Mbp / 50 bp
                    # 500000 reads total (same for reverse, as the reads are longer)
                    sample.simulated_reads[depth][read_pair].num_reads = \
                        int(sample.assembly_length *
                            int(depth) *
                            (int(sample.simulated_reads[depth][read_pair].forward_reads.length) /
                             (int(sample.simulated_reads[depth][read_pair].forward_reads.length) +
                              int(sample.simulated_reads[depth][read_pair].reverse_reads.length)
                              )
                             ) /
                            int(sample.simulated_reads[depth][read_pair].forward_reads.length)
                            )
                    logging.info(
                        'Simulating {num_reads} paired reads for sample {name} with the following parameters:\n'
                        'depth {dp}, forward reads {fl}bp, and reverse reads {rl}bp'
                        .format(num_reads=sample.simulated_reads[depth][read_pair].num_reads,
                                dp=depth,
                                name=sample.name,
                                fl=sample.simulated_reads[depth][read_pair].forward_reads.length,
                                rl=sample.simulated_reads[depth][read_pair].reverse_reads.length))
                    # If the reverse reads are set to 0, supply different parameters to randomreads
                    if sample.simulated_reads[depth][read_pair].reverse_reads.length != '0':
                        # Ensure that both the simulated reads, and the trimmed simulated reads files don't
                        # exist before simulating the reads
                        if not os.path.isfile(sample.simulated_reads[depth][read_pair].forward_reads.fastq) and \
                                not os.path.isfile(
                                    sample.simulated_reads[depth][read_pair].forward_reads.trimmed_simulated_fastq):
                            # Use the randomreads method in the OLCTools bbtools wrapper to simulate the reads
                            out, \
                                err, \
                                sample.simulated_reads[depth][read_pair].forward_reads.simulate_call = bbtools\
                                .randomreads(reference=sample.bestassemblyfile,
                                             length=sample.simulated_reads[depth][read_pair].reverse_reads.length,
                                             reads=sample.simulated_reads[depth][read_pair].num_reads,
                                             out_fastq=sample.simulated_reads[depth][read_pair].forward_reads.fastq,
                                             paired=True,
                                             returncmd=True,
                                             **{'ziplevel': '9',
                                                'illuminanames': 't',
                                                'Xmx': self.mem}
                                             )
                        else:
                            try:
                                forward_size = os.path.getsize(sample.simulated_reads[depth][read_pair]
                                                               .forward_reads.fastq)
                            except FileNotFoundError:
                                forward_size = 0
                            try:
                                reverse_size = os.path.getsize(sample.simulated_reads[depth][read_pair]
                                                               .reverse_reads.fastq)
                            except FileNotFoundError:
                                reverse_size = 0
                            if forward_size <= 100 or reverse_size <= 100:
                                try:
                                    os.remove(sample.simulated_reads[depth][read_pair].forward_reads.fastq)
                                except FileNotFoundError:
                                    pass
                                try:
                                    os.remove(sample.simulated_reads[depth][read_pair].reverse_reads.fastq)
                                except FileNotFoundError:
                                    pass
                                # Use the randomreads method in the OLCTools bbtools wrapper to simulate the reads
                                out, \
                                err, \
                                sample.simulated_reads[depth][read_pair].forward_reads.simulate_call = bbtools \
                                    .randomreads(reference=sample.bestassemblyfile,
                                                 length=sample.simulated_reads[depth][read_pair].reverse_reads.length,
                                                 reads=sample.simulated_reads[depth][read_pair].num_reads,
                                                 out_fastq=sample.simulated_reads[depth][read_pair].forward_reads.fastq,
                                                 paired=True,
                                                 returncmd=True,
                                                 **{'ziplevel': '9',
                                                    'illuminanames': 't'}
                                                 )
                    else:
                        if not os.path.isfile(sample.simulated_reads[depth][read_pair].forward_reads.fastq):
                            # Use the randomreads method in the OLCTools bbtools wrapper to simulate the reads
                            out, \
                                err, \
                                sample.simulated_reads[depth][read_pair].forward_reads.simulate_call = bbtools\
                                .randomreads(reference=sample.bestassemblyfile,
                                             length=sample.simulated_reads[depth][read_pair].forward_reads.length,
                                             reads=sample.simulated_reads[depth][read_pair].num_reads,
                                             out_fastq=sample.simulated_reads[depth][read_pair].forward_reads.fastq,
                                             paired=False,
                                             returncmd=True,
                                             **{'ziplevel': '9',
                                                'illuminanames': 't'}
                                             )
                # Update the JSON file
                self.write_json(sample)

    def read_length_adjust(self, analysistype):
        """
        Trim the reads to the correct length using reformat.sh
        :param analysistype: current analysis type. Will be either 'simulated' or 'sampled'
        """
        logging.info('Trimming {at} reads'.format(at=analysistype))
        for sample in self.metadata:
            # Iterate through all the desired depths of coverage
            for depth in self.read_depths:
                for read_pair in self.read_lengths:
                    # Create variables using the analysis type. These will be used in setting GenObject attributes
                    read_type = '{at}_reads'.format(at=analysistype)
                    fastq_type = 'trimmed_{at}_fastq'.format(at=analysistype)
                    logging.info(
                        'Trimming forward {at} reads for sample {name} at depth {depth} to length {length}'
                        .format(at=analysistype,
                                name=sample.name,
                                depth=depth,
                                length=sample[read_type][depth][read_pair].forward_reads.length))
                    # Create the output path if necessary
                    make_path(os.path.dirname(sample[read_type][depth][read_pair].forward_reads[fastq_type]))
                    if sample[read_type][depth][read_pair].reverse_reads.length != '0':
                        # Use the reformat method in the OLCTools bbtools wrapper to trim the reads
                        out, \
                            err, \
                            sample[read_type][depth][read_pair].forward_reads.sample_call = bbtools \
                            .reformat_reads(forward_in=sample[read_type][depth][read_pair].forward_reads.fastq,
                                            reverse_in=None,
                                            forward_out=sample[read_type][depth][read_pair].forward_reads[fastq_type],
                                            returncmd=True,
                                            **{'ziplevel': '9',
                                               'forcetrimright':
                                                   sample[read_type][depth][read_pair].forward_reads.length,
                                               'tossbrokenreads': 't',
                                               'tossjunk': 't',
                                               'Xmx': self.mem
                                               }
                                            )
                        # # Remove the untrimmed reads
                        # try:
                        #     os.remove(sample[read_type][depth][read_pair].forward_reads.fastq)
                        # except FileNotFoundError:
                        #     pass

                    else:
                        # If the files do not need to be trimmed, create a symlink to the original file
                        relative_symlink(sample[read_type][depth][read_pair].forward_reads.fastq,
                                         os.path.dirname(sample[read_type][depth][read_pair].
                                                         forward_reads[fastq_type]),
                                         os.path.basename(sample[read_type][depth][read_pair].
                                                          forward_reads[fastq_type])
                                         )
                    # Same as above, but for the reverse reads
                    logging.info(
                        'Trimming reverse {at} reads for sample {name} at depth {depth} to length {length}'
                        .format(at=analysistype,
                                name=sample.name,
                                depth=depth,
                                length=sample[read_type][depth][read_pair].reverse_reads.length))
                    if sample[read_type][depth][read_pair].reverse_reads.length != '0':
                        # Use the reformat method in the OLCTools bbtools wrapper to trim the reads
                        out, \
                            err, \
                            sample[read_type][depth][read_pair].reverse_reads.sample_call = bbtools \
                            .reformat_reads(forward_in=sample[read_type][depth][read_pair].reverse_reads.fastq,
                                            reverse_in=None,
                                            forward_out=sample[read_type][depth][read_pair].reverse_reads[fastq_type],
                                            returncmd=True,
                                            **{'ziplevel': '9',
                                               'forcetrimright':
                                                   sample[read_type][depth][read_pair].reverse_reads.length,
                                               'tossbrokenreads': 't',
                                               'tossjunk': 't',
                                               'Xmx': self.mem
                                               })
                        # # Remove the untrimmed reads
                        # try:
                        #     os.remove(sample[read_type][depth][read_pair].reverse_reads.fastq)
                        # except FileNotFoundError:
                        #     pass
            # Update the JSON file
            self.write_json(sample)

    def read_quality_trim(self):
        """
        Perform quality trim, and toss reads below appropriate thresholds
        """
        logging.info('Quality trim')
        for sample in self.metadata:
            sample.sampled_reads = GenObject()
            sample.sampled_reads.outputdir = os.path.join(sample.outputdir, 'sampled')
            sample.sampled_reads.trimmed_dir = os.path.join(sample.sampled_reads.outputdir, 'qualitytrimmed_reads')
            make_path(sample.sampled_reads.trimmed_dir)
            for depth in self.read_depths:
                # Create the depth GenObject
                setattr(sample.sampled_reads, depth, GenObject())
                # Set the depth and output directory attributes for the depth GenObject
                sample.sampled_reads[depth].depth = depth
                sample.sampled_reads[depth].depth_dir = os.path.join(sample.sampled_reads.outputdir, depth)
                # Create the output directory
                make_path(sample.sampled_reads[depth].depth_dir)
                for read_pair in self.read_lengths:
                    # Create the read_pair GenObject within the depth GenObject
                    setattr(sample.sampled_reads[depth], read_pair, GenObject())
                    # Set and create the output directory
                    sample.sampled_reads[depth][read_pair].outputdir = \
                        os.path.join(sample.sampled_reads[depth].depth_dir, read_pair)
                    make_path(sample.sampled_reads[depth][read_pair].outputdir)
                    # Create both forward_reads and reverse_reads sub-GenObjects
                    sample.sampled_reads[depth][read_pair].forward_reads = GenObject()
                    sample.sampled_reads[depth][read_pair].reverse_reads = GenObject()
                    sample.sampled_reads[depth][read_pair].trimmed_dir = \
                        os.path.join(sample.sampled_reads.trimmed_dir,
                                     read_pair)
                    make_path(sample.sampled_reads[depth][read_pair].trimmed_dir)
                    # Extract the forward and reverse reads lengths from the read_pair variable
                    sample.sampled_reads[depth][read_pair].forward_reads.length, \
                        sample.sampled_reads[depth][read_pair].reverse_reads.length = read_pair.split('_')
                    logging.info('Performing quality trimming on reads from sample {name} at depth {depth} '
                                 'for minimum read length {forward}'
                                 .format(name=sample.name,
                                         depth=depth,
                                         forward=sample.sampled_reads[depth][read_pair].forward_reads.length))
                    # Set the attributes for the trimmed forward and reverse reads to use for subsampling
                    sample.sampled_reads[depth][read_pair].trimmed_forwardfastq = \
                        os.path.join(sample.sampled_reads[depth][read_pair].trimmed_dir,
                                     '{name}_{length}_R1.fastq.gz'
                                     .format(name=sample.name,
                                             length=sample.sampled_reads[depth][read_pair].forward_reads.length))
                    sample.sampled_reads[depth][read_pair].trimmed_reversefastq = \
                        os.path.join(sample.sampled_reads[depth][read_pair].trimmed_dir,
                                     '{name}_{length}_R2.fastq.gz'
                                     .format(name=sample.name,
                                             length=sample.sampled_reads[depth][read_pair].forward_reads.length))
                    # Create the trimmed output directory attribute
                    sample.sampled_reads[depth][read_pair].sampled_trimmed_outputdir \
                        = os.path.join(sample.sampled_reads[depth][read_pair].outputdir,
                                       'sampled_trimmed')
                    # Set the name of the forward trimmed reads - include the depth and read length information
                    # This is set now, as the untrimmed files will be removed, and a check is necessary
                    sample.sampled_reads[depth][read_pair].forward_reads.trimmed_sampled_fastq = \
                        os.path.join(sample.sampled_reads[depth][read_pair].sampled_trimmed_outputdir,
                                     '{name}_sampled_{depth}_{read_pair}_R1.fastq.gz'
                                     .format(name=sample.name,
                                             depth=depth,
                                             read_pair=read_pair))
                    # Reverse reads
                    sample.sampled_reads[depth][read_pair].reverse_reads.trimmed_sampled_fastq = \
                        os.path.join(sample.sampled_reads[depth][read_pair].sampled_trimmed_outputdir,
                                     '{name}_sampled_{depth}_{read_pair}_R2.fastq.gz'
                                     .format(name=sample.name,
                                             depth=depth,
                                             read_pair=read_pair))
                    # Sample if the forward output file does not already exist
                    if not os.path.isfile(sample.sampled_reads[depth][read_pair].trimmed_forwardfastq) and \
                            not os.path.isfile(
                                sample.sampled_reads[depth][read_pair].forward_reads.trimmed_sampled_fastq):
                        out, \
                            err, \
                            sample.sampled_reads[depth][read_pair].sample_cmd = \
                            bbtools.bbduk_trim(forward_in=sample.forward_fastq,
                                               forward_out=sample.sampled_reads[depth][read_pair]
                                               .trimmed_forwardfastq,
                                               reverse_in=sample.reverse_fastq,
                                               reverse_out=sample.sampled_reads[depth][read_pair]
                                               .trimmed_reversefastq,
                                               minlength=sample.sampled_reads[depth][read_pair]
                                               .forward_reads.length,
                                               forcetrimleft=0,
                                               returncmd=True,
                                               **{'ziplevel': '9',
                                                  'Xmx': self.mem})
            # Update the JSON file
            self.write_json(sample)

    def sample_reads(self):
        """
        For each PacBio assembly, sample reads from corresponding FASTQ files for appropriate forward and reverse
        lengths and sequencing depths using reformat.sh from the bbtools suite
        """
        logging.info('Read sampling')
        for sample in self.metadata:
            # Iterate through all the desired depths of coverage
            for depth in self.read_depths:
                for read_pair in self.read_lengths:
                    # Set the name of the output directory
                    sample.sampled_reads[depth][read_pair].sampled_outputdir \
                        = os.path.join(sample.sampled_reads[depth][read_pair].outputdir, 'sampled')
                    # Set the name of the forward reads - include the depth and read length information
                    sample.sampled_reads[depth][read_pair].forward_reads.fastq = \
                        os.path.join(sample.sampled_reads[depth][read_pair].sampled_outputdir,
                                     '{name}_{depth}_{read_pair}_R1.fastq.gz'
                                     .format(name=sample.name,
                                             depth=depth,
                                             read_pair=read_pair))
                    # Reverse reads
                    sample.sampled_reads[depth][read_pair].reverse_reads.fastq = \
                        os.path.join(sample.sampled_reads[depth][read_pair].sampled_outputdir,
                                     '{name}_{depth}_{read_pair}_R2.fastq.gz'
                                     .format(name=sample.name,
                                             depth=depth,
                                             read_pair=read_pair))
                    logging.info(
                        'Sampling {num_reads} paired reads for sample {name} with the following parameters:\n'
                        'depth {dp}, forward reads {fl}bp, and reverse reads {rl}bp'
                        .format(num_reads=sample.simulated_reads[depth][read_pair].num_reads,
                                dp=depth,
                                name=sample.name,
                                fl=sample.sampled_reads[depth][read_pair].forward_reads.length,
                                rl=sample.sampled_reads[depth][read_pair].reverse_reads.length))
                    # Use the reformat method in the OLCTools bbtools wrapper
                    # Note that upsample=t is used to ensure that the target number of reads (samplereadstarget) is met
                    if not os.path.isfile(sample.sampled_reads[depth][read_pair].forward_reads.trimmed_sampled_fastq):
                        out, \
                            err, \
                            sample.sampled_reads[depth][read_pair].sample_call = bbtools \
                            .reformat_reads(forward_in=sample.sampled_reads[depth][read_pair].trimmed_forwardfastq,
                                            reverse_in=sample.sampled_reads[depth][read_pair].trimmed_reversefastq,
                                            forward_out=sample.sampled_reads[depth][read_pair].forward_reads.fastq,
                                            reverse_out=sample.sampled_reads[depth][read_pair].reverse_reads.fastq,
                                            returncmd=True,
                                            **{'samplereadstarget': sample.simulated_reads[depth][read_pair].num_reads,
                                               'upsample': 't',
                                               'minlength':
                                                   sample.sampled_reads[depth][read_pair].forward_reads.length,
                                               'ziplevel': '9',
                                               'tossbrokenreads': 't',
                                               'tossjunk': 't',
                                               'Xmx': self.mem
                                               }
                                            )
                    # # Remove the trimmed reads, as they are no longer necessary
                    # try:
                    #     os.remove(sample.sampled_reads[depth][read_pair].trimmed_forwardfastq)
                    #     os.remove(sample.sampled_reads[depth][read_pair].trimmed_reversefastq)
                    # except FileNotFoundError:
                    #     pass
            # Update the JSON file
            self.write_json(sample)

    def link_reads(self, analysistype):
        """
        Create folders with relative symlinks to the desired simulated/sampled reads. These folders will contain all
        the reads created for each sample, and will be processed with GeneSippr and COWBAT pipelines
        :param analysistype: Current analysis type. Will either be 'simulated' or 'sampled'
        """
        logging.info('Linking {at} reads'.format(at=analysistype))
        for sample in self.metadata:
            # Create the output directories
            genesippr_dir = os.path.join(self.path, 'genesippr', sample.name)
            sample.genesippr_dir = genesippr_dir
            make_path(genesippr_dir)
            cowbat_dir = os.path.join(self.path, 'cowbat', sample.name)
            sample.cowbat_dir = cowbat_dir
            make_path(cowbat_dir)
            # Iterate through all the desired depths of coverage
            for depth in self.read_depths:
                for read_pair in self.read_lengths:
                    # Create variables using the analysis type. These will be used in setting GenObject attributes
                    read_type = '{at}_reads'.format(at=analysistype)
                    fastq_type = 'trimmed_{at}_fastq'.format(at=analysistype)
                    # Link reads to both output directories
                    for output_dir in [genesippr_dir, cowbat_dir]:
                        # If the original reads are shorter than the specified read length, the FASTQ files will exist,
                        # but will be empty. Do not create links for these files
                        size = os.path.getsize(sample[read_type][depth][read_pair].forward_reads[fastq_type])
                        if size > 20:
                            # Create relative symlinks to the FASTQ files - use the relative path from the desired
                            # output directory to the read storage path e.g.
                            # ../../2013-SEQ-0072/simulated/40/50_150/simulated_trimmed/2013-SEQ-0072_simulated_40_50_150_R1.fastq.gz
                            # is the relative path to the output_dir. The link name is the base name of the reads
                            # joined to the desired output directory e.g.
                            # output_dir/2013-SEQ-0072/2013-SEQ-0072_simulated_40_50_150_R1.fastq.gz
                            relative_symlink(sample[read_type][depth][read_pair].forward_reads[fastq_type],
                                             output_dir)
                            # Original FASTQ files
                            relative_symlink(sample.forward_fastq,
                                             output_dir)
                            relative_symlink(sample.reverse_fastq,
                                             output_dir)
                        # Reverse reads
                        try:
                            size = os.path.getsize(sample[read_type][depth][read_pair].reverse_reads[fastq_type])
                            if size > 20:
                                relative_symlink(sample[read_type][depth][read_pair].reverse_reads[fastq_type],
                                                 output_dir)
                        except FileNotFoundError:
                            pass

    def run_genesippr(self):
        """
        Run GeneSippr on each of the samples
        """
        from pathlib import Path
        home = str(Path.home())
        logging.info('GeneSippr')
        # These unfortunate hard coded paths appear to be necessary
        miniconda_path = os.path.join(home, 'miniconda3')
        miniconda_path = miniconda_path if os.path.isdir(miniconda_path) else os.path.join(home, 'miniconda')
        logging.debug(miniconda_path)
        activate = 'source {mp}/bin/activate {mp}/envs/sipprverse'.format(mp=miniconda_path)
        sippr_path = '{mp}/envs/sipprverse/bin/sippr.py'.format(mp=miniconda_path)
        for sample in self.metadata:
            logging.info(sample.name)

            # Run the pipeline. Check to make sure that the serosippr report, which is created last doesn't exist
            if not os.path.isfile(os.path.join(sample.genesippr_dir, 'reports', 'genesippr.csv')):
                cmd = 'python {py_path} -o {outpath} -s {seqpath} -r {refpath} -F'\
                    .format(py_path=sippr_path,
                            outpath=sample.genesippr_dir,
                            seqpath=sample.genesippr_dir,
                            refpath=self.referencefilepath
                            )
                logging.critical(cmd)
                # Create another shell script to execute within the PlasmidExtractor conda environment
                template = "#!/bin/bash\n{activate} && {cmd}".format(activate=activate,
                                                                     cmd=cmd)
                genesippr_script = os.path.join(sample.genesippr_dir, 'run_genesippr.sh')
                with open(genesippr_script, 'w+') as file:
                    file.write(template)
                # Modify the permissions of the script to allow it to be run on the node
                self.make_executable(genesippr_script)
                # Run shell script
                os.system('/bin/bash {}'.format(genesippr_script))
                # quit()

    def parse_genesippr(self):
        """

        """
        import pandas
        for sample in self.metadata:
            sample.genesippr_reports = sorted(glob(os.path.join(sample.genesippr_dir, 'reports', '*.csv')))
            for report in sample.genesippr_reports:
                # Extract the analysis type from the report name
                report_name = os.path.splitext(os.path.basename(report))[0]
                # A dictionary to store the parsed CSV file in a more readable format
                nesteddictionary = dict()
                # Use pandas to read in the CSV file, and subsequently convert the pandas data frame to a dictionary
                # (.to_dict()).
                dictionary = pandas.read_csv(report).to_dict()
                # Iterate through the dictionary - each header from the CSV file
                for header in dictionary:
                    # primary_key is the primary key, and value is the value of the cell for that
                    # primary key + header combination
                    for primary_key, value in dictionary[header].items():
                        # Update the dictionary with the new data
                        try:
                            nesteddictionary[primary_key].update({header: value})
                        # Create the nested dictionary if it hasn't been created yet
                        except KeyError:
                            nesteddictionary[primary_key] = dict()
                            nesteddictionary[primary_key].update({header: value})
                #
                strain = str()
                for name, value in nesteddictionary.items():
                    # As strain name is not printed on every line, it is entered as 'nan' by pandas. This is a float.
                    if type(value['Strain']) is not float:
                        strain = value['Strain']
                        # Find the 'original' sample
                        if len(strain.split('_')) > 1:
                            strain, analysis_type, depth, forward_length, reverse_length = strain.split('_')
                            print(strain, analysis_type, depth, forward_length, reverse_length)
                        else:
                            print(strain)

    @staticmethod
    def make_executable(path):
        """
        Takes a shell script and makes it executable (chmod +x)
        :param path: path to shell script
        """
        mode = os.stat(path).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(path, mode)

    # def run_cowbat(self):
    #     """
    #     Run COWBAT on all the samples
    #     """
    #     logging.info('COWBAT')
    #     # Create a MetadataObject to spoof ArgumentParser supplied arguments
    #     args = MetadataObject()
    #     args.referencefilepath = self.referencefilepath
    #     args.numreads = 2
    #     args.preprocess = False
    #     args.startingtime = self.start
    #     args.customsamplesheet = False
    #     args.threads = multiprocessing.cpu_count() - 1
    #     args.commit = b''
    #     args.homepath = ''
    #     for sample in self.metadata:
    #         args.sequencepath = sample.cowbat_dir
    #         # Run the pipeline
    #         cowbat = RunAssemble(args)
    #         cowbat.main()

    def __init__(self, start, path, referencefilepath, debug):
        """

        :param start: Time at which the analyses were started
        :param path: Location in which analyses are to be performed
        :param referencefilepath: Location of reference database
        :param debug: Boolean for whether debug level logging enabled, and whether a toy dataset should be used
        """
        self.start = start
        self.path = os.path.join(path)
        self.referencefilepath = os.path.join(referencefilepath)
        self.fastapath = os.path.join(self.path, 'fasta')
        self.fastqpath = os.path.join(self.path, 'fastq')
        self.debug = debug
        if self.debug:
            self.read_lengths = ['50_0']
            self.read_depths = ['10']
        else:
            self.read_lengths = ['50_0', '50_50', '50_75', '50_100', '50_150', '50_250', '50_300',
                                 '75_0', '75_50', '75_75', '75_100', '75_150', '75_250', '75_300',
                                 '100_0', '100_50', '100_75', '100_100', '100_150', '100_250', '100_300',
                                 '150_0', '150_50', '150_75', '150_100', '150_150', '150_250', '150_300',
                                 '250_0', '250_50', '250_75', '250_100', '250_150', '250_250', '250_300',
                                 '300_0', '300_50', '300_75', '300_100', '300_150', '300_250', '300_300']
            self.read_depths = ['10', '20', '30', '40', '50']
        self.straindict = dict()
        self.strainset = set()
        self.metadata = list()
        self.mem = int(0.85 * float(psutil.virtual_memory().total))


if __name__ == '__main__':
    # Parser for arguments
    parser = ArgumentParser(description='Perform FASTQ read simulations and sampling from assembled genomes, and'
                                        'corresponding FASTQ reads, respectively')
    parser.add_argument('-p', '--path',
                        required=True,
                        help='Path to folder containing subdirectories with assemblies, and raw reads')
    parser.add_argument('-r', '--referencefilepath',
                        required=True,
                        help='Provide the location of the folder containing the pipeline accessory files (reference '
                             'genomes, MLST data, etc.')
    parser.add_argument('-d', '--debug',
                        default=False,
                        action='store_true',
                        help='Run the pipeline in debug mode. Will enable more logging. Currently will use a '
                             'greatly decreased range of read lengths and read depths')
    # Get the arguments into an object
    arguments = parser.parse_args()
    SetupLogging(debug=arguments.debug)
    arguments.start = time()
    prep = ReadPrep(start=arguments.start,
                    path=arguments.path,
                    referencefilepath=arguments.referencefilepath,
                    debug=arguments.debug)
    prep.main()
    logging.info('Analyses Complete!')
