import re

from functions import *
from creature import *

if not config:
    if os.path.isfile(os.path.join(os.getcwd(), 'config-marseq.yaml')):
        configfile: os.path.join(os.getcwd(), 'config-marseq.yaml')
    elif os.path.isfile(os.path.join(os.getcwd(), 'config-rnaseq.yaml')):
        configfile: os.path.join(os.getcwd(), 'config-rnaseq.yaml')

RUN_ID = str(config['run_id'])
RAW_JOB_NAME = str(config['job_name'])
JOB_NAME = re.sub('[^0-9a-zA-Z]+', '_', RAW_JOB_NAME)
SCRIPTS = config['scripts']
TEMPLATES = config['templates']
PYTHON = config['python']
CONDA_ROOT = config['conda_root'].replace('/', '\/')
RSCRIPT = config['Rscript'].replace('/', '\/')
R_LIB_PATHS = config['R_lib_paths'].replace('/', '\/')
CUTADAPT_EXE = config['cutadapt_exe']
FASTQC_EXE = config['fastqc_exe']
STAR_EXE = config['star_exe']
SAMTOOLS_EXE = config['samtools_exe']
NGS_PLOT_EXE = config['ngs_plot_exe'] if config['ngs_plot_exe'] else ''
GS_EXE = config['gs_exe']
HTSEQ_COUNT_EXE = config['htseq_count_exe']
INDEX = config['my_star_index']
INDEX_PATH = INDEX.replace('/', '\/')
GTF = config['gtf']
GTF_PATH = GTF.replace('/', '\/')
ROOT_OUT_DIR = config['output_dir']
ROOT_OUT_DIR_SED = ROOT_OUT_DIR.replace('/', '\/')
FASTQ_DIR = config['fastq_dir']
FASTQ_DIR_SED = FASTQ_DIR.replace('/', '\/')
MAX_THREADS_NUM = int(config['max_threads_num'])
JAVA_FOR_FASTQ = os.path.join(config['conda_root'], 'envs/utap/bin/java')

if 'TEST' in config:
   SCRIPTS = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/bin"
   TEMPLATES = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/lib/python2.7/site-packages/ngs-snakemake"
   PYTHON = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/bin/python"

SAMPLES, COMBINE_INPUT_FILES = get_samples(FASTQ_DIR)
FASTQ_DIR_ANALYSIS = concatenate_fastq_files(ROOT_OUT_DIR, FASTQ_DIR, SAMPLES) if COMBINE_INPUT_FILES else FASTQ_DIR
PAIRED_END = is_paired_end(FASTQ_DIR_ANALYSIS, SAMPLES)
DIR_REPORT_NAME = 'report_output_' + RUN_ID
LOG_DIR_NAME = 'logs_' + RUN_ID
CUTADAPT_TEMPLATE = cutadapt_template(ROOT_OUT_DIR, PAIRED_END)

creature = os.path.basename(GTF).split('.')[0]
required_parameters = ['NGSPLOT_GENOME', 'INTERMINE_WEB_QUERY', 'INTERMINE_WEB_BASE', 'MINE_CREATURE', 'ANNOTAT_TYPE', 'GENE_DB_URL', 'RUN_NGSPLOT']
NGSPLOT_GENOME, INTERMINE_WEB_QUERY, INTERMINE_WEB_BASE, MINE_CREATURE, ANNOTAT_TYPE, GENE_DB_URL, RUN_NGSPLOT = get_creature_parameters(creature, NGS_PLOT_EXE, *required_parameters)


# Must to implement these functions here because they need to get FASTQ_DIR_ANALYSIS parameter that cannot to be passed to the function
def fastq_r1(wildcards):
    sample = wildcards.sample
    return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*_R1*'))[0]


def fastq_r2(wildcards):
    sample = wildcards.sample
    return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*_R2*'))[0]


def get_fastq(paired_end):
    return [fastq_r1, fastq_r2] if paired_end else [fastq_r1]


SAMPLE_DESC_CSV = 'sample_desc_' + RUN_ID + '.csv'
COMPARISONS_CSV = 'comparisons_' + RUN_ID + '.csv'


if 'factors_file' in config.keys() and ('samples' in config.keys() or 'factors' in config.keys()):
    raise Exception(
        'Invalid config.yaml file: You use with \'factors_file\' and \'sample\' or \'factors\' togther in config file, you can use only with factors_file alone or sample and factors')

SAMPLES_DESEQ = []
FACTORS = []
BATCHES = []

try:
    SAMPLES_DESEQ_FILE = config['factors_file']
    with open(SAMPLES_DESEQ_FILE) as ff:
        for line in ff:
            line = line.rstrip()
            try:
                sample, factor, batch = line.split('\t')
                BATCHES.append(batch)
            except ValueError:
                sample, factor = line.split('\t')
                if not BATCHES:
                    BATCHES.append('no-deseq')
            SAMPLES_DESEQ.append(sample)
            FACTORS.append(factor.strip())
except KeyError:  # No factors_file in config
    try:
        FACTORS += config['factors']
        BATCHES += config['batches']
        SAMPLES_DESEQ = config['samples_deseq']
    except KeyError:
        FACTORS.append('no-deseq')
        BATCHES.append('no-deseq')
        SAMPLES_DESEQ.append('no-deseq')

# reorder SAMPLES according to SAMPLES_DESEQ
TEMP_SAMPLES = []
for i in SAMPLES_DESEQ:
    if i != 'no-deseq':
        TEMP_SAMPLES.append(i)
        SAMPLES.remove(i)
TEMP_SAMPLES.extend(SAMPLES)
SAMPLES = TEMP_SAMPLES

SAMPLES_LIST = ' '.join(SAMPLES)
SAMPLES_DESEQ_LIST = ' '.join(SAMPLES_DESEQ)
FACTORS_LIST = ' '.join(FACTORS)
BATCHES_LIST = ' '.join(BATCHES)

FACTOR_OBJ = ''
unique_factor = sorted(list(set(FACTORS)))
try:
    FACTOR_OBJ = unique_factor[0] + '_or_' + unique_factor[1]
except IndexError:
    FACTOR_OBJ = ''
