#!/usr/bin/env python

import argparse
import itertools
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
    --output-dir: Directory for output files.
    --samples: Space separator list of the samples names.
    --samples-deseq: Space separator list of the samples descriptors for run deseq on them.
    --factors: Space separator list of the samples descriptors.
    --logFile: (optional) Where the log file should be written.

'''


class OutputMatrix(object):
    def __init__(self):
        self.header = []
        self.lines = OrderedDict()


class StepReport(object):
    __metaclass__ = ABCMeta

    def __init__(self, samples, template_input_file, out_file):
        self.samples = samples
        self.out_file = out_file
        self.template_input_file = self.get_step_path(template_input_file)
        self.out_container = OutputMatrix()
        logging.info('Start step: %s' % self.name)

    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def read_sample_details(self, sample_name):
        pass

    @abstractmethod
    def create_header(self):
        pass

    def save_container(self, key, value):
        try:
            self.out_container.lines[key].append(value)  # Zscan21 75
        except KeyError:
            self.out_container.lines[key] = [value]

    def create_output(self):
        self.create_header()
        for sample in self.samples:
            logging.info('Start read step %s of sample: %s' % (self.name, sample))
            self.read_sample_details(sample)
            logging.info('End read step %s of sample: %s' % (self.name, sample))
        self.write_counts_to_file()

    def get_step_path(self, file):
        template_step = os.path.basename(os.path.dirname(file))
        for step_path in os.listdir(os.path.dirname(os.path.dirname(file))):
            if os.path.isdir(step_path) and template_step[2:] in step_path:
                return os.path.join(os.path.dirname(os.path.dirname(file)), step_path, os.path.basename(file))
        return ''

    def input_lines(self, sample_name):
        try:
            fh = open(self.template_input_file % sample_name)
        except (IOError, TypeError):
            raise Exception('No such %s step in this pipeline or not run yet' % self.name)
        for line in fh:
            yield line
        fh.close()

    def write_counts_to_file(self):
        fw = open(self.out_file, 'w')
        lines = []
        lines.append('\t'.join(self.out_container.header) + '\n')
        for name, values in self.out_container.lines.items():
            line = [name] + values
            lines.append('\t'.join(line) + '\n')
        fw.writelines(lines)
        fw.close()
        logging.info('End step: %s' % self.name)


# Get the counts of reads.
class CountMatrix(StepReport):
    def __init__(self, samples, template_input_file, out_file):
        super(CountMatrix, self).__init__(samples, template_input_file, out_file)

    def create_header(self):
        self.out_container.header.append('Gene')
        for sample in self.samples:
            self.out_container.header.append(sample)

    def read_sample_details(self, sample):
        for line in self.input_lines(sample):
            if '__' not in line:  # __no_feature
                space_index = line.find('\t')
                name = line[:space_index]
                counts = line[space_index + 1:-1]
                self.save_container(name, counts)


# Get the counts of non features reads.
class NonFeatureCounts(StepReport):
    def __init__(self, samples, template_input_file, out_file):
        super(NonFeatureCounts, self).__init__(samples, template_input_file, out_file)

    def create_header(self):
        self.out_container.header.append('Gene')
        for sample in self.samples:
            self.out_container.header.append(sample)

    def read_sample_details(self, sample):
        for line in self.input_lines(sample):
            if '__' in line:  # __no_feature
                space_index = line.find('\t')
                name = line[2:space_index]
                counts = line[space_index + 1:-1]
                self.save_container(name, counts)


# Get statistics of cutadapt.
class TrimStats(StepReport):
    def __init__(self, samples, template_input_file, out_file):
        super(TrimStats, self).__init__(samples, template_input_file, out_file)

    def create_header(self):
        with open(self.template_input_file % self.samples[0]) as statf:
            if "Total read pairs processed" in statf.read():
                columns = ['Sample', 'Total read pairs processed', 'Read 1 with adapter', 'Pairs that were too short',
                           'Percent Read 1 with adapters', 'Percent Pairs too short']
            else:
                columns = ['Sample', 'Total reads processed', 'Reads with adapters', 'Reads that were too short',
                           'Percent with adapters', 'Percent too short']
        for col in columns:
            self.out_container.header.append(col)

    def read_sample_details(self, sample):
        for line in self.input_lines(sample):
            if self.out_container.header[1] in line:
                col_index = line.find(":")
                num_start = line.rfind(' ') + 1
                num = line[num_start:-1]
                self.save_container(sample, num.replace(',', ''))
            if self.out_container.header[2] in line:
                col_index = line.find(":")
                percent_start = line.rfind('(') + 1
                percent_adapt = line[percent_start:-3]
                num_start = line[:percent_start - 3].rfind(' ') + 1
                num = line[num_start:percent_start - 2]
                self.save_container(sample, num.replace(',', ''))
            if self.out_container.header[3] in line:
                col_index = line.find(":")
                percent_start = line.rfind('(') + 1
                percent_short = line[percent_start:-3]
                num_start = line[:percent_start - 3].rfind(' ') + 1
                num = line[num_start:percent_start - 2]
                self.save_container(sample, num.replace(',', ''))
                self.save_container(sample, percent_adapt)
                self.save_container(sample, percent_short)


# Get statistics of mapping.
class MappingStats(StepReport):
    def __init__(self, samples, template_input_file, out_file):
        super(MappingStats, self).__init__(samples, template_input_file, out_file)

    def create_header(self):
        columns = ['Sample', 'Started job on', 'Started mapping on', 'Finished on',
                   'Mapping speed, Million of reads per hour', 'Number of input reads', 'Average input read length',
                   'Uniquely mapped reads number', 'Uniquely mapped reads %', 'Average mapped length',
                   'Number of splices: Total', 'Number of splices: Annotated (sjdb)', 'Number of splices: GT/AG',
                   'Number of splices: GC/AG', 'Number of splices: AT/AC', 'Number of splices: Non-canonical',
                   'Mismatch rate per base, %', 'Deletion rate per base', 'Deletion average length',
                   'Insertion rate per base', 'Insertion average length', 'Number of reads mapped to multiple loci',
                   '% of reads mapped to multiple loci', 'Number of reads mapped to too many loci',
                   '% of reads mapped to too many loci', '% of reads unmapped: too many mismatches',
                   '% of reads unmapped: too short', '% of reads unmapped: other']
        for col in columns:
            self.out_container.header.append(col)

    def read_sample_details(self, sample):
        for line in self.input_lines(sample):
            for feature in self.out_container.header:
                if feature in line:  # Uniquely mapped reads number |       1703635
                    counts = line[line.find('|\t') + 2:-1]
                    self.save_container(sample, counts)


class StarCountsStats(StepReport):
    def __init__(self, samples, template_input_file, out_file, stranded):
        self.stranded = stranded
        super(StarCountsStats, self).__init__(samples, template_input_file, out_file)

    def create_header(self):
        self.out_container.header.append('Gene')
        for sample in self.samples:
            self.out_container.header.append(sample)

    def get_counts_column(self, sample):
        two_strands = first_strands = second_strands = 0
        flag = False
        for line in self.input_lines(sample):
            flag = True
            if 'N_unmapped' not in line and 'N_multimapping' not in line and 'N_noFeature' not in line and 'N_ambiguous' not in line and '__' not in line:  # __no_feature
                line_list = line.split('\t')
                two_strands += int(line_list[1])
                first_strands += int(line_list[2])
                second_strands += int(line_list[3])
        if flag:
            if self.stranded == 'yes':
                return 2 if first_strands > second_strands else 3
            elif self.stranded == 'no':
                return 1
            else:
                min_strand = min(first_strands, second_strands)
                max_strand = max(first_strands, second_strands)
                if float(min_strand) / max_strand <= 0.5:  # stranded
                    return 2 if first_strands > second_strands else 3
                else:
                    return 1


    def read_sample_details(self, sample):
        counts_column = self.get_counts_column(sample)
        for line in self.input_lines(sample):
            if 'N_unmapped' not in line and 'N_multimapping' not in line and 'N_noFeature' not in line and 'N_ambiguous' not in line and '__' not in line:  # __no_feature
                line_list = line.split('\t')
                name = line_list[0]
                counts = line_list[counts_column].strip()
                self.save_container(name, counts)


class NGSplotConfig(object):
    def __init__(self, samples, root_dir, output_dir):
        self.samples = samples
        self.root_dir = root_dir
        self.input_dir = self.get_step_path('%d_mapping')
        self.out_file = os.path.join(output_dir, 'ngsplot_config.txt')

    def get_step_path(self, step):
        for step_path in os.listdir(self.root_dir):
            if os.path.isdir(step_path) and step[2:] in step_path:
                return os.path.join(self.root_dir, step_path)
        return ''

    def create_config_file(self):
        with open(self.out_file, 'w') as output:
            for sample in self.samples:
                output.write(self.input_dir + "/" + sample + "Aligned.sortedByCoord.out.bam" + "\t-1\t" + sample + "\n")


class ComparingFiles(object):
    def __init__(self, samples, samples_deseq, factors, batches, output_dir, run_id):
        self.samples = samples
        self.samples_deseq = samples_deseq
        self.factors = factors
        self.batches = None if batches == ['no-deseq'] else batches
        self.desc_out_file = os.path.join(output_dir, 'sample_desc_'+run_id+'.csv')
        self.comp_out_file = os.path.join(output_dir, 'comparisons_'+run_id+'.csv')
        self.unique_desc = list(sorted(set(self.factors), key=self.factors.index))
        logging.info('Start step: %s' % self.__class__.__name__)

    def valid_factors(self):
        if self.factors == ['no-deseq']:
            logging.info('no factors - no run deseq')
            return True
        if len(self.samples_deseq) != len(self.factors):
            self.factors = self.samples_deseq
            logging.error('The numbers of the samples and their factors is not equal.')
            return False
        # if len(self.unique_desc) > 2:
        #     self.factors = self.samples_deseq
        #     logging.error('The factors cannot contain more than 2 factors.')
        #     return False
        if len(self.unique_desc) == 1:
            logging.error('There is only one factor.')
            return False
        if self.batches:
            if len(list(set(self.batches))) == 1:
                logging.error('There is only one batch')
                return False
            if len(self.batches) != len(self.factors):
                logging.error('The numbers of the factors and their batches is not equal.')
                return False
            else:
                logging.info('There is %d samples and %d descriptions' % (len(self.samples), len(self.factors)))
                return True
        else:#There are factors but not batch
            logging.info('There is %d samples and %d descriptions' % (len(self.samples), len(self.factors)))
            return True

    def print_desc_file(self):
        lines = []
        # header
        if self.batches:
            lines.append('\t'.join(['Sample', 'condition', 'batches']) + '\n')
        else:
            lines.append('\t'.join(['Sample', 'condition']) + '\n')
        # lines
        if self.factors == ['no-deseq']:
            self.factors = ['No'] * len(self.samples)
            for sample, desc in zip(self.samples, self.factors):
                lines.append('\t'.join([sample, desc]) + '\n')
        else:
            if self.batches:
                for sample, desc, batch in zip(self.samples_deseq, self.factors, self.batches):
                    lines.append('\t'.join([sample, desc, batch]) + '\n')
            else:
                for sample, desc in zip(self.samples_deseq, self.factors):
                    lines.append('\t'.join([sample, desc]) + '\n')
        with open(self.desc_out_file, 'w') as descfile:
            descfile.writelines(lines)

    def print_comp_file(self):
        lines = []
        lines.append('\t'.join(['Comparison', 'Factor', 'A', 'B', 'Formula']) + '\n')

        for pair in itertools.combinations(self.unique_desc, r=2):
            vs = pair[0] + '_vs_' + pair[1]
            Or = pair[0] + '_or_' + pair[1]
            lines.append('\t'.join([vs, Or, pair[0], pair[1], Or]) + '\n')
        with open(self.comp_out_file, 'w') as compfile:
            compfile.writelines(lines)

    def print_empty_files(self):
        with open(self.desc_out_file, 'w') as descfile:
            descfile.writelines([])
        with open(self.comp_out_file, 'w') as compfile:
            compfile.writelines([])

    def print_files(self):
        if self.valid_factors():
            self.print_desc_file()
            self.print_comp_file()
        else:
            self.print_empty_files()
        logging.info('End step: %s' % self.__class__.__name__)


###### main methods #####

def parse_args():
    help_txt = "Create report of counts in each step of pipeline for each sample"
    parser = argparse.ArgumentParser(description=help_txt)
    parser.add_argument('--run-id', type=str, help='This name incorporate to name of output file', default='', required=False)
    parser.add_argument('--pipeline-dir', type=str, help='Working directory of the pipeline', required=True)
    parser.add_argument('--output-dir', type=str, help='Output directory for the output files', required=True)
    parser.add_argument('--samples', type=str, nargs='+', help='Space separator list of the samples names',
                        required=True)
    parser.add_argument('--samples-deseq', type=str, nargs='+', help='Space separator list of the samples factors',
                        required=True)
    parser.add_argument('--factors', type=str, nargs='+', help='Space separator list of the samples factors',
                        required=True)
    parser.add_argument('--batches', type=str, nargs='+', help='Space separator list of the samples batches',
                        required=True)
    parser.add_argument('--stranded', help='Type of protocol: yes, no or float',
                        required=False)  # Only for RNA-seq (not MAR-seq)
    parser.add_argument('--logFile', help='Log File', required=False)
    args = parser.parse_args()
    return args


class CreateArgs(object):
    def __init__(self, samples, root_dir, root_out_dir):
        self.samples = samples
        self.root_dir = root_dir
        self.root_out_dir = root_out_dir

    def getargs(self, indir, infile, outfile):
        template_input_file = os.path.join(self.root_dir, indir, infile)
        out_file = os.path.join(args.output_dir, outfile)
        return (self.samples, template_input_file, out_file)


if __name__ == '__main__':
    # parse command line
    args = parse_args()
    logging_args = {
        "level": logging.DEBUG,
        "filemode": 'w',
        "format": '%(asctime)s %(message)s',
        "datefmt": '%m/%d/%Y %H:%M:%S'
    }

    # set up log file
    if args.logFile is not None:
        logging_args["filename"] = args.logFile
    logging.basicConfig(**logging_args)

    create_args = CreateArgs(args.samples, args.pipeline_dir, args.output_dir)
    # Do work
    logging.info('Program started')
    try:
        steps_args = args.samples, args.samples_deseq, args.factors, args.batches, args.output_dir, args.run_id
        ComparingFiles(*steps_args).print_files()
    except Exception as e:
        logging.info(e.message)
    try:
        steps_args = create_args.getargs('%d_umi_counts', '%s.deDup_counts.corrected.txt', 'countsCorrectedMatrix.txt')
        CountMatrix(*steps_args).create_output()
    except Exception as e:
        logging.info(e.message)
    try:
        steps_args = create_args.getargs('%d_count_reads', '%s_counts.txt', 'countsMatrix.txt')
        CountMatrix(*steps_args).create_output()
    except Exception as e:
        logging.info(e.message)
    try:
        steps_args = create_args.getargs('%d_count_reads', '%s_counts.txt', 'noncountsMatrix.csv')
        NonFeatureCounts(*steps_args).create_output()
    except Exception as e:
        logging.info(e.message)
    try:
        steps_args = create_args.getargs('%d_cutadapt', '%s.cutadapt.txt', 'trim_stats.csv')
        TrimStats(*steps_args).create_output()
    except Exception as e:
        logging.info(e.message)
    try:
        steps_args = create_args.getargs('%d_mapping', '%sLog.final.out', 'mapping_stats.csv')
        MappingStats(*steps_args).create_output()
    except Exception as e:
        logging.info(e.message)
    steps_args = (args.samples, args.pipeline_dir, args.output_dir)
    NGSplotConfig(*steps_args).create_config_file()
    try:
        steps_args = create_args.getargs('%d_mapping', '%sReadsPerGene.out.tab', 'countsMatrix.txt')
        steps_args += (args.stranded,)
        StarCountsStats(*steps_args).create_output()
    except Exception as e:
        logging.info(e.message)
    logging.info('Program done')
