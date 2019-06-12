include: 'transcriptome_consts.py'

if not config:
    configfile: os.path.join(os.getcwd(), 'config-rnaseq.yaml')

STRANDED = config['stranded_protocol']
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

REPORT_STEP = '4_reports'
COMMANDS_LOG_SED = 'commands_log_' + RUN_ID + '.txt'

os.makedirs(ROOT_OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, 'Advanced_analysis'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, LOG_DIR_NAME), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, REPORT_STEP), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, REPORT_STEP, DIR_REPORT_NAME), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '1_cutadapt'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '2_fastqc'), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, '3_mapping'), exist_ok=True)

with open(os.path.join(ROOT_OUT_DIR, REPORT_STEP, DIR_REPORT_NAME, 'report.html'), 'w') as r_file:
    r_file.write("<h1>The pipeline has not ended yet</h1>")
