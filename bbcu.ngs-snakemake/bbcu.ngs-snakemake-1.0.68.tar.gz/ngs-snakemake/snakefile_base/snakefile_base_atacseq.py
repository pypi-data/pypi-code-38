import re

from functions import *
from creature import *

if not config:
    configfile: os.path.join(os.getcwd(), 'config-atacseq.yaml')

RUN_ID = str(config['run_id'])
RAW_JOB_NAME = str(config['job_name'])
JOB_NAME = re.sub('[^0-9a-zA-Z]+', '_', RAW_JOB_NAME)
FASTQ_DIR = config['fastq_dir']
ROOT_OUT_DIR = config['output_dir']
SCRIPTS = config['scripts']
TEMPLATES = config['templates']
PYTHON = config['python']
RSCRIPT = config['Rscript'].replace('/', '\/')
CONDA_ROOT = config['conda_root'] #Not in use for now
JAVA = config['java']
PICARD_EXE = config['picard_exe']
R_LIB_PATHS = config['R_lib_paths'].replace('/', '\/')
FASTQC_EXE = config['fastqc_exe']
MULTIQC_EXE = config['multiqc_exe']
BOWTIE2_EXE = config['bowtie2_exe']
NGS_PLOT_EXE = config['ngs_plot_exe'] if config['ngs_plot_exe'] else ''
GS_EXE = config['gs_exe']
MACS2_EXE = config['macs2_exe']
SAMTOOLS_EXE = config['samtools_exe']
CUTADAPT_EXE = config['cutadapt_exe']
CUTADAPT_ADAP1 = config['adaptor1']
CUTADAPT_ADAP2 = config['adaptor2']
GENOME = config['genome']
TSS_FILE = config['tss_file']
BEDTOOLS_EXE  = config['bedtools_exe'] #Not in use for now
IGVTOOLS_EXE  = config['igvtools_exe'] #Not in use for now
TREAT_VS_CONTROL= config['treat_vs_control'] if 'treat_vs_control' in config.keys() else None
MAX_THREADS_NUM = int(config['max_threads_num'])
JAVA_FOR_FASTQ = os.path.join(config['conda_root'], 'envs/utap/bin/java')


if 'TEST' in config:
    SCRIPTS = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/bin"
    TEMPLATES = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/lib/python2.7/site-packages/ngs-snakemake"
    PYTHON = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/bin/python"

creature = os.path.basename(TSS_FILE).split('.')[0]
if creature == 'hg19' or creature == 'hg38': #For now no tss file for human
    TSS_FILE = None
required_parameters = ['NGSPLOT_GENOME', 'RUN_NGSPLOT', 'MACS_GENOME_SIZE']
NGSPLOT_GENOME, RUN_NGSPLOT, MACS_GENOME_SIZE = get_creature_parameters(creature, NGS_PLOT_EXE, *required_parameters)
SAMPLES, COMBINE_INPUT_FILES = get_samples(FASTQ_DIR)
SAMPLES_LIST = ' '.join(SAMPLES)
#COMBINE_SAMPLES_DB is dictionary. key is combined name of the sampls, value is list of the combined samples. For example: {"samp1+samp2":[samp1, samp2]}
COMBINE_SAMPLES_DB, TREATMENT, CONTROL = get_treat_vs_control(phenodata_file=TREAT_VS_CONTROL) if TREAT_VS_CONTROL else ({}, None, None)
FASTQ_DIR_ANALYSIS = concatenate_fastq_files(ROOT_OUT_DIR, FASTQ_DIR, SAMPLES) if COMBINE_INPUT_FILES else FASTQ_DIR
LOG_DIR_NAME = 'logs_' + RUN_ID
# CUTADAPT_TEMPLATE = cutadapt_template(ROOT_OUT_DIR, paired_end=True)  # Not in use. Always paired-end

REPORT_STEP = '10_reports'  # TODO: Update the number of this folder
TEMP_DIR = os.path.join(ROOT_OUT_DIR, 'tmp')
COMMANDS_LOG_SED = 'commands_log_' + RUN_ID + '.txt'


# Must to implement these functions here because they need to get FASTQ_DIR_ANALYSIS parameter that cannot to be passed to the function
def fastq_r1(wildcards):
    sample = wildcards.sample
    return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*_R1*'))[0]


def fastq_r2(wildcards):
    sample = wildcards.sample
    return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*_R2*'))[0]


def get_fastq(paired_end):
    return [fastq_r1, fastq_r2] if paired_end else [fastq_r1]


os.makedirs(ROOT_OUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, 'Advanced_analysis'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, LOG_DIR_NAME), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, REPORT_STEP), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '1_cutadapt'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '2_fastqc'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '3_multiqc'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '4_mapping'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '5_process_alignment'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '6_ngs_plot'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '7_nucleosome_free'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '8_tss_count'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '9_call_peak'), exist_ok=True)

# TODO: For now we have no report file
with open(os.path.join(ROOT_OUT_DIR, REPORT_STEP, 'report.html'), 'w') as r_file:
    r_file.write("<h1>The pipeline has not ended yet</h1>")

# //{PYTHON} {SCRIPTS}/PrepareFilesToReport.py --pipeline-dir {ROOT_OUT_DIR} --output-dir {params.output_dir} --samples {SAMPLES_LIST} --samples-deseq {SAMPLES_DESEQ_LIST} --factors no-deseq --batches no-deseq --run-id {RUN_ID} --logFile {log.report}
# //{PYTHON} {SCRIPTS}/run-fastqc-report-table.py --fastqc-dir {params.fastqc_dir} --output-file-base {params.fastqc_report}
# //{PYTHON} {SCRIPTS}/ReportsCounts.py --pipeline-dir {ROOT_OUT_DIR} --output {params.output_dir}/counts_all_steps.txt --samples {SAMPLES_LIST} --logFile {log.counts}
