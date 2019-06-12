import os
from glob import glob

from functions import *
from creature import *

if not config:
    configfile: os.path.join(os.getcwd(), 'config-chipseq.yaml')

# if 'TEST' in config:
#    SCRIPTS = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/bin"
#    TEMPLATES = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/lib/python2.7/site-packages/ngs-snakemake"
#    PYTHON = "/home/labs/bioservices/services/test_env/python27-ve-ngs-snakemakeTest/bin/python"
# else:
#    SCRIPTS = "/apps/RH7U2/scripts/bbcu-python-packages/python27-ve-ngs-snakemake/bin"
#    TEMPLATES = "/apps/RH7U2/scripts/bbcu-python-packages/python27-ve-ngs-snakemake/lib/python2.7/site-packages/ngs-snakemake"
#    PYTHON = "/apps/RH7U2/scripts/bbcu-python-packages/python27-ve-ngs-snakemake/bin/python"


JOB_NAME = config['job_name']
RUN_ID=config['run_id']
BOWTIE2_EXE = config['bowtie2_exe']
FASTQ_DIR = config['fastq_dir']
OUTPUT_DIR= config['output_dir']
SCRIPTS = config['scripts']
TEMPLATES = config['templates']
PYTHON = config['python']
GENOME_INDEX=config['genomeIndx']
GENOME=config['genome']
CON_VS_TREAT= config['con_vs_treat']
FASTQC_EXE=config['fastqc_exe']
MACS2_EXE=config['macs_exe']
SAMTOOLS_EXE=config['samtools_exe']
MULTIQC_EXE=config['multiQC_exe']
LOG_DIR_NAME = 'logs_'+ JOB_NAME
CUTADAPT_EXE = config['cutadapt_exe']
CHR_INFO = config['chr_info']
NGS_PLOT_EXE = config['ngs_plot_exe'] if config['ngs_plot_exe'] else ''

#SAMPLES = [dir for dir in os.listdir(FASTQ_DIR) if os.path.isdir(
 #   os.path.join(FASTQ_DIR, dir)) and dir != 'FastQCinput' and dir != 'Reports' and dir != 'Stats'] # better code exist refael needs to send me

creature = os.path.basename(CHR_INFO).split('.')[0]
required_parameters = ['NGSPLOT_GENOME', 'MACS_GENOME_SIZE']
NGSPLOT_GENOME, MACS_GENOME_SIZE = get_creature_parameters(creature, NGS_PLOT_EXE, *required_parameters)
SAMPLES, COMBINE_INPUT_FILES = get_samples(FASTQ_DIR)
FASTQ_DIR_ANALYSIS = concatenate_fastq_files(OUTPUT_DIR, FASTQ_DIR, SAMPLES) if COMBINE_INPUT_FILES else FASTQ_DIR
PAIRED_END = is_paired_end(FASTQ_DIR_ANALYSIS, SAMPLES)
CUTADAPT_TEMPLATE = cutadapt_template(OUTPUT_DIR, PAIRED_END)

ADAPTOR_RAW = config['adaptor']
pattern = re.compile(r'\s+')
ADAPTOR = re.sub(pattern, '', ADAPTOR_RAW)
ADAPTORS = ADAPTOR.split(',')
if PAIRED_END and len(ADAPTORS) < 2:
    raise IOError("The number of adapters is not equal to the numbers of the reads")
if len(ADAPTORS) < 2:
    ADAPTORS.append("")
ADAPTOR1 = ADAPTORS[0]
ADAPTOR2 = ADAPTORS[1]

COMBINE_SAMPLES_DB, TREATMENT, CONTROL = get_treat_vs_control(phenodata_file=CON_VS_TREAT) if CON_VS_TREAT else ({}, None, None)

for sample in SAMPLES:
    file_name = glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, "*R*"))
    for f in file_name:
        if f.endswith('.gz'):
            os.system("gunzip %s" % f)

def fastq_r1(wildcards):
    sample = wildcards.sample
    print(sample)
    return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*_R1*'))[0]


def fastq_r2(wildcards):
    sample = wildcards.sample
    print (sample)
    return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*_R2*'))[0]


def get_fastq(paired_end):
    return [fastq_r1, fastq_r2] if paired_end else [fastq_r1]


#def rule_6_out(output_dir, control):
#    return os.path.join(output_dir, '6_peaks_prediction', '{sample}_peaks.narrowPeak,') + \
#           os.path.join(output_dir, '6_peaks_prediction', '{sample}_treat_pileup.bdg') if not control \
#           else os.path.join(output_dir, '6_peaks_prediction', '{treat}_vs_{control}_peaks.narrowPeak,') + \
#           os.path.join(output_dir, '6_peaks_prediction', '{treat}_vs_{control}_treat_pileup.bdg')
#
#def rule_9_out(output_dir,control):
#    return os.path.join(output_dir, '9_BigWig', '{sample}_treat_pileup.bw') if not control else os.path.join(output_dir, '9_BigWig', '{treat}_vs{control}_treat_pileup.bw')
# 
#
#RULE_6_OUTPUT = rule_6_out(OUTPUT_DIR, CONTROL)
#RULE_9_OUTPUT = rule_9_out(OUTPUT_DIR, CONTROL)

def if_control(control):
    return '{sample}' if not control else '{treat}_vs_{control}'
    
RULE_6_and_9_OUTPUT = if_control(CONTROL)

#cwd = os.getcwd()
#with open(os.path.join(cwd,CON_VS_TREAT), 'r') as f: #what should be the path to the pheno data file 
#    contents = [x.split() for x in f.readlines() if x.split() != []]
#samples = list(zip(*contents))
#TREATMENT = samples[0][1:]
#CONTROL= samples[1][1:]


os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, LOG_DIR_NAME), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, '1_cutadapt'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, '2_fastqc'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, '3_multiQC'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, '4_alignment'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, '5_samtools'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, '6_peaks_prediction'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, '7_peaks_annotation'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, '8_graphs'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, '9_BigWig'), exist_ok=True)


