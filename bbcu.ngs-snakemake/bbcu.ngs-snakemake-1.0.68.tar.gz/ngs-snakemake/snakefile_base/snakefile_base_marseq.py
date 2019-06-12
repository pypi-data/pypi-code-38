include: 'transcriptome_consts.py'

if not config:
    configfile: os.path.join(os.getcwd(), 'config-marseq.yaml')

REPORT_STEP = '10_reports'
COMMANDS_LOG_SED = 'commands_log_' + RUN_ID + '.txt'

DIR_REPORT_UMI_COUNTS_NAME = 'report_umi_counts_output_' + RUN_ID

os.makedirs(ROOT_OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, 'Advanced_analysis'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, LOG_DIR_NAME), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, REPORT_STEP), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, REPORT_STEP, DIR_REPORT_NAME), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '1_combined_fastq'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '2_cutadapt'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '3_fastqc'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '4_mapping'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '5_move_umi'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '6_count_reads'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '7_mark_dup'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '8_dedup_counts'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '9_umi_counts'), exist_ok=True)

with open(os.path.join(ROOT_OUT_DIR, REPORT_STEP, DIR_REPORT_NAME, 'report.html'), 'w') as r_file:
    r_file.write("<h1>The pipeline has not ended yet</h1>")
