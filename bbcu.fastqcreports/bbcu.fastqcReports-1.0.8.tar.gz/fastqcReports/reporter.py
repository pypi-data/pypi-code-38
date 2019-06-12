import re
import logging
from math import log10, ceil
from os import path, listdir, walk
from shutil import copytree, copyfile, rmtree

import numpy
from bioutils.fastqc.io import FastQcOutputReader
from bs4 import BeautifulSoup
from jinja2 import Template
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot

logger = logging.getLogger(__name__)


def get_fastqc_stats(path_to_fastqc_data):
    with open(path_to_fastqc_data, 'r') as fastqc_fh:
        read_module_output = FastQcOutputReader(fastqc_fh)
        read_module_output.read()
    return read_module_output


def get_fastqc_data(path_to_fastqc_data, per_base_quality=True, basic_statistics=True):
    means = None
    bases = None
    pf = None
    read_module_output = get_fastqc_stats(path_to_fastqc_data)
    if per_base_quality:
        means = read_module_output.per_base_sequence_quality_reader_output.means
        bases = read_module_output.per_base_sequence_quality_reader_output.bases
    if basic_statistics:
        pf = read_module_output.basic_statistics_reader_output.reads_pf
    p_q30 = read_module_output.per_sequence_quality_scores_reader_output.p_over_q_30
    count = read_module_output.per_sequence_quality_scores_reader_output.count
    return means, bases, count, pf, p_q30


def sample_statistics(path_to_fastqc_data):
    read_module_output = get_fastqc_stats(path_to_fastqc_data)
    mean_q_score = read_module_output.per_sequence_quality_scores_reader_output.mean_q_score
    p_over_q_30 = read_module_output.per_sequence_quality_scores_reader_output.p_over_q_30
    return '%0.2f' % p_over_q_30, '%0.1f' % mean_q_score



class Reporter(object):
    def __init__(self, fastq_dir, fastqc_dir, paired_end):
        self.fastq_dir = fastq_dir
        self.fc_name = path.basename(fastq_dir.strip('/'))
        self.fastqc_dir = fastqc_dir
        self.paired_end = paired_end
        self.flw_features = ['Clusters (Raw)', 'Clusters(PF)', 'Yield (MBases)']
        self.project_features_str = ['Sample', 'Barcode sequence']
        self.project_features_num = ['PF Clusters', '% of thelane', 'Yield (Mbases)']

    def statistics(self, read_identifier):
        logger.debug(self.fastqc_dir)
        fastqc_dir_pattern = re.compile(read_identifier + '_fastqc$')
        all_means = []
        bases = []
        all_pf = []
        samples = []
        skip_q_score_graph = False
        for root_sample_dir in numpy.sort(listdir(path.join(self.fastqc_dir))):
            if root_sample_dir == 'resources' or root_sample_dir == 'index.html' or root_sample_dir == 'tmp_blast' or root_sample_dir == 'MultiQC':
                continue
            for sample_dir in numpy.sort(listdir(path.join(self.fastqc_dir, root_sample_dir))):
                if re.search(fastqc_dir_pattern, sample_dir):
                    fastqc_xml_file = path.join(self.fastqc_dir, root_sample_dir, sample_dir, 'fastqc_data.txt')
                    basic_stats = (read_identifier == 'R1')
                    logger.debug("Getting FastQC data for: " + sample_dir)
                    sample_means, sample_bases, count, sample_pf, p_q30 = get_fastqc_data(fastqc_xml_file,
                                                                                          basic_statistics=basic_stats)
                    all_means.append(sample_means)
                    all_pf.append(sample_pf)
                    sample_name = re.compile('_[AGCT]{4,15}_').split(sample_dir)[0]
                    samples.append(sample_name)
                    if len(bases) == 0:
                        bases = sample_bases
                    if len(bases) != len(sample_bases):
                        # one or more of the samples has a different read length!
                        logger.info("Samples in lane %s have varying read lengths. Skipping q-scores graph.")
                        skip_q_score_graph = True
        return all_means, bases, all_pf, samples, skip_q_score_graph

    def plot_graphs_for_samples(self, read_identifier):
        logger.debug(self.fastqc_dir)
        fastqc_dir_pattern = re.compile(read_identifier + '_fastqc$')
        all_means, bases, all_pf, samples, skip_q_score_graph = self.statistics(read_identifier)
        output_dir = path.join(self.fastqc_dir, 'resources', 'images')
        # finished iterating over samples of lane, plot and save
        if any(samples):
            plot_name = '%s_q_scores.png' % read_identifier
            if (skip_q_score_graph):
                copyfile(path.join(path.dirname(path.realpath(__file__)), 'reports', 'graph_unavailable.png', ),
                         path.join(output_dir, plot_name))
            else:
                x = range(1, len(bases) + 1)
                pyplot.figure(figsize=(20, 10))
                pyplot.grid()
                for i in range(0, len(samples)):
                    pyplot.plot(x, all_means[i], label=samples[i])
                pyplot.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0., ncol=1 + len(samples) // 30)
                locs, labels = pyplot.xticks(x, bases)
                # show every other tick on x axis (as in FastQC report)
                for label in labels[9::2]:
                    label.set_visible(False)
                pyplot.ylim(0, 40)
                pyplot.savefig(path.join(output_dir, plot_name), bbox_inches='tight')
                pyplot.close()

        # plot and save
        if any(all_pf):
            num_bins = len(samples)
            plot_width = 15
            bars_per_graph = min(25, num_bins)
            N = int(ceil(num_bins / (0.0 + bars_per_graph)))
            fig = pyplot.figure(figsize=(plot_width, N * 5))
            step = 2 * pow(10, int(log10(max(all_pf))))
            ymax = max(all_pf) + step
            # define mean line
            mean_pf_line = sum(all_pf) / num_bins
            # create sub lists for subplots
            sublists_samples = [samples[x:x + bars_per_graph] for x in range(0, num_bins, bars_per_graph)]
            sublists_pf = [all_pf[x:x + bars_per_graph] for x in range(0, num_bins, bars_per_graph)]

            for num_subplot in range(0, N):
                index = numpy.arange(0, len(sublists_samples[num_subplot]))
                pyplot.subplot(N, 1, num_subplot + 1)
                # draw mean line
                line = pyplot.plot([0, bars_per_graph], [mean_pf_line, mean_pf_line], color='red')

                rects = pyplot.bar(index, sublists_pf[num_subplot])
                pyplot.ylabel("#PF reads")
                pyplot.yticks(range(0, ymax, step))
                pyplot.xticks(index, sublists_samples[num_subplot], rotation=45, ha='center')
                pyplot.xlim([0, bars_per_graph])
                for ii, rect in enumerate(rects):
                    height = rect.get_height()
                    pyplot.text(rect.get_x() + rect.get_width() / 2., 1.02 * height,
                                '%s' % (sublists_pf[num_subplot][ii]), ha='center', va='bottom')
            fig.legend(line, ["Average #PF reads per sample"], bbox_to_anchor=(0., .99, 1., 0.02), loc='lower right',
                       borderaxespad=0.)
            pyplot.tight_layout()
            plot_name = 'pf_reads.png'
            pyplot.savefig(path.join(output_dir, plot_name), bbox_inches='tight')
            pyplot.close()

    def parse_demultiplex_stats(self):
        html_f = path.join(self.fastq_dir, 'Reports/html')
        html_f = path.join(html_f, walk(html_f).next()[1][0], 'all/all/all/laneBarcode.html')
        text = None
        if path.isfile(html_f):
            with open(html_f, 'r') as f:
                with open(html_f, 'r') as f:
                    text = f.read()
                if text is None:
                    logger.error('Failed getting summary from %s file.' % html_f)
                    return
        else:
            logger.error('Cannot open %s file' % html_f)
        self.flw_dict = {}
        soup = BeautifulSoup(text, "html.parser")
        flw_table = soup.find('table', {'id': 'ReportTable'})
        header_line = [i.text for i in flw_table.find('th').parent.findAll('th')]
        body = flw_table.find('tr').find_next_siblings('tr')
        for line in body:
            line = [i.text for i in line.findAll('td')]
            for header, value in zip(header_line, line):
                self.flw_dict[header] = value

        self.samples_dict = {}
        samples_table = flw_table.findNext('table', {'id': 'ReportTable'})
        header_line = [i.text for i in samples_table.find('th').parent.findAll('th')]
        body = samples_table.find('tr').find_next_siblings('tr')
        for line in body:
            line = [i.text for i in line.findAll('td')]
            sample_name = line[2]
            if sample_name not in self.samples_dict:
                self.samples_dict[sample_name] = {}
                self.samples_dict[sample_name]['dup'] = 1
            else:
                self.samples_dict[sample_name]['dup'] += 1

            for header, value in zip(header_line, line):
                if header not in self.samples_dict[sample_name]:
                    self.samples_dict[sample_name][header] = str(self.str2num(value, header))
                elif header in self.project_features_num:#sum the numbers of the sample from all lanes
                    self.samples_dict[sample_name][header] = str(
                        self.str2num(self.samples_dict[sample_name][header], header) + self.str2num(value, header))
        for sample in self.samples_dict.keys():
            self.samples_dict[sample]['PF Clusters'] = "{:,}".format(int(self.samples_dict[sample]['PF Clusters']))
            self.samples_dict[sample]['% of thelane'] = "%.2f" % (
                float(self.samples_dict[sample]['% of thelane']) / float(self.samples_dict[sample]['dup']))
            self.samples_dict[sample]['Yield (Mbases)'] = "{:,}".format(
                int(self.samples_dict[sample]['Yield (Mbases)']))

    def str2num(self, num, header):
        if header == 'PF Clusters' or header == 'Yield (Mbases)':
            return int(num.replace(',', ''))
        elif header == '% of thelane':
            try:
                return float(num)
            except ValueError:
                return 0.0
        else:
            return num

    def summary_files(self):
        # full porject_features
        # [u'Lane', u'Project', u'Sample', u'Barcode sequence', u'PF Clusters', u'% of thelane', u'% Perfectbarcode',
        # u'% One mismatchbarcode', u'Yield (Mbases)', u'% PFClusters', u'% >= Q30bases', u'Mean QualityScore']
        date, _, _, fc = self.fc_name.split('_')
        date = '%s-%s-20%s' % (
            date[4:6], date[2:4], date[0:2])  # the format in the run data is: first year, then month, then day
        fastqc_dir_pattern = re.compile('fastqc$')
        read_dirs = {}
        is_cellranger = False
        for sample_root_dir in listdir(path.join(self.fastqc_dir)):
            if sample_root_dir == 'resources' or sample_root_dir == 'index.html' or sample_root_dir == 'tmp_blast' or sample_root_dir == 'MultiQC':
                continue
            for sample_dir in listdir(path.join(self.fastqc_dir, sample_root_dir)):
                if re.search(fastqc_dir_pattern, sample_dir):
                    sample_name = sample_dir
                    if '_Lall_' in sample_name:
                        is_cellranger = True
                    # TODO: replace with regular expression
                    for pattern in ('_Lall_I1_fastqc', '_Lall_R1_fastqc', '_Lall_R2_fastqc', #For cellranger pipeline
                                    '_R1_fastqc', '_R1_001_fastqc', '_R2_fastqc', '_R2_001_fastqc',
                                    '_R3_fastqc', '_R3_001_fastqc', '_R4_fastqc', '_R4_001_fastqc'):

                        sample_name = sample_name.replace(pattern, '')
                        # sample_name = P84_Lall_I1_fastqc
                        # sample_dir = /services/FastQC/190218_NB501465_0471_AHTTM3BGX9/P84/
                        # sample_root_dir = /services/FastQC/190218_NB501465_0471_AHTTM3BGX9/
                    if sample_name not in read_dirs:
                        read_dirs[sample_name] = []
                    read_dirs[sample_name].append(sample_dir)

        template_file = open(path.join(path.dirname(__file__), 'reports', 'project_report.html'), 'r')
        template = Template(template_file.read())
        template_file.close()
        project_stats = []
        samp_dict = None

        for sample in sorted(self.samples_dict):
            if sample != 'Undetermined':
                samp_dict = self.samples_dict[sample]
                # sample_id = '%s_%s' %(sample, samp_dict['Barcode sequence'])
                for read_dir in read_dirs:
                    if not is_cellranger and sample != read_dir:
                        continue
                    if is_cellranger and sample[:-3] != read_dir and sample[:-4] != read_dir:
                        continue
                    for read in read_dirs[read_dir]:
                        if 'R1_fastqc' in read or 'R1_001_fastqc' in read:
                            samp_dict['readID'] = path.join(read_dir, read)
                            # add statistics from fastqc
                            samp_dict['q30_pf_r1'], samp_dict['mean_qscore_r1'] = sample_statistics(
                                path.join(self.fastqc_dir, read_dir, read, 'fastqc_data.txt'))
                        if 'R2_fastqc' in read or 'R3_fastqc' in read or 'R4_fastqc' in read or 'R2_001_fastqc' in \
                                read or 'R3_001_fastqc' in read or 'R4_001_fastqc' in read:
                            samp_dict['read2ID'] = path.join(read_dir, read)
                            # add statistics from fastqc
                            samp_dict['q30_pf_r2'], samp_dict['mean_qscore_r2'] = sample_statistics(
                                path.join(self.fastqc_dir, read_dir, read, 'fastqc_data.txt'))
                project_stats.append(samp_dict)
        if 'Undetermined' in self.samples_dict:
            samp_dict = self.samples_dict['Undetermined']
            samp_dict['Sample'] = 'Undetermined Indices'
            samp_dict['Barcode sequence'] = 'Undetermined'
            project_stats.append(samp_dict)

        text = template.render(d_stat=project_stats, paired_end=self.paired_end, date=date, fc_name=fc,
                               run_name=self.fc_name, left_project_features=self.project_features_str,
                               right_project_features=self.project_features_num, flw_stats=self.flw_dict,
                               flw_features=self.flw_features)
        # write to file
        html_file_name = path.join(self.fastqc_dir, 'index.html')
        with open(html_file_name, 'w+') as html_f:
            html_f.write(text)

    def copy_files(self):
        # copy resources to output dir (images, css etc.)
        resources_dir = path.join(path.dirname(path.realpath(__file__)), 'reports', 'resources')
        target_dir = path.join(self.fastqc_dir, 'resources')
        if path.exists(target_dir):
            rmtree(target_dir)
        copytree(resources_dir, target_dir)

    def marseq_report(self):
        with open(path.join(self.fastq_dir, "sampleBarcodeList.txt"), 'r') as barcodes:
            flag = False
            for line in barcodes:
                if not flag:  # header line
                    flag = True
                    continue
                sample, barcode = line.split(' ')
                features = [u'Lane', u'Project', u'Sample', u'Barcode sequence', u'PF Clusters', u'% of thelane',
                            u'% Perfectbarcode', u'% One mismatchbarcode', u'Yield (Mbases)',
                            u'% PFClusters', u'% >= Q30bases', u'Mean QualityScore', 'readID', 'read2ID', 'q30_pf_r1',
                            'q30_pf_r2']
                self.samples_dict[sample] = {}
                # for feature in features:
                #     self.samples_dict[sample][feature] = ''
                self.samples_dict[sample]['Barcode sequence'] = barcode
                self.samples_dict[sample]['Sample'] = sample
        for sample_name in self.samples_dict.keys() + ['Undetermined']:
            yieldbases = 0
            fastqc_xml_file1 = path.join(self.fastqc_dir, sample_name, sample_name + '_R1_' + 'fastqc',
                                         'fastqc_data.txt')
            fastqc_xml_file2 = path.join(self.fastqc_dir, sample_name, sample_name + '_R2_' + 'fastqc',
                                         'fastqc_data.txt')
            if path.exists(fastqc_xml_file1):
                logger.debug("Getting FastQC data for: " + sample_name)
                sample_means, sample_bases, count, sample_pf, p_q30 = get_fastqc_data(fastqc_xml_file1,
                                                                                      basic_statistics=True)
                self.samples_dict[sample_name]['PF Clusters'] = "{:,}".format(int(sample_pf))
                self.samples_dict[sample_name]['% of thelane'] = "%.2f" % (
                    float(sample_pf)*100 / float(self.flw_dict['Clusters(PF)'].replace(',', '')))
                yieldbases = "{:,}".format(int(int(len(sample_bases) * count) / 1000000))
                self.samples_dict[sample_name]['Yield (Mbases)'] = yieldbases
            if path.exists(fastqc_xml_file2):
                sample_means, sample_bases, count, sample_pf, p_q30 = get_fastqc_data(fastqc_xml_file2,
                                                                                      basic_statistics=True)
                self.samples_dict[sample_name]['Yield (Mbases)'] = "{:,}".format(
                    int((int(len(sample_bases) * count) + int(yieldbases.replace(',', '')) * 1000000) / 1000000))

    def table_for_read(self, output_file, read):
        all_means, bases, all_pf, samples, skip_q_score_graph = self.statistics(read)
        with open(output_file, 'w') as report_file:
            report_file.write('\t'.join(['Sample','Base','Mean']) + '\n')
            for i in range(len(samples)):
                if samples[i] == 'Undetermined_'+read+'_fastqc':
                    continue
                for j in range(len(all_means[i])):
                    line = [samples[i]]
                    line.append(str(j+1))
                    line.append(str(all_means[i][j]))
                    report_file.write('\t'.join(line) + '\n')

    def write_table(self, output_file_base):
        self.table_for_read(output_file_base + '_R1.csv', 'R1')
        if self.paired_end:
            self.table_for_read(output_file_base + '_R2.csv', 'R2')

    def run(self):
        self.copy_files()
        self.parse_demultiplex_stats()
        if len(self.samples_dict.keys()) == 1:  # only undetermined
            self.marseq_report()
        self.summary_files()
        self.plot_graphs_for_samples('R1')
        if self.paired_end:
            self.plot_graphs_for_samples('R2')
