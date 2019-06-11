#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import combinetargets, GenObject, make_path, run_subprocess
from genemethods.sipprCommon.sippingmethods import Sippr
from genemethods.genesippr.genesippr import GeneSippr
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio import SeqIO
from threading import Thread
from queue import Queue
from glob import glob
import logging
import shutil
import os
__author__ = 'adamkoziol'


class PointSippr(GeneSippr):

    def runner(self):
        """
        Run the necessary methods in the correct order
        """
        logging.info('Starting {} analysis pipeline'.format(self.analysistype))
        # Initialise the GenObject
        for sample in self.runmetadata.samples:
            setattr(sample, self.analysistype, GenObject())
            try:
                sample[self.analysistype].pointfindergenus = self.pointfinder_org_dict[sample.general.referencegenus]
            except KeyError:
                sample[self.analysistype].pointfindergenus = 'ND'
        # Run the raw read mapping
        PointSipping(inputobject=self,
                     cutoff=self.cutoff)
        # Create FASTA files from the raw read matcves
        self.fasta()
        # Run PointFinder on the FASTA files
        self.run_pointfinder()
        # Create summary reports of the PointFinder outputs
        self.parse_pointfinder()

    def fasta(self):
        """
        Create FASTA files of the PointFinder results to be fed into PointFinder
        """
        logging.info('Extracting FASTA sequences matching PointFinder database')
        for sample in self.runmetadata.samples:
            # Ensure that there are sequence data to extract from the GenObject
            if GenObject.isattr(sample[self.analysistype], 'sequences'):
                # Set the name of the FASTA file
                sample[self.analysistype].pointfinderfasta = \
                    os.path.join(sample[self.analysistype].outputdir,
                                 '{seqid}_pointfinder.fasta'.format(seqid=sample.name))
                # Create a list to store all the SeqRecords created
                sequences = list()
                with open(sample[self.analysistype].pointfinderfasta, 'w') as fasta:
                    for gene, sequence in sample[self.analysistype].sequences.items():
                        # Create a SeqRecord using a Seq() of the sequence - both SeqRecord and Seq are from BioPython
                        seq = SeqRecord(seq=Seq(sequence),
                                        id=gene,
                                        name=str(),
                                        description=str())
                        sequences.append(seq)
                    # Write all the SeqRecords to file
                    SeqIO.write(sequences, fasta, 'fasta')

    def run_pointfinder(self):
        """
        Run PointFinder on the FASTA sequences extracted from the raw reads
        """
        logging.info('Running PointFinder on FASTA files')
        for i in range(len(self.runmetadata.samples)):
            # Start threads
            threads = Thread(target=self.pointfinder_threads, args=())
            # Set the daemon to True - something to do with thread management
            threads.setDaemon(True)
            # Start the threading
            threads.start()
        # PointFinder requires the path to the blastn executable
        blast_path = shutil.which('blastn')
        for sample in self.runmetadata.samples:
            # Ensure that the attribute storing the name of the FASTA file has been created
            if GenObject.isattr(sample[self.analysistype], 'pointfinderfasta'):
                sample[self.analysistype].pointfinder_outputs = os.path.join(sample[self.analysistype].outputdir,
                                                                             'pointfinder_outputs')
                # Don't run the analyses if the outputs have already been created
                if not os.path.isfile(os.path.join(sample[self.analysistype].pointfinder_outputs,
                                                   '{samplename}_blastn_results.tsv'.format(samplename=sample.name))):
                    make_path(sample[self.analysistype].pointfinder_outputs)
                    # Create and run the PointFinder system call
                    pointfinder_cmd = \
                        'python -m pointfinder.PointFinder -i {input} -s {species} -p {db_path} -m blastn ' \
                        '-o {output_dir} -m_p {blast_path}'\
                        .format(input=sample[self.analysistype].pointfinderfasta,
                                species=sample[self.analysistype].pointfindergenus,
                                db_path=self.targetpath,
                                output_dir=sample[self.analysistype].pointfinder_outputs,
                                blast_path=blast_path)
                    self.queue.put(pointfinder_cmd)
        self.queue.join()

    def pointfinder_threads(self):
        while True:
            pointfinder_cmd = self.queue.get()
            run_subprocess(pointfinder_cmd)
            self.queue.task_done()

    def populate_summary_dict(self, genus=str(), key=str()):
        """
        :param genus: Non-supported genus to be added to the dictionary
        :param key: section of dictionary to be populated. Supported keys are: prediction, table, and results
        Populate self.summary_dict as required. If the genus is not provided, populate the dictionary for Salmonella
        Escherichia and Campylobacter. If the genus is provided, this genus is non-standard, and an 'empty' profile
        must be created for it
        """
        # If the genus is not provided, generate the generic dictionary
        if not genus:
            # Populate the summary dict
            self.summary_dict = {
                'Salmonella':
                    {
                        'prediction':
                            {
                                'header': 'Strain,Colitsin,Colistin,Spectinomycin,Quinolones,\n',
                                'output': str(),
                                'summary': os.path.join(self.reportpath, 'Salmonella_prediction_summary.csv')
                            },
                        'table':
                            {
                                'header': 'Strain,parE,parC,gyrA,pmrB,pmrA,gyrB,16S_rrsD,23S,\n',
                                'output': str(),
                                'summary': os.path.join(self.reportpath, 'Salmonella_table_summary.csv')
                            },
                        'results':
                            {
                                'header': 'Strain,Genus,Mutation,NucleotideChange,AminoAcidChange,Resistance,PMID,\n',
                                'output': str(),
                                'summary': os.path.join(self.reportpath, 'PointFinder_results_summary.csv')
                            }
                    },
                'Escherichia':
                    {
                        'prediction':
                            {
                                'header': 'Strain,Colistin,GentamicinC,gentamicinC,Streptomycin,Macrolide,Sulfonamide,'
                                          'Tobramycin,Neomycin,Fluoroquinolones,Aminocoumarin,Tetracycline,KanamycinA,'
                                          'Spectinomycin,B-lactamResistance,Paromomycin,Kasugamicin,Quinolones,G418,'
                                          'QuinolonesAndfluoroquinolones,\n',
                                'output': str(),
                                'summary': os.path.join(self.reportpath, 'Escherichia_prediction_summary.csv')
                            },
                        'table':
                            {
                                'header': 'Strain,parE,parC,folP,gyrA,pmrB,pmrA,16S_rrsB,16S_rrsH,gyrB,ampC,'
                                          '16S_rrsC,23S,\n',
                                'output': str(),
                                'summary': os.path.join(self.reportpath, 'Escherichia_table_summary.csv')
                            },
                        'results':
                            {
                                'header': 'Strain,Genus,Mutation,NucleotideChange,AminoAcidChange,Resistance,PMID,\n',
                                'output': str(),
                                'summary': os.path.join(self.reportpath, 'PointFinder_results_summary.csv')
                            }
                    },
                'Campylobacter':
                    {

                        'prediction':
                            {
                                'header': 'Strain,LowLevelIncreaseMIC,AssociatedWithT86Mutations,Macrolide,Quinolone,'
                                          'Streptinomycin,Erythromycin,IntermediateResistance,HighLevelResistance_'
                                          'nalidixic_and_ciprofloxacin,\n',
                                'output': str(),
                                'summary': os.path.join(self.reportpath, 'Campylobacter_prediction_summary.csv')
                            },
                        'table':
                            {
                                'header': 'Strain,L22,rpsL,cmeR,gyrA,23S,\n',
                                'output': str(),
                                'summary': os.path.join(self.reportpath, 'Campylobacter_table_summary.csv')
                            },
                        'results':
                            {
                                'header': 'Strain,Genus,Mutation,NucleotideChange,AminoAcidChange,Resistance,PMID,\n',
                                'output': str(),
                                'summary': os.path.join(self.reportpath, 'PointFinder_results_summary.csv')
                            }
                    }
            }
        else:
            # Create the nesting structure as required
            if genus not in self.summary_dict:
                self.summary_dict[genus] = dict()
            if key not in self.summary_dict[genus]:
                self.summary_dict[genus][key] = dict()
            # The output section is the same regardless of the key
            self.summary_dict[genus][key]['output'] = str()
            # The results report is more generic, and contains all strains, so the header and summary are set to
            # the default values required to generate this report
            if key == 'results':
                self.summary_dict[genus][key]['header'] = \
                    'Strain,Genus,Mutation,NucleotideChange,AminoAcidChange,Resistance,PMID,\n'
                self.summary_dict[genus][key]['summary'] = \
                    os.path.join(self.reportpath, 'PointFinder_results_summary.csv')
            # Create an empty header, and a report with the genus name
            else:
                self.summary_dict[genus][key]['header'] = 'Strain,\n'
                self.summary_dict[genus][key]['summary'] = os.path.join(self.reportpath, '{genus}_{key}_summary.csv'
                                                                        .format(genus=genus,
                                                                                key=key))
                # Remove the report if it exists, as the script will append data to this existing report
                if os.path.isfile(self.summary_dict[genus][key]['summary']):
                    os.remove(self.summary_dict[genus][key]['summary'])

    def parse_pointfinder(self):
        """
        Create summary reports for the PointFinder outputs
        """
        # Create the nested dictionary that stores the necessary values for creating summary reports
        self.populate_summary_dict()
        # Clear out any previous reports
        for organism in self.summary_dict:
            for report in self.summary_dict[organism]:
                try:
                    os.remove(self.summary_dict[organism][report]['summary'])
                except FileNotFoundError:
                    pass
        for sample in self.runmetadata.samples:
            # Find the PointFinder outputs. If the outputs don't exist, create the appropriate entries in the
            # summary dictionary as required
            try:
                self.summary_dict[sample.general.referencegenus]['prediction']['output'] = \
                    glob(os.path.join(sample[self.analysistype].pointfinder_outputs, '{seq}*prediction.txt'
                                      .format(seq=sample.name)))[0]
            except IndexError:
                try:
                    self.summary_dict[sample.general.referencegenus]['prediction']['output'] = str()
                except KeyError:
                    self.populate_summary_dict(genus=sample.general.referencegenus,
                                               key='prediction')
            try:
                self.summary_dict[sample.general.referencegenus]['table']['output'] = \
                    glob(os.path.join(sample[self.analysistype].pointfinder_outputs, '{seq}*table.txt'
                                      .format(seq=sample.name)))[0]
            except IndexError:
                try:
                    self.summary_dict[sample.general.referencegenus]['table']['output'] = str()
                except KeyError:
                    self.populate_summary_dict(genus=sample.general.referencegenus,
                                               key='table')
            try:
                self.summary_dict[sample.general.referencegenus]['results']['output'] = \
                    glob(os.path.join(sample[self.analysistype].pointfinder_outputs, '{seq}*results.tsv'
                                      .format(seq=sample.name)))[0]
            except IndexError:
                try:
                    self.summary_dict[sample.general.referencegenus]['results']['output'] = str()
                except KeyError:
                    self.populate_summary_dict(genus=sample.general.referencegenus,
                                               key='results')
            # Process the predictions
            self.write_report(summary_dict=self.summary_dict,
                              seqid=sample.name,
                              genus=sample.general.referencegenus,
                              key='prediction')
            # Process the results summary
            self.write_report(summary_dict=self.summary_dict,
                              seqid=sample.name,
                              genus=sample.general.referencegenus,
                              key='results')

            # Process the table summary
            self.write_table_report(summary_dict=self.summary_dict,
                                    seqid=sample.name,
                                    genus=sample.general.referencegenus)

    @staticmethod
    def write_report(summary_dict, seqid, genus, key):
        """
        Parse the PointFinder outputs, and write the summary report for the current analysis type
        :param summary_dict: nested dictionary containing data such as header strings, and paths to reports
        :param seqid: name of the strain,
        :param genus: MASH-calculated genus of current isolate
        :param key: current result type. Options are 'prediction', and 'results'
        """
        # Set the header string if the summary report doesn't already exist
        if not os.path.isfile(summary_dict[genus][key]['summary']):
            header_string = summary_dict[genus][key]['header']
        else:
            header_string = str()
        summary_string = str()
        try:
            # Read in the predictions
            with open(summary_dict[genus][key]['output'], 'r') as outputs:
                # Skip the header
                next(outputs)
                for line in outputs:
                    # Skip empty lines
                    if line != '\n':
                        # When processing the results outputs, add the seqid to the summary string
                        if key == 'results':
                            summary_string += '{seq},{genus},'.format(seq=seqid,
                                                                      genus=genus)
                        # Clean up the string before adding it to the summary string - replace commas
                        # with semi-colons, and replace tabs with commas
                        summary_string += line.replace(',', ';').replace('\t', ',')
            # Ensure that there were results to report
            if summary_string:
                if not summary_string.endswith('\n'):
                    summary_string += '\n'
            else:
                if key == 'results':
                    summary_string += '{seq},{genus}\n'.format(seq=seqid,
                                                               genus=genus)
                else:
                    summary_string += '{seq}\n'.format(seq=seqid)
            # Write the summaries to the summary file
            with open(summary_dict[genus][key]['summary'], 'a+') as summary:
                # Write the header if necessary
                if header_string:
                    summary.write(header_string)
                summary.write(summary_string)
        # Add the strain information If no FASTA file could be created by reference mapping
        except FileNotFoundError:
            # Extract the length of the header from the dictionary. Subtract two (don't need the strain, or the
            # empty column created by a trailing comma
            header_len = len(summary_dict[genus][key]['header'].split(',')) - 2
            # When processing the results outputs, add the seqid to the summary string
            if key == 'results':
                summary_string += '{seq},{genus}\n'.format(seq=seqid,
                                                           genus=genus)
            # For the prediction summary, populate the summary string with the appropriate number of comma-separated
            # '0' entries
            elif key == 'prediction':
                summary_string += '{seq}{empty}\n'.format(seq=seqid,
                                                          empty=',0' * header_len)
            # Write the summaries to the summary file
            with open(summary_dict[genus][key]['summary'], 'a+') as summary:
                # Write the header if necessary
                if header_string:
                    summary.write(header_string)
                summary.write(summary_string)

    @staticmethod
    def write_table_report(summary_dict, seqid, genus):
        """
        Parse the PointFinder table output, and write a summary report
        :param summary_dict: nested dictionary containing data such as header strings, and paths to reports
        :param seqid: name of the strain,
        :param genus: MASH-calculated genus of current isolate
        """
        # Set the header string if the summary report doesn't already exist
        if not os.path.isfile(summary_dict[genus]['table']['summary']):
            header_string = summary_dict[genus]['table']['header']
        else:
            header_string = str()
        summary_string = '{seq},'.format(seq=seqid)
        try:
            # Read in the predictions
            with open(summary_dict[genus]['table']['output'], 'r') as outputs:
                for header_value in summary_dict[genus]['table']['header'].split(',')[:-1]:
                    for line in outputs:
                        if line.startswith('{hv}\n'.format(hv=header_value)):
                            # Iterate through the lines following the match
                            for subline in outputs:
                                if subline != '\n':
                                    if subline.startswith('Mutation'):
                                        for detailline in outputs:
                                            if detailline != '\n':
                                                summary_string += '{},'.format(detailline.split('\t')[0])
                                            else:
                                                break
                                    else:
                                        summary_string += '{},'.format(
                                            subline.replace(',', ';').replace('\t', ',').rstrip())
                                        break
                                else:
                                    break
                                break
                    # Reset the file iterator to the first line in preparation for the next header
                    outputs.seek(0)
            # Ensure that there were results to report
            if summary_string:
                if not summary_string.endswith('\n'):
                    summary_string += '\n'
                # Write the summaries to the summary file
                with open(summary_dict[genus]['table']['summary'], 'a+') as summary:
                    # Write the header if necessary
                    if header_string:
                        summary.write(header_string)
                    summary.write(summary_string)
        except FileNotFoundError:
            # Write the summaries to the summary file
            with open(summary_dict[genus]['table']['summary'], 'a+') as summary:
                # Extract the length of the header from the dictionary. Subtract two (don't need the strain, or the
                # empty column created by a trailing comma
                header_len = len(summary_dict[genus]['table']['header'].split(',')) - 2
                # Populate the summary strain with the appropriate number of comma-separated 'Gene not found' entries
                summary_string += '{empty}\n'.format(empty='Gene not found,' * header_len)
                # Write the header if necessary
                if header_string:
                    summary.write(header_string)
                summary.write(summary_string)

    def __init__(self, args, pipelinecommit, startingtime, scriptpath, analysistype, cutoff, pipeline, revbait):
        # Dictionary to convert the mash-calculated genus to the pointfinder format
        self.pointfinder_org_dict = {'Campylobacter': 'campylobacter',
                                     'Escherichia': 'e.coli',
                                     'Shigella': 'e.coli',
                                     '‎Mycobacterium': 'tuberculosis',
                                     'Neisseria': 'gonorrhoeae',
                                     'Salmonella': 'salmonella'}
        # Reverse look-up dictionary
        self.rev_org_dict = {'campylobacter': 'Campylobacter',
                             'e.coli': 'Escherichia',
                             'tuberculosis': 'Mycobacterium',
                             'gonorrhoeae': 'Neisseria',
                             'salmonella': 'Salmonella'}
        self.summary_dict = dict()
        self.queue = Queue(maxsize=args.cpus)
        super().__init__(args, pipelinecommit, startingtime, scriptpath, analysistype, cutoff, pipeline, revbait)


class PointSipping(Sippr):

    def targets(self):
        """
        Search the targets folder for FASTA files, create the multi-FASTA file of all targets if necessary, and
        populate objects
        """
        logging.info('Performing analysis with {} targets folder'.format(self.analysistype))
        for sample in self.runmetadata:
            sample[self.analysistype].runanalysis = True
            sample[self.analysistype].targetpath = (os.path.join(self.targetpath,
                                                                 sample[self.analysistype].pointfindergenus))
            # There is a relatively strict databasing scheme necessary for the custom targets. Eventually,
            # there will be a helper script to combine individual files into a properly formatted combined file
            try:
                sample[self.analysistype].baitfile = glob(os.path.join(sample[self.analysistype].targetpath,
                                                                       '*.fasta'))[0]
            # If the fasta file is missing, raise a custom error
            except IndexError:
                # Combine any .tfa files in the directory into a combined targets .fasta file
                fsafiles = glob(os.path.join(sample[self.analysistype].targetpath, '*.fsa'))
                if fsafiles:
                    combinetargets(fsafiles, sample[self.analysistype].targetpath)
                try:
                    sample[self.analysistype].baitfile = glob(os.path.join(sample[self.analysistype].targetpath,
                                                                           '*.fasta'))[0]
                except IndexError as e:
                    # noinspection PyPropertyAccess
                    e.args = [
                        'Cannot find the combined fasta file in {}. Please note that the file must have a '
                        '.fasta extension'.format(sample[self.analysistype].targetpath)]
                    if os.path.isdir(sample[self.analysistype].targetpath):
                        raise
                    else:
                        sample[self.analysistype].runanalysis = False
        for sample in self.runmetadata:
            # Set the necessary attributes
            sample[self.analysistype].outputdir = os.path.join(sample.run.outputdirectory, self.analysistype)
            make_path(sample[self.analysistype].outputdir)
            sample[self.analysistype].logout = os.path.join(sample[self.analysistype].outputdir, 'logout.txt')
            sample[self.analysistype].logerr = os.path.join(sample[self.analysistype].outputdir, 'logerr.txt')
            sample[self.analysistype].baitedfastq = \
                os.path.join(sample[self.analysistype].outputdir,
                             '{at}_targetMatches.fastq.gz'.format(at=self.analysistype))

    def __init__(self, inputobject, cutoff):
        super().__init__(inputobject=inputobject,
                         cutoff=cutoff)
