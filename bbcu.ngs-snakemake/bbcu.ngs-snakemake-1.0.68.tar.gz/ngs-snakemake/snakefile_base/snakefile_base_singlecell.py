import os

from functions import *


if not config:
    configfile: os.path.join(os.getcwd(), 'config-singlecell.yaml')

RUN_ID = str(config['run_id'])
RAW_JOB_NAME = str(config['job_name'])
JOB_NAME = re.sub('[^0-9a-zA-Z]+', '_', RAW_JOB_NAME)
FASTQ_DIR = config['fastq_dir']
ROOT_OUT_DIR = config['output_dir']
CELLRANGER_TRANSCRIPTOME = config["cellranger_transcriptom"]
CELLRANGER_EXE = config["cellranger_exe"]
SCRIPTS = config['scripts']
TEMPLATES = config['templates']
PYTHON = config['python']
MAX_THREADS_NUM = int(config['max_threads_num'])

if 'TEST' in config:
   SCRIPTS = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/bin"
   TEMPLATES = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/lib/python2.7/site-packages/ngs-snakemake"
   PYTHON = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/bin/python"

samples_fastq = os.path.join(FASTQ_DIR, 'outs', 'fastq_path')
SAMPLES = [dir for dir in os.listdir(samples_fastq) if os.path.isdir(
    os.path.join(samples_fastq, dir)) and dir != 'FastQCinput' and dir != 'Reports' and dir != 'Stats']
LOG_DIR_NAME = 'logs_' + RUN_ID
REPORT_STEP = '3_reports'

os.makedirs(ROOT_OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, 'Advanced_analysis'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, LOG_DIR_NAME), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '1_count'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '2_aggregation'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, REPORT_STEP), exist_ok=True)

