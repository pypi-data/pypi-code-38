#!/usr/bin/env python

import argparse
import re
import logging
import os
from abc import ABCMeta, abstractmethod
from collections import OrderedDict

__author__ = 'Refael Kohen'

'''
ReportCounts: "Create report of read counts"

Overview: Create report of counts in each step of pipeline for each sample.

Output: csv file with counts of reads in each step (columns) for each sample (rows)

Arguments:
    --pipeline-dir: Working directory of the pipeline
    --output: Name of the output file.
    --samples: Space separator list of the samples names.
    --logFile: (optional) Where the log file should be written.

'''

class StepReport(object):
    __metaclass__ = ABCMeta

    def __init__(self, samples, counts_container, template_counts_file):
        self.step, self.template_counts_file = self.get_step_path(template_counts_file)
        self.samples = samples
        self.counts_container = counts_container
        logging.info('Read counts of step: %s' %self.step)

    @abstractmethod
    def read_sample_counts(self, sample_name):
        pass

    def read_counts(self):
        for sample in self.samples:
            self.read_sample_counts(sample)

    def get_step_path(self, file):
        template_step = os.path.basename(os.path.dirname(file))
        for step_path in os.listdir(os.path.dirname(os.path.dirname(file))):
            if step_path != 'logs' and step_path != '.snakemake' and os.path.isdir(
                    os.path.join(os.path.dirname(os.path.dirname(file)), step_path)):
                for l_file in os.listdir(os.path.join(os.path.dirname(os.path.dirname(file)), step_path)):
                    if template_step[2:] in step_path and os.path.basename(file).replace('%s', '') in l_file:
                        return step_path, os.path.join(os.path.dirname(os.path.dirname(file)), step_path, os.path.basename(file))
        raise IOError("No step in this pipeline or step not run yet")

    def counts_lines(self, sample_name):
        logging.info('Read counts of step: %s sample: %s' %(self.step, sample_name))
        try:
            fh = open(self.template_counts_file %sample_name)
        except (IOError, TypeError):
            logging.info('Step %s did not run yet' %self.step)
            return
        for line in fh:
            yield line
        fh.close()

    def save_counts(self, step, sample, counts):
        try:
            self.counts_container[sample][step] = counts
        except KeyError:
            self.counts_container[sample] = OrderedDict()
            self.counts_container[sample][step] = counts

class CombinedFastqReport(StepReport):
    def __init__(self, samples, root_dir, counts_container):
        template_counts_file = os.path.join(root_dir, '%d_combined_fastq', '%s.txt')
        super(CombinedFastqReport, self).__init__(samples, counts_container, template_counts_file)

    def read_sample_counts(self, sample):
        for line in self.counts_lines(sample):
            if 'Done' in line:#'03/08/2017 17:21:55 Done. 4478144 reads processed.'
                counts = line[line.find('Done')+6:line.find(' reads processed')]
                self.save_counts(self.step, sample, counts)
                return

class CutadaptReport(StepReport):
    def __init__(self, samples, root_dir, counts_container):
        template_counts_file = os.path.join(root_dir, '%d_cutadapt', '%s.cutadapt.txt')
        super(CutadaptReport, self).__init__(samples, counts_container, template_counts_file)

    def read_sample_counts(self, sample):
        for line in self.counts_lines(sample):
            if 'Reads written (passing filters)' in line or 'Pairs written (passing filters)' in line:  # Reads written (passing filters):     4,425,993 (98.8%)
                if 'Reads written (passing filters)' in line:
                    space_index = line.find('Pairs written (passing filters)') + 33
                elif 'Pairs written (passing filters)' in line:
                    space_index = line.find('Pairs written (passing filters)') + 33
                start_index = len(line[space_index:]) - len(line[space_index:].lstrip()) + space_index
                counts = line[start_index:start_index + line[start_index:].find(' (')].replace(',','')
                self.save_counts(self.step, sample, counts)
                return

class Bowtie2MappingReport(StepReport):
    def __init__(self, samples, root_dir, counts_container):
        template_counts_file = os.path.join(root_dir, '%d_mapping', '%s.stat')
        super(Bowtie2MappingReport, self).__init__(samples, counts_container, template_counts_file)

    def read_sample_counts(self, sample):
        for line in self.counts_lines(sample):
            if 'aligned concordantly exactly 1 time' in line:  #'    49443 (20.11%) aligned concordantly exactly 1 time'
                uniquely_counts = re.match("\s+(\d+) \(\d+.\d+\%\) aligned concordantly exactly 1 time", line).group(1)
                self.save_counts(self.step+'_uniquely', sample, uniquely_counts)
            if 'aligned concordantly >1 times' in line:  #'    15490 (6.30%) aligned concordantly >1 times'
                uniquely_counts = re.match("\s+(\d+) \(\d+.\d+\%\) aligned concordantly >1 times", line).group(1)
                self.save_counts(self.step+'_multiple_loci', sample, uniquely_counts)

class FlagstatReport(StepReport):
    # for example: step='%d_process_alignment', step_name='rm_dup', file_name='%s_rm_mito_statistics.txt'
    def __init__(self, step, step_name, file_name, samples, root_dir, counts_container):
        self.step_name = step_name
        template_counts_file = os.path.join(root_dir, step, file_name)
        super(FlagstatReport, self).__init__(samples, counts_container, template_counts_file)

    def read_sample_counts(self, sample):
        for line in self.counts_lines(sample):
            if 'in total (QC-passed reads + QC-failed reads)' in line:  #'424760 + 0 in total (QC-passed reads + QC-failed reads)'
                counts = re.match("(\d+) + 0 in total (QC-passed reads + QC-failed reads)", line).group(1)
                self.save_counts(self.step+'_'+self.step_name, sample, counts)

class StarMappingReport(StepReport):
    def __init__(self, samples, root_dir, counts_container):
        template_counts_file = os.path.join(root_dir, '%d_mapping', '%sLog.final.out')
        super(StarMappingReport, self).__init__(samples, counts_container, template_counts_file)

    def read_sample_counts(self, sample):
        counts = 0
        for line in self.counts_lines(sample):
            if 'Uniquely mapped reads number' in line:  #     Uniquely mapped reads number |       1703635
                uniquely_counts = line[line.find('Uniquely mapped reads number |\t')+31:line.find('\n')]
                self.save_counts(self.step+'_uniquely', sample, uniquely_counts)
            if 'Number of reads mapped to multiple loci' in line:  #   Number of reads mapped to multiple loci |       441781
                counts += int(line[line.find('Number of reads mapped to multiple loci |\t')+42:line.find('\n')])
            if 'Number of reads mapped to too many loci' in line: #        Number of reads mapped to too many loci |       5115479
                counts += int(line[line.find('Number of reads mapped to too many loci |\t')+42:line.find('\n')])
        self.save_counts(self.step+'_multiple_loci', sample, str(counts))


class StarCountReadsReport(StepReport):
    def __init__(self, samples, root_dir, counts_container, stranded):
        template_counts_file = os.path.join(root_dir, '%d_mapping', '%sReadsPerGene.out.tab')
        self.stranded = stranded
        super(StarCountReadsReport, self).__init__(samples, counts_container, template_counts_file)


    def get_counts_column(self, sample):
        two_strands = first_strands = second_strands = 0
        for line in self.counts_lines(sample):
            if 'N_unmapped' not in line and 'N_multimapping' not in line and 'N_noFeature' not in line and 'N_ambiguous' not in line and '__' not in line:  # __no_feature
                line_list = line.split('\t')
                two_strands += int(line_list[1])
                first_strands += int(line_list[2])
                second_strands += int(line_list[3])
        if self.stranded == 'yes':
            return first_strands if first_strands > second_strands else second_strands
        elif self.stranded == 'no':
            return two_strands
        else:
            min_strand = min(first_strands, second_strands)
            max_strand = max(first_strands, second_strands)
            if float(min_strand)/max_strand <= 0.5: #stranded
                return max_strand
            else:
                return two_strands

    def read_sample_counts(self, sample):
        counts = self.get_counts_column(sample)
        self.save_counts("3_count_reads", sample, str(counts))

class CountReadsReport(StepReport):
    def __init__(self, samples, root_dir, counts_container):
        template_counts_file = os.path.join(root_dir, '%d_count_reads', '%s_counts.txt')
        super(CountReadsReport, self).__init__(samples, counts_container, template_counts_file)

    def read_sample_counts(self, sample):
        counts = 0
        flag_line = False
        for line in self.counts_lines(sample):
            flag_line = True
            if '__' not in line:  # __no_feature
                start_index = line.find('\t')+1
                counts += int(line[start_index:-1]) #Zscan21 75
        if flag_line:
            self.save_counts(self.step, sample, str(counts))

class DeDupCountsReport(StepReport):
    def __init__(self, samples, root_dir, counts_container):
        template_counts_file = os.path.join(root_dir, '%d_dedup_counts', '%s.deDup_counts.txt')
        super(DeDupCountsReport, self).__init__(samples, counts_container, template_counts_file)

    def read_sample_counts(self, sample):
        counts = 0
        flag_line = False
        for line in self.counts_lines(sample):
            flag_line = True
            if '__' not in line:  # __no_feature
                start_index = line.find('\t') + 1
                counts += int(line[start_index:-1])  # Zscan21 75
        if flag_line:
            self.save_counts(self.step, sample, str(counts))

class CorrectCountsReport(StepReport):
    def __init__(self, samples, root_dir, counts_container):
        template_counts_file = os.path.join(root_dir, '%d_umi_counts', '%s.deDup_counts.corrected.txt')
        super(CorrectCountsReport, self).__init__(samples, counts_container, template_counts_file)

    def read_sample_counts(self, sample):
        counts = 0
        flag_line = False
        for line in self.counts_lines(sample):
            flag_line = True
            if '__' not in line:  # __no_feature
                start_index = line.find('\t') + 1
                counts += float(line[start_index:-1])  # Zscan21 75
        if flag_line:
            self.save_counts(self.step, sample, str(int(counts)))#round the numbers


READABLE_STEP_NAME = {'1_cutadapt':'1_After_cutadapt',  #RNA-seq
                      '3_mapping_uniquely':'2_Mapped_uniquely',  #RNA-seq
                      '3_mapping_multiple_loci':'2_Mapped_to_multiple_loci',  #RNA-seq
                      '3_count_reads':'3_Mapped_to_genes_uniquely',  #RNA-seq
                      '2_cutadapt':'1_After_cutadapt',  #MARS-seq
                      '4_mapping_uniquely':'2_Mapped_uniquely',  #MARS-seq, ATAC-seq
                      '4_mapping_multiple_loci': '2_Mapped_to_multiple_loci',  # MARS-seq, ATAC-seq
                      '6_count_reads': '3_Mapped_to_genes_uniquely',  #MARS-seq
                      '8_dedup_counts': '4_Counts_after_deduplication',  #MARS-seq
                      '9_umi_counts': '5_Counts_after_correction',#MARS-seq
                      '5_process_alignment_without_mitochondria': '2_Counts_without_mitochondria',#ATAC-seq
                      '5_process_alignment_mapped_uniquely': '3_Mapped_uniquely',#ATAC-seq
                      '5_process_alignment_counts_after_deduplication': '4_Counts_after_deduplication',#ATAC-seq
                      '7_nucleosome_free_counts_without_nucleosomes': '5_Counts_without_nucleosomes'}#ATAC-seq


###### main methods #####

def get_readable_step_name(step):
    return READABLE_STEP_NAME[step]

def write_counts_to_file(counts_container, report_file):
    fw = open(report_file, 'w')
    lines = []
    line = ['samples']
    for sample, steps in counts_container.items():#title line
        for step in steps.keys():
            line.append(get_readable_step_name(step))
        break
    lines.append('\t'.join(line)+'\n')
    for sample, steps in counts_container.items():
        line = []
        line.append(sample)
        for step, counts in steps.items():
            line.append(counts)
        lines.append('\t'.join(line)+'\n')
    fw.writelines(lines)
    fw.close()


def parse_args():
    help_txt = "Create report of counts in each step of pipeline for each sample"
    parser = argparse.ArgumentParser(description=help_txt)
    parser.add_argument('--pipeline-dir', type=str, help='Working directory of the pipeline', required=True)
    parser.add_argument('--output', type=str, help='Output file', required=True)
    parser.add_argument('--samples', type=str, nargs='+', help='Space separator list of the samples names', required=True)
    parser.add_argument('--stranded', help='Type of protocol: yes, no or float', required=False)#Only for RNA-seq (not MAR-seq)
    parser.add_argument('--logFile', help='Log File', required=False)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # parse command line
    args = parse_args()
    logging_args = {
        "level": logging.DEBUG,
        "filemode": 'w',
        "format": '%(asctime)s %(message)s',
        "datefmt":'%m/%d/%Y %H:%M:%S'
    }

    # set up log file
    if args.logFile is not None:
        logging_args["filename"] = args.logFile
    logging.basicConfig(**logging_args)

    # Do work
    logging.info('Program started')

    counts_container = {}
    steps_args = args.samples, args.pipeline_dir, counts_container
    try:
        CombinedFastqReport(*steps_args).read_counts()
    except IOError as e:
        logging.info(e.message)
    try:
        CutadaptReport(*steps_args).read_counts()
    except IOError as e:
        logging.info(e.message)
    try:
        StarMappingReport(*steps_args).read_counts()
    except IOError as e:
        logging.info(e.message)
    try:
        CountReadsReport(*steps_args).read_counts()
    except IOError as e:
        logging.info(e.message)
    try:
        DeDupCountsReport(*steps_args).read_counts()
    except IOError as e:
        logging.info(e.message)
    try:
        CorrectCountsReport(*steps_args).read_counts()
    except IOError as e:
        logging.info(e.message)
    flagstat_steps = [['%d_process_alignment', '%d_process_alignment', '%d_process_alignment', '%d_nucleosome_free'],
                     ['without_mitochondria', 'mapped_uniquely', 'counts_after_deduplication', 'counts_without_nucleosomes'],
                     ['%s_rm_mito_statistics.txt', '%s_rm_not_uniq_statistics.txt', '%s_rm_dup_statistics.txt', '%s_nucl_free.statistics']]
    for step, step_name, file_name in zip(*flagstat_steps):
        try:
            FlagstatReport(step, step_name, file_name, *steps_args).read_counts()
        except IOError as e:
            logging.info(e.message)
    steps_args = args.samples, args.pipeline_dir, counts_container, args.stranded
    try:
        StarCountReadsReport(*steps_args).read_counts()
    except IOError as e:
        logging.info(e.message)

    write_counts_to_file(counts_container, args.output)

    logging.info('Program done')

