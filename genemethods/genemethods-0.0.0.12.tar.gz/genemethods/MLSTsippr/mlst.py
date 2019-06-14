#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import make_dict, GenObject, make_path, SetupLogging
from olctools.accessoryFunctions.metadataprinter import MetadataPrinter
from genemethods.sipprCommon.objectprep import Objectprep
from genemethods.MLSTsippr.sipprmlst import MLSTmap
from argparse import ArgumentParser
from collections import defaultdict
from csv import DictReader
import multiprocessing
import subprocess
import operator
import logging
import time
import sys
import os


__author__ = 'adamkoziol'


class GeneSippr(object):

    def runner(self):
        """
        Run the necessary methods in the correct order
        """
        if os.path.isfile(self.report):
            self.report_parse()
        else:
            logging.info('Starting {at} analysis pipeline'.format(at=self.analysistype))
            # Create the objects to be used in the analyses (if required)
            general = None
            for sample in self.runmetadata.samples:
                general = getattr(sample, 'general')
            if general is None:
                # Create the objects to be used in the analyses
                objects = Objectprep(self)
                objects.objectprep()
                self.runmetadata = objects.samples
            # Run the analyses
            MLSTmap(self, self.analysistype, self.cutoff)
            # Create the reports
            self.reporter()
            # Print the metadata to a .json file
            MetadataPrinter(self)

    def reporter(self):
        """
        Runs the necessary methods to parse raw read outputs
        """
        logging.info('Preparing reports')
        # Populate self.plusdict in order to reuse parsing code from an assembly-based method
        for sample in self.runmetadata.samples:
            self.plusdict[sample.name] = dict()
            self.matchdict[sample.name] = dict()
            if sample.general.bestassemblyfile != 'NA':
                for gene in sample[self.analysistype].allelenames:
                    self.plusdict[sample.name][gene] = dict()
                    for allele, percentidentity in sample[self.analysistype].results.items():
                        if gene in allele:
                            # Split the allele number from the gene name using the appropriate delimiter
                            if '_' in allele:
                                splitter = '_'
                            elif '-' in allele:
                                splitter = '-'
                            else:
                                splitter = ''
                            self.matchdict[sample.name].update({gene: allele.split(splitter)[-1]})
                            # Create the plusdict dictionary as in the assembly-based (r)MLST method. Allows all the
                            # parsing and sequence typing code to be reused.
                            try:
                                self.plusdict[sample.name][gene][allele.split(splitter)[-1]][percentidentity] \
                                    = sample[self.analysistype].avgdepth[allele]
                            except KeyError:
                                self.plusdict[sample.name][gene][allele.split(splitter)[-1]] = dict()
                                self.plusdict[sample.name][gene][allele.split(splitter)[-1]][percentidentity] \
                                    = sample[self.analysistype].avgdepth[allele]
                    if gene not in self.matchdict[sample.name]:
                        self.matchdict[sample.name].update({gene: 'N'})
        self.profiler()
        self.sequencetyper()
        self.mlstreporter()

    def profiler(self):
        """
        Creates a dictionary from the profile scheme(s)
        """
        logging.info('Loading profiles')
        # Initialise variables
        profiledata = defaultdict(make_dict)
        reverse_profiledata = dict()
        profileset = set()
        # Find all the unique profiles to use with a set
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                if sample[self.analysistype].profile not in ['NA', 'ND']:
                    profileset.add(sample[self.analysistype].profile)
        # Extract the profiles for each set
        for sequenceprofile in profileset:
            #
            if sequenceprofile not in self.meta_dict:
                self.meta_dict[sequenceprofile] = dict()
            reverse_profiledata[sequenceprofile] = dict()
            self.meta_dict[sequenceprofile]['ND'] = dict()
            # Clear the list of genes
            geneset = set()
            # Calculate the total number of genes in the typing scheme
            for sample in self.runmetadata.samples:
                if sample.general.bestassemblyfile != 'NA':
                    if sequenceprofile == sample[self.analysistype].profile:
                        geneset = {allele for allele in sample[self.analysistype].alleles}
            try:
                # Open the sequence profile file as a dictionary
                profile = DictReader(open(sequenceprofile), dialect='excel-tab')
            # Revert to standard comma separated values
            except KeyError:
                # Open the sequence profile file as a dictionary
                profile = DictReader(open(sequenceprofile))
            # Iterate through the rows
            for row in profile:
                # Populate the profile dictionary with profile number: {gene: allele}. Use the first field name,
                # which will be either ST, or rST as the key to determine the profile number value
                allele_comprehension = {gene: allele for gene, allele in row.items() if gene in geneset}
                st = row[profile.fieldnames[0]]
                for header, value in row.items():
                    value = value if value else 'ND'
                    if header not in geneset and header not in ['ST', 'rST']:
                        if st not in self.meta_dict[sequenceprofile]:
                            self.meta_dict[sequenceprofile][st] = dict()
                        if header == 'CC' or header == 'clonal_complex':
                            header = 'CC'
                        self.meta_dict[sequenceprofile][st][header] = value
                        self.meta_dict[sequenceprofile]['ND'][header] = 'ND'
                        self.meta_dict[sequenceprofile][st]['PredictedSerogroup'] = 'ND'
                        if header not in self.meta_headers:
                            self.meta_headers.append(header)
                profiledata[sequenceprofile][st] = allele_comprehension
                # Create a 'reverse' dictionary using the the allele comprehension as the key, and
                # the sequence type as the value - can be used if exact matches are ever desired
                reverse_profiledata[sequenceprofile].update({frozenset(allele_comprehension.items()): st})
            # Add the profile data, and gene list to each sample
            for sample in self.runmetadata.samples:
                if sample.general.bestassemblyfile != 'NA' and sample[self.analysistype].profile not in ['NA', 'ND']:
                    if sequenceprofile == sample[self.analysistype].profile:
                        # Populate the metadata with the profile data
                        sample[self.analysistype].profiledata = profiledata[sample[self.analysistype].profile]
                        sample[self.analysistype].reverse_profiledata = reverse_profiledata[sequenceprofile]
                        sample[self.analysistype].meta_dict = self.meta_dict[sequenceprofile]
                else:
                    sample[self.analysistype].profiledata = 'NA'
                    sample[self.analysistype].reverse_profiledata = 'NA'
                    sample[self.analysistype].meta_dict = 'NA'

    def sequencetyper(self):
        """
        Determines the sequence type of each strain based on comparisons to sequence type profiles
        """
        logging.info('Performing sequence typing')
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                if type(sample[self.analysistype].allelenames) == list:
                    # Initialise variables
                    header = 0
                    genome = sample.name
                    # Initialise self.bestmatch[genome] with an int that will eventually be replaced by the # of matches
                    self.bestmatch[genome] = defaultdict(int)
                    if sample[self.analysistype].profile not in ['NA', 'ND']:
                        # Create the profiledata variable to avoid writing self.profiledata[self.analysistype]
                        profiledata = sample[self.analysistype].profiledata
                        # Calculate the number of allele matches between each sequence type and the results
                        best_seqtype = dict()
                        for sequencetype in sample[self.analysistype].profiledata:
                            # Initialise a counter
                            count = 0
                            # Iterate through each gene for the sequence type
                            for gene, refallele in sample[self.analysistype].profiledata[sequencetype].items():
                                # Use the gene to extract the calculated allele
                                allele = self.matchdict[genome][gene]
                                # Increment the count on a match
                                if refallele == allele:
                                    count += 1
                            # Add the sequence type to the set of sequence types with the number of matches as the key
                            try:
                                best_seqtype[count].add(sequencetype)
                            except KeyError:
                                best_seqtype[count] = set()
                                best_seqtype[count].add(sequencetype)
                        # Find the highest number of matches from the dictionary
                        best_count, best_type = sorted(best_seqtype.items(), key=operator.itemgetter(0),
                                                       reverse=True)[0]
                        # Deal with multiple allele matches
                        for gene in sample[self.analysistype].allelenames:
                            # Clear the appropriate count and lists
                            multiallele = list()
                            multipercent = list()
                            # Go through the alleles in plusdict
                            for allele in self.plusdict[genome][gene]:
                                percentid = list(self.plusdict[genome][gene][allele].keys())[0]
                                # "N" alleles screw up the allele splitter function
                                if allele not in ['N', 'NA']:
                                    # Append as appropriate - alleleNumber is treated as an integer for proper sorting
                                    multiallele.append(int(allele))
                                    multipercent.append(percentid)
                                # If the allele is "N"
                                else:
                                    # Append "N" and a percent identity of 0
                                    multiallele.append("N")
                                    multipercent.append(0)
                            # Populate self.bestdict with genome, gene, alleles joined with a space (this was made like
                            # this because allele is a list generated by the .iteritems() above
                            try:
                                self.bestdict[genome][gene][" ".join(str(allele)
                                                                     for allele in sorted(multiallele))] = \
                                    multipercent[0]
                            except IndexError:
                                self.bestdict[genome][gene]['NA'] = 0
                            # Find the profile with the most alleles in common with the query genome
                            for sequencetype in best_type:
                                # The number of genes in the analysis
                                header = len(profiledata[sequencetype])
                                # refallele is the allele number of the sequence type
                                refallele = profiledata[sequencetype][gene]
                                # If there are multiple allele matches for a gene in the reference profile e.g. 10 692
                                if len(refallele.split(" ")) > 1:
                                    # Map the split (on a space) alleles as integers - if they are treated as integers,
                                    # the alleles will sort properly
                                    intrefallele = map(int, refallele.split(" "))
                                    # Create a string of the joined, sorted alleles
                                    sortedrefallele = " ".join(str(allele) for allele in sorted(intrefallele))
                                else:
                                    # Use the reference allele as the sortedRefAllele
                                    sortedrefallele = refallele
                                for allele, percentid in self.bestdict[genome][gene].items():
                                    # If the allele in the query genome matches the allele in the reference profile, add
                                    # the result to the bestmatch dictionary. Genes with multiple alleles were sorted
                                    # the same, strings with multiple alleles will match: 10 692 will never be 692 10
                                    if allele == sortedrefallele and float(percentid) == 100.00:
                                        # Increment the number of matches to each profile
                                        self.bestmatch[genome][sequencetype] += 1
                                    # Special handling of BACT000060 and BACT000065 genes for E. coli and BACT000014
                                    # for Listeria. When the reference profile has an allele of 'N', and the query
                                    # allele doesn't, set the allele to 'N', and count it as a match
                                    elif sortedrefallele == 'N' and allele != 'N':
                                        # Increment the number of matches to each profile
                                        self.bestmatch[genome][sequencetype] += 1
                                    # Consider cases with multiple allele matches
                                    elif len(allele.split(' ')) > 1:
                                        # Also increment the number of matches if one of the alleles matches the
                                        # reference allele e.g. 41 16665 will match either 41 or 16665
                                        if sortedrefallele != 'N' and allele != 'N':
                                            match = False
                                            for sub_allele in allele.split(' '):
                                                if sub_allele == refallele:
                                                    match = True
                                            if match:
                                                # Increment the number of matches to each profile
                                                self.bestmatch[genome][sequencetype] += 1
                                    elif allele == sortedrefallele and sortedrefallele == 'N':
                                        # Increment the number of matches to each profile
                                        self.bestmatch[genome][sequencetype] += 1
                        # Get the best number of matches
                        # From: https://stackoverflow.com/questions/613183/sort-a-python-dictionary-by-value
                        try:
                            sortedmatches = sorted(self.bestmatch[genome].items(), key=operator.itemgetter(1),
                                                   reverse=True)[0][1]
                        # If there are no matches, set :sortedmatches to zero
                        except IndexError:
                            sortedmatches = 0
                        # Otherwise, the query profile matches the reference profile
                        if int(sortedmatches) == header:
                            # Iterate through best match
                            for sequencetype, matches in self.bestmatch[genome].items():
                                if matches == sortedmatches:
                                    for gene in profiledata[sequencetype]:
                                        # Populate resultProfile with the genome, best match to profile, # of matches
                                        # to the profile, gene, query allele(s), reference allele(s), and % identity
                                        self.resultprofile[genome][sequencetype][sortedmatches][gene][
                                            list(self.bestdict[genome][gene]
                                                 .keys())[0]] = str(list(self.bestdict[genome][gene].values())[0])
                                    try:
                                        sample[self.analysistype].sequencetype.add(sequencetype)
                                    except AttributeError:
                                        sample[self.analysistype].sequencetype = set()
                                        sample[self.analysistype].sequencetype.add(sequencetype)
                                    sample[self.analysistype].matchestosequencetype = matches
                        # If there are fewer matches than the total number of genes in the typing scheme
                        elif 0 < int(sortedmatches) < header:
                            mismatches = []
                            # Iterate through the sequence types and the number of matches in bestDict for each genome
                            for sequencetype, matches in self.bestmatch[genome].items():
                                # If the number of matches for a profile matches the best number of matches
                                if matches == sortedmatches:
                                    # Iterate through the gene in the analysis
                                    for gene in profiledata[sequencetype]:
                                        # Get the reference allele as above
                                        refallele = profiledata[sequencetype][gene]
                                        # As above get the reference allele split and ordered as necessary
                                        if len(refallele.split(" ")) > 1:
                                            intrefallele = map(int, refallele.split(" "))
                                            sortedrefallele = " ".join(str(allele) for allele in sorted(intrefallele))
                                        else:
                                            sortedrefallele = refallele
                                        # Populate self.mlstseqtype with the genome, best match to profile, # of matches
                                        # to the profile, gene, query allele(s), reference allele(s), and % identity
                                        if self.analysistype == 'mlst':
                                            self.resultprofile[genome][sequencetype][sortedmatches][gene][
                                                list(self.bestdict[genome][gene]
                                                     .keys())[0]] = str(list(self.bestdict[genome][gene].values())[0])
                                        else:
                                            self.resultprofile[genome][sequencetype][sortedmatches][gene][
                                                list(self.bestdict[genome][gene].keys())[0]] \
                                                = str(list(self.bestdict[genome][gene].values())[0])
                                            #
                                            if sortedrefallele != list(self.bestdict[sample.name][gene].keys())[0]:
                                                mismatches.append(
                                                    ({gene: ('{} ({})'.format(list(self.bestdict[sample.name][gene]
                                                                                   .keys())[0], sortedrefallele))}))
                                        sample[self.analysistype].mismatchestosequencetype = mismatches
                                        try:
                                            sample[self.analysistype].sequencetype.add(sequencetype)
                                        except AttributeError:
                                            sample[self.analysistype].sequencetype = set()
                                            sample[self.analysistype].sequencetype.add(sequencetype)
                                        sample[self.analysistype].matchestosequencetype = matches
                        elif sortedmatches == 0:
                            for gene in sample[self.analysistype].allelenames:
                                # Populate the results profile with negative values for sequence type and sorted matches
                                self.resultprofile[genome]['NA'][sortedmatches][gene]['NA'] = 0
                            # Add the new profile to the profile file (if the option is enabled)
                            sample[self.analysistype].sequencetype = 'NA'
                            sample[self.analysistype].matchestosequencetype = 'NA'
                            sample[self.analysistype].mismatchestosequencetype = 'NA'
                        else:
                            sample[self.analysistype].matchestosequencetype = 'NA'
                            sample[self.analysistype].mismatchestosequencetype = 'NA'
                            sample[self.analysistype].sequencetype = 'NA'
                else:
                    sample[self.analysistype].matchestosequencetype = 'NA'
                    sample[self.analysistype].mismatchestosequencetype = 'NA'
                    sample[self.analysistype].sequencetype = 'NA'

            else:
                sample[self.analysistype].matchestosequencetype = 'NA'
                sample[self.analysistype].mismatchestosequencetype = 'NA'
                sample[self.analysistype].sequencetype = 'NA'
            # Clear out the reverse_profiledata attribute - frozen sets can not be .json encoded
            try:
                delattr(sample[self.analysistype], 'reverse_profiledata')
            except AttributeError:
                pass

    def mlstreporter(self):
        """ Parse the results into a report"""
        logging.info('Writing reports')
        # Initialise variables
        header_row = str()
        combinedrow = str()
        combined_header_row = str()
        reportdirset = set()
        mlst_dict = dict()
        # Populate a set of all the report directories to use. A standard analysis will only have a single report
        # directory, while pipeline analyses will have as many report directories as there are assembled samples
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                # Ignore samples that lack a populated reportdir attribute
                if sample[self.analysistype].reportdir != 'NA':
                    make_path(sample[self.analysistype].reportdir)
                    # Add to the set - I probably could have used a counter here, but I decided against it
                    reportdirset.add(sample[self.analysistype].reportdir)
        # Create a report for each sample from :self.resultprofile
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                if sample[self.analysistype].reportdir != 'NA':
                    if type(sample[self.analysistype].allelenames) == list:
                        # Initialise the string
                        row = str()
                        # Extract the closest reference genus
                        try:
                            genus = sample.general.closestrefseqgenus
                        except AttributeError:
                            try:
                                genus = sample.general.referencegenus
                            except AttributeError:
                                genus = 'ND'
                        if self.analysistype == 'mlst':
                            header_row = str()
                            if genus not in mlst_dict:
                                mlst_dict[genus] = dict()
                        # Additional fields such as clonal complex and lineage
                        additional_fields = list()
                        #
                        if self.meta_headers:
                            for header in self.meta_headers:
                                try:
                                    _ = sample[self.analysistype].meta_dict[
                                        list(sample[self.analysistype].sequencetype)[0]][header]
                                    additional_fields.append(header.rstrip())
                                except (AttributeError, KeyError):
                                    pass
                        if self.analysistype == 'mlst':
                            additional_fields = sorted(additional_fields)
                            #
                            try:
                                if genus == 'Listeria':
                                    additional_fields.append('PredictedSerogroup')
                            except AttributeError:
                                pass
                            header_fields = additional_fields
                        else:
                            additional_fields = [
                                'genus', 'species', 'subspecies', 'lineage', 'sublineage', 'other_designation', 'notes'
                            ]
                            header_fields = [
                                'rMLST_genus', 'species', 'subspecies', 'lineage', 'sublineage', 'other_designation',
                                'notes'
                            ]
                        # Populate the header with the appropriate data, including all the genes in the list of targets
                        if not header_row:
                            if additional_fields:
                                header_row = 'Strain,MASHGenus,{additional},SequenceType,Matches,{matches},\n' \
                                    .format(additional=','.join(header_fields),
                                            matches=','.join(sorted(sample[self.analysistype].allelenames)))
                            else:
                                header_row = 'Strain,MASHGenus,SequenceType,Matches,{matches},\n' \
                                    .format(matches=','.join(sorted(sample[self.analysistype].allelenames)))
                        sample[self.analysistype].sequencetype = set()
                        # Iterate through the best sequence types for the sample
                        for seqtype in sorted(self.resultprofile[sample.name]):
                            sample[self.analysistype].sequencetype.add(seqtype)
                            # except AttributeError:
                            #     sample[self.analysistype].sequencetype = set(seqtype)
                            # sample[self.analysistype].sequencetype = seqtype
                            try:
                                if genus == 'Listeria':
                                    for serogroup, mlst_list in self.listeria_serogroup_dict.items():
                                        if seqtype in [str(string) for string in mlst_list]:
                                            sample[self.analysistype].meta_dict[seqtype]['PredictedSerogroup'] = \
                                                serogroup
                            except AttributeError:
                                pass
                            # The number of matches to the profile
                            sample[self.analysistype].matches = list(self.resultprofile[sample.name][seqtype].keys())[0]
                            # If this is the first of one or more sequence types, include the sample name
                            if additional_fields:
                                row += '{name},{mashgenus},{additional},{seqtype},{matches},'\
                                    .format(name=sample.name,
                                            mashgenus=genus,
                                            additional=','.join(sample[self.analysistype].
                                                                meta_dict[seqtype][header].replace(',', ';')
                                                                for header in additional_fields),
                                            seqtype=seqtype,
                                            matches=sample[self.analysistype].matches)
                            else:
                                row += '{name},{mashgenus},{seqtype},{matches},' \
                                    .format(name=sample.name,
                                            mashgenus=genus,
                                            seqtype=seqtype,
                                            matches=sample[self.analysistype].matches)
                            # Create an attribute to store the results in a format suitable for parsing for creating
                            # the final combinedMetadata report
                            sample[self.analysistype].combined_metadata_results = dict()
                            # Iterate through all the genes present in the analyses for the sample
                            for gene in sorted(sample[self.analysistype].allelenames):
                                refallele = sample[self.analysistype].profiledata[seqtype][gene]
                                # Set the allele and percent id from the dictionary's keys and values, respectively
                                allele = \
                                    list(self.resultprofile[sample.name][seqtype][sample[self.analysistype].matches]
                                         [gene].keys())[0]
                                percentid = \
                                    list(self.resultprofile[sample.name][seqtype][sample[self.analysistype].matches]
                                         [gene].values())[0]

                                gene_allele = '{gene}_{allele}'.format(gene=gene,
                                                                       allele=allele)
                                sample[self.analysistype].combined_metadata_results[gene_allele] = percentid
                                try:
                                    if refallele and refallele != allele:
                                        if 0 < float(percentid) < 100:
                                            row += '{} ({:.2f}%),'.format(allele, float(percentid))
                                        else:
                                            row += '{} ({}),'.format(allele, refallele)
                                    else:
                                        # Add the allele and % id to the row (only add the % identity if it is not 100%)
                                        if 0 < float(percentid) < 100:
                                            row += '{} ({:.2f}%),'.format(allele, float(percentid))
                                        else:
                                            row += '{},'.format(allele)
                                    self.referenceprofile[sample.name][gene] = allele
                                except ValueError:
                                    pass
                            # Add a newline
                            row += '\n'
                        #
                        combinedrow += row
                        #
                        combined_header_row += header_row
                        combined_header_row += row
                        if self.analysistype == 'mlst':
                            mlst_dict[genus]['header'] = header_row
                            try:
                                mlst_dict[genus]['combined_row'] += row
                            except KeyError:
                                mlst_dict[genus]['combined_row'] = str()
                                mlst_dict[genus]['combined_row'] += row
                        # Convert the set into a sorted list for JSON serialization
                        sample[self.analysistype].sequencetype = sorted(list(sample[self.analysistype].sequencetype))
                        # If the length of the # of report directories is greater than 1 (script is being run as part of
                        # the assembly pipeline) make a report for each sample
                        if self.pipeline:
                            # Open the report
                            with open(os.path.join(sample[self.analysistype].reportdir,
                                                   '{sn}_{at}.csv'.format(sn=sample.name,
                                                                          at=self.analysistype)), 'w') as report:
                                # Write the row to the report
                                report.write(header_row)
                                report.write(row)
        # Create the report folder
        make_path(self.reportpath)
        # Create the report containing all the data from all samples
        if self.analysistype == 'mlst':
            for genus in mlst_dict:
                if mlst_dict[genus]['combined_row']:
                    with open(os.path.join(self.reportpath, '{at}_{genus}.csv'.format(at=self.analysistype,
                                                                                      genus=genus)), 'w') \
                            as mlstreport:
                        # Add the header
                        mlstreport.write(mlst_dict[genus]['header'])
                        # Write the results to this report
                        mlstreport.write(mlst_dict[genus]['combined_row'])
            with open(os.path.join(self.reportpath,  '{at}.csv'.format(at=self.analysistype)), 'w') \
                    as combinedreport:
                # Write the results to this report
                combinedreport.write(combined_header_row)
        else:
            with open(os.path.join(self.reportpath,  '{at}.csv'.format(at=self.analysistype)), 'w') \
                    as combinedreport:
                # Add the header
                combinedreport.write(header_row)
                # Write the results to this report
                combinedreport.write(combinedrow)

    def report_parse(self):
        """
        If the pipeline has previously been run on these data, instead of reading through the results, parse the
        report instead
        """
        # Initialise lists
        report_strains = list()
        genus_list = list()
        if self.analysistype == 'mlst':
            for sample in self.runmetadata.samples:
                # Extract the closest reference genus
                try:
                    genus = sample.general.closestrefseqgenus
                except AttributeError:
                    try:
                        genus = sample.general.referencegenus
                    except AttributeError:
                        genus = 'ND'
                genus_list.append(genus)
        # Read in the report
        if self.analysistype == 'mlst':
            for genus in genus_list:
                try:
                    report_name = os.path.join(self.reportpath, '{at}_{genus}.csv'.format(at=self.analysistype,
                                                                                          genus=genus))
                    report_strains = self.report_read(report_strains=report_strains,
                                                      report_name=report_name)
                except FileNotFoundError:
                    report_name = self.report
                    report_strains = self.report_read(report_strains=report_strains,
                                                      report_name=report_name)
        else:
            report_name = self.report
            report_strains = self.report_read(report_strains=report_strains,
                                              report_name=report_name)
        # Populate strains not in the report with 'empty' GenObject with appropriate attributes
        for sample in self.runmetadata.samples:
            if sample.name not in report_strains:
                setattr(sample, self.analysistype, GenObject())
                sample[self.analysistype].sequencetype = 'ND'
                sample[self.analysistype].matches = 0
                sample[self.analysistype].results = dict()
                sample[self.analysistype].combined_metadata_results = dict()
            else:
                sample[self.analysistype].sequencetype = sorted(list(sample[self.analysistype].sequencetype))

    def report_read(self, report_strains, report_name):
        """
        If the report already exists, parse the values from the report, and populate the metadata object with these
        values
        :param report_strains: type LIST: Empty list of strains present in the report
        :param report_name: type STR: Name and absolute path of the report
        :return report_strains: Updated list of strains present in the report
        """
        # Initialise variables to store the header information
        header_dict = dict()
        header_list = list()
        with open(report_name, 'r') as report:
            for line in report:
                # As the report will have a header line for every separate strain, extract this header
                # e.g. Strain,Genus,SequenceType,Matches,adk,fumC,gyrB,icd,mdh,purA,recA
                if line.startswith('Strain'):
                    header_list = line.rstrip().split(',')
                    for i, entry in enumerate(header_list):
                        header_dict[entry] = i
                # Find the outputs for each sample
                for sample in self.runmetadata.samples:
                    if sample.name in line:
                        # List of strains present in the report - will be used for finding strains not in the report
                        report_strains.append(sample.name)
                        # Split the results on commas e.g.:2016-SEQ-1217,Escherichia,2223,7,6,11,5,8,7,8,2
                        results = line.rstrip().split(',')
                        # Create the GenObject
                        if not GenObject.isattr(sample, self.analysistype):
                            setattr(sample, self.analysistype, GenObject())
                        # Populate the attributes
                        try:
                            sample[self.analysistype].sequencetype.add(results[header_dict['SequenceType']])
                        except AttributeError:
                            sample[self.analysistype].sequencetype = set()
                            sample[self.analysistype].sequencetype.add(results[header_dict['SequenceType']])
                        try:
                            sample[self.analysistype].matches = int(results[header_dict['Matches']])
                        except (ValueError, TypeError):
                            sample[self.analysistype].matches = results[header_dict['Matches']]
                        # Initialise a dictionary to store the typing data
                        sample[self.analysistype].results = dict()
                        sample[self.analysistype].combined_metadata_results = dict()
                        # Iterate through the gene:allele combination present in header[index]: results[index]
                        # The header has genes starting in the 5th column, so start the list splice there
                        iterator = header_dict['Matches'] + 1
                        for allele in results[iterator:]:
                            # Initialise the gene variable
                            gene = header_list[iterator]
                            # Ensure that there is an allele
                            if allele:
                                # Recreate the gene_allele format present in the standard .results attribute
                                # e.g. mdh_5
                                # .split(' ')[0]
                                gene_allele = '{gene}_{allele}'.format(gene=gene,
                                                                       allele=allele.split(' (')[0])
                                # Set the percent identity for this gene_allele combination to 100%
                                sample[self.analysistype].results[gene_allele] = 100
                                sample[self.analysistype].combined_metadata_results[gene_allele] = 100
                                iterator += 1
        return report_strains

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
        # Initialise variables
        self.commit = str(pipelinecommit)
        self.starttime = startingtime
        self.homepath = scriptpath
        # Define variables based on supplied arguments
        self.path = os.path.join(args.path)
        assert os.path.isdir(self.path), 'Supplied path is not a valid directory {path}'.format(path=self.path)
        try:
            self.sequencepath = os.path.join(args.sequencepath)
        except AttributeError:
            self.sequencepath = self.path
        assert os.path.isdir(self.sequencepath), 'Sequence path  is not a valid directory {seq_path}' \
            .format(seq_path=self.sequencepath)
        try:
            if pipeline:
                self.targetpath = os.path.join(args.reffilepath, analysistype)
            else:
                self.targetpath = os.path.join(args.reffilepath)
        except AttributeError:
            self.targetpath = os.path.join(args.targetpath)
        if pipeline:
            if 'mlst' in self.targetpath.lower():
                if 'rmlst' in self.targetpath.lower():
                    self.targetpath = os.path.join(os.path.dirname(self.targetpath), 'rMLST')
                elif 'mlst' in self.targetpath.lower():
                    self.targetpath = os.path.join(os.path.dirname(self.targetpath), 'MLST')
        assert os.path.isdir(self.targetpath), 'Target path is not a valid directory {target_path}' \
            .format(target_path=self.targetpath)
        self.reportpath = os.path.join(self.path, 'reports')
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
        # Set the custom cutoff value
        self.cutoff = float(cutoff)
        self.logfile = args.logfile
        try:
            self.averagedepth = int(args.averagedepth)
        except AttributeError:
            self.averagedepth = 10
        try:
            self.copy = args.copy
        except AttributeError:
            self.copy = False
        try:
            self.runmetadata = args.runmetadata
        except AttributeError:
            # Create the objects to be used in the analyses
            objects = Objectprep(self)
            objects.objectprep()
            self.runmetadata = objects.samples
        # Use the argument for the number of threads to use, or default to the number of cpus in the system
        try:
            self.cpus = int(args.cpus)
        except AttributeError:
            self.cpus = multiprocessing.cpu_count()
        try:
            self.threads = int(self.cpus / len(self.runmetadata.samples)) if self.cpus / len(self.runmetadata.samples) \
                                                                             > 1 else 1
        except TypeError:
            self.threads = self.cpus
        self.taxonomy = {'Escherichia': 'coli', 'Listeria': 'monocytogenes', 'Salmonella': 'enterica'}
        #
        self.pipeline = pipeline
        if analysistype.lower() == 'mlst':
            self.analysistype = 'mlst'
        elif analysistype.lower() == 'rmlst':
            self.analysistype = 'rmlst'
        else:
            sys.stderr.write('Please ensure that you specified a valid option for the analysis type. You entered {}. '
                             'The only acceptable options currently are mlst and rmlst.'.format(args.analysistype))
            quit()
        self.plusdict = dict()
        self.matchdict = dict()
        self.bestdict = defaultdict(make_dict)
        self.bestmatch = defaultdict(int)
        self.mlstseqtype = defaultdict(make_dict)
        self.resultprofile = defaultdict(make_dict)
        self.referenceprofile = defaultdict(make_dict)
        self.report = os.path.join(self.reportpath, self.analysistype + '.csv')
        self.meta_dict = dict()
        self.meta_headers = list()
        self.listeria_serogroup_dict = {
            'IIb': [3, 5, 39, 59, 66, 87, 117, 287, 489, 517, 576, 617],
            'IVb': [1, 2, 4, 6, 55, 63, 64, 67, 73, 145, 257, 290, 291, 347, 397, 454, 458, 495],
            'IIa': [7, 8, 12, 21, 26, 31, 98, 101, 103, 109, 121, 155, 177, 398, 403, 451, 466, 519, 521],
            'IIc': [9, 122, 356],
            'spp.': [71, 202, 467, 488]
        }


if __name__ == '__main__':
    # Get the current commit of the pipeline from git
    # Extract the path of the current script from the full path + file name
    homepath = os.path.split(os.path.abspath(__file__))[0]
    # Find the commit of the script by running a command to change to the directory containing the script and run
    # a git command to return the short version of the commit hash
    commit = subprocess.Popen('cd {} && git rev-parse --short HEAD'.format(homepath),
                              shell=True, stdout=subprocess.PIPE).communicate()[0].rstrip()
    # Parser for arguments
    parser = ArgumentParser(description='Perform modelling of parameters for GeneSipping')
    parser.add_argument('path',
                        help='Specify input directory')
    parser.add_argument('-s', '--sequencepath',
                        required=True,
                        help='Path of .fastq(.gz) files to process.')
    parser.add_argument('-t', '--targetpath',
                        required=True,
                        help='Path of target files to process.')
    parser.add_argument('-n', '--numthreads',
                        help='Number of threads. Default is the number of cores in the system')
    parser.add_argument('-b', '--bcl2fastq',
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
    parser.add_argument('-u', '--customcutoffs',
                        default=1.0,
                        help='Custom cutoff values')
    parser.add_argument('-a', '--analysistype',
                        required=True,
                        help='Specify analysis type: mlst or rmlst')
    parser.add_argument('-C', '--copy',
                        action='store_true',
                        help='Normally, the program will create symbolic links of the files into the sequence path, '
                             'however, the are occasions when it is necessary to copy the files instead')
    SetupLogging()
    # Get the arguments into an object
    arguments = parser.parse_args()
    arguments.pipeline = False
    arguments.logfile = os.path.join(arguments.path, 'logfile')
    # Define the start time
    start = time.time()

    # Run the script
    mlst_sippr = GeneSippr(args=arguments,
                           pipelinecommit=commit,
                           startingtime=start,
                           scriptpath=homepath,
                           analysistype=arguments.analysistype,
                           cutoff=arguments.customcutoffs,
                           pipeline=arguments.pipeline)
    mlst_sippr.runner()
    # Print an exit statement
    logging.info('Analyses complete')
