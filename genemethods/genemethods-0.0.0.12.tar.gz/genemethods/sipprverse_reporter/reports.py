#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import make_path, MetadataObject
from Bio.Sequencing.Applications import SamtoolsFaidxCommandline
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC
from Bio.Seq import Seq
from Bio import SeqIO
from io import StringIO
import seaborn as sns
from glob import glob
import pandas as pd
import operator
import logging
import numpy
import os
import re


__author__ = 'adamkoziol'


class Reports(object):

    def reporter(self, analysistype='genesippr'):
        """
        Creates a report of the genesippr results
        :param analysistype: The variable to use when accessing attributes in the metadata object
        """
        logging.info('Creating {} report'.format(analysistype))
        # Create a dictionary to link all the genera with their genes
        genusgenes = dict()
        # The organism-specific targets are in .tfa files in the target path
        targetpath = str()
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                targetpath = sample[analysistype].targetpath
        for organismfile in glob(os.path.join(targetpath, '*.tfa')):
            organism = os.path.splitext(os.path.basename(organismfile))[0]
            # Use BioPython to extract all the gene names from the file
            for record in SeqIO.parse(open(organismfile), 'fasta'):
                # Append the gene names to the genus-specific list
                try:
                    genusgenes[organism].add(record.id.split('_')[0])
                except (KeyError, IndexError):
                    genusgenes[organism] = set()
                    genusgenes[organism].add(record.id.split('_')[0])
        # Determine from which genera the gene hits were sourced
        for sample in self.runmetadata.samples:
            # Initialise the list to store the genera
            sample[analysistype].targetgenera = list()
            if sample.general.bestassemblyfile != 'NA':
                for organism in genusgenes:
                    # Iterate through all the genesippr hits and attribute each gene to the appropriate genus
                    for gene in sample[analysistype].results:
                        # If the gene name is in the genes from that organism, add the genus name to the list of
                        # genera found in the sample
                        if gene.split('_')[0] in genusgenes[organism]:
                            if organism not in sample[analysistype].targetgenera:
                                sample[analysistype].targetgenera.append(organism)
        # Create the path in which the reports are stored
        make_path(self.reportpath)
        # The report will have every gene for all genera in the header
        header = 'Strain,Genus,{},\n'.format(','.join(self.genelist))
        data = str()
        with open(os.path.join(self.reportpath, analysistype + '.csv'), 'w') as report:
            for sample in self.runmetadata.samples:
                sample[analysistype].report_output = list()
                if sample.general.bestassemblyfile != 'NA':
                    # Add the genus/genera found in the sample
                    data += '{},{},'.format(sample.name, ';'.join(sample[analysistype].targetgenera))
                    best_dict = dict()
                    if sample[analysistype].results:
                        gene_check = list()
                        # Find the best match for all the hits
                        for target, pid in sample[analysistype].results.items():
                            gene_name = target.split('_')[0]
                            for gene in self.genelist:
                                # If the key matches a gene in the list of genes
                                if gene == gene_name:
                                    # If the percent identity is better, update the dictionary
                                    try:
                                        if float(pid) > best_dict[gene]:
                                            best_dict[gene] = float(pid)
                                    except KeyError:
                                        best_dict[gene] = float(pid)
                        for gene in self.genelist:
                            # If the gene was not found in the sample, print an empty cell in the report
                            try:
                                best_dict[gene]
                            except KeyError:
                                data += ','
                            # Print the required information for the gene
                            for name, identity in sample[analysistype].results.items():
                                if name.split('_')[0] == gene and gene not in gene_check:
                                    data += '{pid}%'.format(pid=best_dict[gene])
                                    try:
                                        if not sample.general.trimmedcorrectedfastqfiles[0].endswith('.fasta'):
                                            data += ' ({avgd} +/- {std}),'\
                                                .format(avgd=sample[analysistype].avgdepth[name],
                                                        std=sample[analysistype].standarddev[name])
                                        else:
                                            data += ','
                                    except IndexError:
                                        data += ','
                                    gene_check.append(gene)
                                    # Add the simplified results to the object - used in the assembly pipeline report
                                    sample[analysistype].report_output.append(gene)
                        # Add a newline after each sample
                        data += '\n'
                    # Add a newline if the sample did not have any gene hits
                    else:
                        data += '\n'
            # Write the header and data to file
            report.write(header)
            report.write(data)

    def genusspecific(self, analysistype='genesippr'):
        """
        Creates simplified genus-specific reports. Instead of the % ID and the fold coverage, a simple +/- scheme is
        used for presence/absence
        :param analysistype: The variable to use when accessing attributes in the metadata object
        """
        # Dictionary to store all the output strings
        results = dict()
        for genus, genelist in self.genedict.items():
            # Initialise the dictionary with the appropriate genus
            results[genus] = str()
            for sample in self.runmetadata.samples:
                try:
                    # Find the samples that match the current genus - note that samples with multiple hits will be
                    # represented in multiple outputs
                    if genus in sample[analysistype].targetgenera:
                        # Populate the results string with the sample name
                        results[genus] += '{},'.format(sample.name)
                        # Iterate through all the genes associated with this genus. If the gene is in the current
                        # sample, add a + to the string, otherwise, add a -
                        for gene in genelist:
                            if gene.lower() in [target[0].lower().split('_')[0] for target in
                                                sample[analysistype].results.items()]:
                                results[genus] += '+,'
                            else:
                                results[genus] += '-,'
                        results[genus] += '\n'
                # If the sample is missing the targetgenera attribute, then it is ignored for these reports
                except AttributeError:
                    pass
        # Create and populate the genus-specific reports
        for genus, resultstring in results.items():
            # Only create the report if there are results for the current genus
            if resultstring:
                with open(os.path.join(self.reportpath, '{}_genesippr.csv'.format(genus)), 'w') as genusreport:
                    # Write the header to the report - Strain plus add the genes associated with the genus
                    genusreport.write('Strain,{}\n'.format(','.join(self.genedict[genus])))
                    # Write the results to the report
                    genusreport.write(resultstring)

    def gdcsreporter(self, analysistype='GDCS'):
        """
        Creates a report of the GDCS results
        :param analysistype: The variable to use when accessing attributes in the metadata object
        """
        logging.info('Creating {} report'.format(analysistype))
        # Initialise list to store all the GDCS genes, and genera in the analysis
        gdcs = list()
        genera = list()
        for sample in self.runmetadata.samples:
            if sample.general.bestassemblyfile != 'NA':
                if os.path.isdir(sample[analysistype].targetpath):
                    # Update the fai dict with all the genes in the analysis, rather than just those with baited hits
                    self.gdcs_fai(sample)
                    sample[analysistype].createreport = True
                    # Determine which genera are present in the analysis
                    if sample.general.closestrefseqgenus not in genera:
                        genera.append(sample.general.closestrefseqgenus)
                    try:
                        # Add all the GDCS genes to the list
                        for gene in sorted(sample[analysistype].faidict):
                            if gene not in gdcs:
                                gdcs.append(gene)
                    except AttributeError:
                        sample[analysistype].createreport = False
                else:
                    sample[analysistype].createreport = False
            else:
                sample[analysistype].createreport = False
                sample.general.incomplete = True
        header = 'Strain,Genus,Matches,MeanCoverage,Pass/Fail,{},\n'.format(','.join(gdcs))
        data = str()
        with open(os.path.join(self.reportpath, '{}.csv'.format(analysistype)), 'w') as report:
            # Sort the samples in the report based on the closest refseq genus e.g. all samples with the same genus
            # will be grouped together in the report
            for genus in genera:
                for sample in self.runmetadata.samples:
                    if sample.general.closestrefseqgenus == genus:
                        if sample[analysistype].createreport:
                            sample[analysistype].totaldepth = list()
                            # Add the sample to the report if it matches the current genus
                            # if genus == sample.general.closestrefseqgenus:
                            data += '{},{},'.format(sample.name, genus)
                            # Initialise a variable to store the number of GDCS genes were matched
                            count = 0
                            # As I want the count to be in the report before all the gene results, this string will
                            # store the specific sample information, and will be added to data once count is known
                            specific = str()
                            for gene in gdcs:
                                # As there are different genes present in the GDCS databases for each organism of
                                # interest, genes that did not match because they're absent in the specific database are
                                # indicated using an X
                                if gene not in [result for result in sample[analysistype].faidict]:
                                    specific += 'X,'
                                else:
                                    try:
                                        # Report the necessary information for each gene result
                                        identity = sample[analysistype].results[gene]
                                        specific += '{}% ({} +/- {}),'\
                                            .format(identity, sample[analysistype].avgdepth[gene],
                                                    sample[analysistype].standarddev[gene])
                                        sample[analysistype].totaldepth.append(
                                            float(sample[analysistype].avgdepth[gene]))
                                        count += 1
                                    # If the gene was missing from the results attribute, add a - to the cell
                                    except (KeyError, AttributeError):
                                        sample.general.incomplete = True
                                        specific += '-,'
                            # Calculate the mean depth of the genes and the standard deviation
                            sample[analysistype].mean = numpy.mean(sample[analysistype].totaldepth)
                            sample[analysistype].stddev = numpy.std(sample[analysistype].totaldepth)
                            # Determine whether the sample pass the necessary quality criteria:
                            # Pass, all GDCS, mean coverage greater than 20X coverage;
                            # ?: Indeterminate value;
                            # -: Fail value
                            # Allow one missing GDCS to still be considered a pass
                            if count >= len(sample[analysistype].faidict) - 1:
                                if sample[analysistype].mean > 20:
                                    quality = '+'
                                else:
                                    quality = '?'
                                    sample.general.incomplete = True
                            else:
                                quality = '-'
                                sample.general.incomplete = True
                            # Add the count, mean depth with standard deviation, the pass/fail determination,
                            #  and the total number of GDCS genes as well as the results
                            data += '{hits}/{total},{mean} +/- {std},{fail},{gdcs}\n'\
                                .format(hits=str(count),
                                        total=len(sample[analysistype].faidict),
                                        mean='{:.2f}'.format(sample[analysistype].mean),
                                        std='{:.2f}'.format(sample[analysistype].stddev),
                                        fail=quality,
                                        gdcs=specific)
                        # # Any samples with a best assembly of 'NA' are considered incomplete.
                        # else:
                        #     data += '{},{},,,-\n'.format(sample.name, sample.general.closestrefseqgenus)
                        #     sample.general.incomplete = True
                    elif sample.general.closestrefseqgenus == 'NA':
                        data += '{}\n'.format(sample.name)
                        sample.general.incomplete = True
            # Write the header and data to file
            report.write(header)
            report.write(data)

    @staticmethod
    def gdcs_fai(sample, analysistype='GDCS'):
        """
        GDCS analyses need to use the .fai file supplied in the targets folder rather than the one created following
        reverse baiting
        :param sample: sample object
        :param analysistype: current analysis being performed
        """
        try:
            # Find the .fai file in the target path
            sample[analysistype].faifile = glob(os.path.join(sample[analysistype].targetpath, '*.fai'))[0]
        except IndexError:
            target_file = glob(os.path.join(sample[analysistype].targetpath, '*.fasta'))[0]
            samindex = SamtoolsFaidxCommandline(reference=target_file)
            map(StringIO, samindex(cwd=sample[analysistype].targetpath))
            sample[analysistype].faifile = glob(os.path.join(sample[analysistype].targetpath, '*.fai'))[0]
        # Get the fai file into a dictionary to be used in parsing results
        try:
            with open(sample[analysistype].faifile, 'r') as faifile:
                for line in faifile:
                    data = line.split('\t')
                    try:
                        sample[analysistype].faidict[data[0]] = int(data[1])
                    except KeyError:
                        sample[analysistype].faidict = dict()
                        sample[analysistype].faidict[data[0]] = int(data[1])
        except FileNotFoundError:
            pass

    def sixteensreporter(self, analysistype='sixteens_full'):
        """
        Creates a report of the results
        :param analysistype: The variable to use when accessing attributes in the metadata object
        """
        # Create the path in which the reports are stored
        make_path(self.reportpath)
        # Initialise the header and data strings
        header = 'Strain,Gene,PercentIdentity,Genus,FoldCoverage\n'
        data = ''
        with open(os.path.join(self.reportpath, analysistype + '.csv'), 'w') as report:
            with open(os.path.join(self.reportpath, analysistype + '_sequences.fa'), 'w') as sequences:
                for sample in self.runmetadata.samples:
                    try:
                        # Select the best hit of all the full-length 16S genes mapped
                        sample[analysistype].besthit = sorted(sample[analysistype].results.items(),
                                                              key=operator.itemgetter(1), reverse=True)[0][0]
                        # Add the sample name to the data string
                        data += sample.name + ','
                        # Find the record that matches the best hit, and extract the necessary values to be place in the
                        # data string
                        for name, identity in sample[analysistype].results.items():
                            if name == sample[analysistype].besthit:
                                data += '{},{},{},{}\n'.format(name, identity, sample[analysistype].genus,
                                                               sample[analysistype].avgdepth[name])
                                # Create a FASTA-formatted sequence output of the 16S sequence
                                record = SeqRecord(Seq(sample[analysistype].sequences[name],
                                                       IUPAC.unambiguous_dna),
                                                   id='{}_{}'.format(sample.name, '16S'),
                                                   description='')
                                SeqIO.write(record, sequences, 'fasta')
                    except (KeyError, IndexError):
                        data += '{}\n'.format(sample.name)
            # Write the results to the report
            report.write(header)
            report.write(data)

    def confindr_reporter(self, analysistype='confindr'):
        """
        Creates a final report of all the ConFindr results
        """
        # Initialise the data strings
        data = 'Strain,Genus,NumContamSNVs,ContamStatus,PercentContam,PercentContamSTD\n'
        with open(os.path.join(self.reportpath, analysistype + '.csv'), 'w') as report:
            # Iterate through all the results
            for sample in self.runmetadata.samples:
                data += '{str},{genus},{numcontamsnv},{status},{pc},{pcs}\n'.format(
                    str=sample.name,
                    genus=sample.confindr.genus,
                    numcontamsnv=sample.confindr.num_contaminated_snvs,
                    status=sample.confindr.contam_status,
                    pc=sample.confindr.percent_contam,
                    pcs=sample.confindr.percent_contam_std
                )
            # Write the string to the report
            report.write(data)

    def methodreporter(self):
        """
        Create final reports collating results from all the individual iterations through the method pipeline
        """
        # Ensure that the analyses are set to complete
        self.analysescomplete = True
        # Reset the report path to original value
        self.reportpath = os.path.join(self.path, 'reports')
        # Clear the runmetadata - it will be populated with all the metadata from completemetadata
        self.runmetadata = MetadataObject()
        self.runmetadata.samples = list()
        # As the samples were entered into self.completemetadata depending on when they passed the quality threshold,
        # this list is not ordered numerically/alphabetically like the original runmetadata. Reset the order.
        for strain in self.samples:
            for sample in self.completemetadata:
                if sample.name == strain:
                    # Append the sample to the ordered list of objects
                    self.runmetadata.samples.append(sample)
        # Create the reports
        self.reporter()
        self.genusspecific()
        self.sixteensreporter()
        self.gdcsreporter()
        self.confindr_reporter()

    def __init__(self, inputobject):
        self.starttime = inputobject.starttime
        try:
            self.samples = inputobject.samples
        except AttributeError:
            self.samples = inputobject.runmetadata.samples
        try:
            self.completemetadata = inputobject.completemetadata
        except AttributeError:
            self.completemetadata = inputobject.runmetadata.samples
        self.path = inputobject.path
        try:
            self.analysescomplete = inputobject.analysescomplete
        except AttributeError:
            self.analysescomplete = True
        self.reportpath = inputobject.reportpath
        self.runmetadata = MetadataObject()
        try:
            self.runmetadata.samples = inputobject.runmetadata.samples
        except AttributeError:
            self.runmetadata.samples = inputobject.runmetadata
        # List and dictionary containing genera of interest, and corresponding genus-specific probe names
        self.genelist = ['asp-Cc', 'cdtB-Cj', 'csrA-Cj', 'hipO-Cj',
                         'aggR', 'eae', 'hlyAEc', 'O26', 'O45', 'O103', 'O111', "O121", 'O145', 'O157',
                         'VT1', 'VT2', 'VT2f', 'uidA',
                         'hlyALm', 'IGS', 'inlJ',
                         'invA', 'stn',
                         'entA', 'entB', 'entC', 'entD', 'et_a', 'et_b', 'tsst',
                         'groEL', 'r72h', 'tdh', 'tlh', 'trh',
                         'gyrB-Bc1', 'gyrB-Bc2', 'gyrB-Bt', 'Bct16S', 'hblA', 'hblB', 'hblC', 'hblD', 'nheA',
                         'nheB', 'nheC', 'bceT', 'sph', 'cytK', 'cry1', 'cry2', 'cry4', 'cry9', 'cry10', 'cry11'
                         ]
        self.genedict = {'Campylobacter': self.genelist[:4],
                         'Escherichia': self.genelist[4:18],
                         'Listeria': self.genelist[18:21],
                         'Salmonella': self.genelist[21:23],
                         'Staphylococcus': self.genelist[23:30],
                         'Vibrio': self.genelist[30:35],
                         'Bacillus': self.genelist[35:]
                         }


class ReportImage(object):

    def main(self):
        """
        Run the methods required to create the genesippr report summary image
        """
        self.dataframe_setup()
        self.figure_populate(self.outputfolder,
                             self.image_report,
                             self.header_list,
                             self.samples,
                             'genesippr',
                             'report',
                             fail=self.fail)

    def data_sanitise(self, inputstring, header=None):
        """
        Format the data to be consistent with heatmaps
        :param inputstring: string containing data to be formatted
        :param header: class of the data - certain categories have specific formatting requirements
        :return: the formatted output string
        """
        if str(inputstring) == 'nan':
            outputstring = 0
        elif '%' in str(inputstring):
            group = re.findall('(\d+)\..+', str(inputstring))
            outputstring = group[0]
        elif header == 'Pass/Fail':
            if str(inputstring) == '+':
                outputstring = '100'
            else:
                outputstring = -100
                self.fail = True
        elif header == 'ContamStatus':
            if str(inputstring) == 'Clean':
                outputstring = '100'
            else:
                outputstring = -100
                self.fail = True
        elif header == 'MeanCoverage':
            cov = float(str(inputstring).split(' ')[0])
            if cov >= 20:
                outputstring = 100
            else:
                outputstring = -100
                self.fail = True
        else:
            outputstring = str(inputstring)
        return outputstring

    def dataframe_setup(self):
        """
        Set-up a report to store the desired header: sanitized string combinations
        """
        # Initialise a dictionary to store the sanitized headers and strings
        genesippr_dict = dict()
        # Try to open all the reports - use pandas to extract the results from any report that exists
        try:
            sippr_matrix = pd.read_csv(os.path.join(self.reportpath, 'genesippr.csv'),
                                       delimiter=',', index_col=0).T.to_dict()
        except FileNotFoundError:
            sippr_matrix = dict()
        try:
            conf_matrix = pd.read_csv(os.path.join(self.reportpath, 'confindr_report.csv'),
                                      delimiter=',', index_col=0).T.to_dict()
        except FileNotFoundError:
            conf_matrix = dict()
        try:
            gdcs_matrix = pd.read_csv(os.path.join(self.reportpath, 'GDCS.csv'),
                                      delimiter=',', index_col=0).T.to_dict()
        except FileNotFoundError:
            gdcs_matrix = dict()
        # Populate the header:sanitized string dictionary with results from all strains
        for sample in self.metadata:
            genesippr_dict[sample.name] = dict()
            try:
                genesippr_dict[sample.name]['eae'] = self.data_sanitise(sippr_matrix[sample.name]['eae'])
            except KeyError:
                genesippr_dict[sample.name]['eae'] = 0
            try:
                genesippr_dict[sample.name]['hlyAEc'] = self.data_sanitise(sippr_matrix[sample.name]['hlyAEc'])
            except KeyError:
                genesippr_dict[sample.name]['hlyAEc'] = 0
            try:
                genesippr_dict[sample.name]['VT1'] = self.data_sanitise(sippr_matrix[sample.name]['VT1'])
            except KeyError:
                genesippr_dict[sample.name]['VT1'] = 0
            try:
                genesippr_dict[sample.name]['VT2'] = self.data_sanitise(sippr_matrix[sample.name]['VT2'])
            except KeyError:
                genesippr_dict[sample.name]['VT2'] = 0
            try:
                genesippr_dict[sample.name]['hlyALm'] = self.data_sanitise(sippr_matrix[sample.name]['hlyALm'])
            except KeyError:
                genesippr_dict[sample.name]['hlyALm'] = 0
            try:
                genesippr_dict[sample.name]['IGS'] = self.data_sanitise(sippr_matrix[sample.name]['IGS'])
            except KeyError:
                genesippr_dict[sample.name]['IGS'] = 0
            try:
                genesippr_dict[sample.name]['inlJ'] = self.data_sanitise(sippr_matrix[sample.name]['inlJ'])
            except KeyError:
                genesippr_dict[sample.name]['inlJ'] = 0
            try:
                genesippr_dict[sample.name]['invA'] = self.data_sanitise(sippr_matrix[sample.name]['invA'])
            except KeyError:
                genesippr_dict[sample.name]['invA'] = 0
            try:
                genesippr_dict[sample.name]['stn'] = self.data_sanitise(sippr_matrix[sample.name]['stn'])
            except KeyError:
                genesippr_dict[sample.name]['stn'] = 0
            try:
                genesippr_dict[sample.name]['GDCS'] = self.data_sanitise(gdcs_matrix[sample.name]['Pass/Fail'],
                                                                         header='Pass/Fail')
            except KeyError:
                genesippr_dict[sample.name]['GDCS'] = 0
            try:
                genesippr_dict[sample.name]['Contamination'] = self.data_sanitise(
                    conf_matrix[sample.name]['ContamStatus'], header='ContamStatus')
            except KeyError:
                genesippr_dict[sample.name]['Contamination'] = 0
            try:
                genesippr_dict[sample.name]['Coverage'] = self.data_sanitise(
                    gdcs_matrix[sample.name]['MeanCoverage'], header='MeanCoverage')
            except KeyError:
                genesippr_dict[sample.name]['Coverage'] = 0
        # Create a report from the header: sanitized string dictionary to be used in the creation of the report image
        with open(self.image_report, 'w') as csv:
            data = '{}\n'.format(','.join(self.header_list))
            for strain in sorted(genesippr_dict):
                data += '{str},'.format(str=strain)
                for header in self.header_list[1:]:
                    data += '{value},'.format(value=genesippr_dict[strain][header])

                data = data.rstrip(',')
                data += '\n'
            csv.write(data)

    @staticmethod
    def figure_populate(outputpath, csv, xlabels, ylabels, analysistype, description, fail=False):
        """
        Create the report image from the summary report created in self.dataframesetup
        :param outputpath: Path in which the outputs are to be created
        :param csv: Name of the report file from which data are to be extracted
        :param xlabels: List of all the labels to use on the x-axis
        :param ylabels: List of all the labels to use on the y-axis
        :param analysistype: String of the analysis type
        :param description: String describing the analysis: set to either template for the empty heatmap created prior
        to analyses or report for normal functionality
        :param fail: Boolean of whether any samples have failed the quality checks - used for determining the palette
        """
        # Create a data frame from the summary report
        df = pd.read_csv(
            os.path.join(outputpath, csv),
            delimiter=',',
            index_col=0)
        # Set the palette appropriately - 'template' uses only grey
        if description == 'template':
            cmap = ['#a0a0a0']
        # 'fail' uses red (fail), grey (not detected), and green (detected/pass)
        elif fail:
            cmap = ['#ff0000', '#a0a0a0', '#00cc00']
        # Otherwise only use grey (not detected) and green (detected/pass)
        else:
            cmap = ['#a0a0a0', '#00cc00']
        # Use seaborn to create a heatmap of the data
        plot = sns.heatmap(df,
                           cbar=False,
                           linewidths=.5,
                           cmap=cmap)
        # Move the x-axis to the top of the plot
        plot.xaxis.set_ticks_position('top')
        # Remove the y-labels
        plot.set_ylabel('')
        # Set the x-tick labels as a slice of the x-labels list (first entry is not required, as it makes the
        # report image look crowded. Rotate the x-tick labels 90 degrees
        plot.set_xticklabels(xlabels[1:], rotation=90)
        # Set the y-tick labels from the supplied list
        plot.set_yticklabels(ylabels, rotation=0)
        # Create the figure
        fig = plot.get_figure()
        # Save the figure in .png format, using the bbox_inches='tight' option to ensure that everything is scaled
        fig.savefig(os.path.join(outputpath, '{at}_{desc}.png'.format(at=analysistype,
                                                                      desc=description)),
                    bbox_inches='tight'
                    )

    def __init__(self, args, analysistype):
        self.samplesheetpath = args.samplesheetpath
        self.reportpath = args.reportpath
        self.header_list = ['Strain', 'eae', 'hlyAEc', 'VT1', 'VT2',
                            'hlyALm', 'IGS', 'inlJ', 'invA', 'stn',
                            'GDCS', 'Contamination', 'Coverage']
        self.outputfolder = os.path.join(args.path, 'reports')
        self.metadata = args.runmetadata.samples
        self.image_report = os.path.join(self.reportpath, 'genesippr_image_report_{}.csv'.format(analysistype))
        self.samples = sorted([sample.name for sample in self.metadata])
        self.genesippr_frame = str()
        self.fail = False
        self.main()
