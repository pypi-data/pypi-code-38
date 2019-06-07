# config
DEBUG = False
FROM_S3 = True
UPLOAD_S3 = True
USE_COMPILED_CODE = False

ALLOWED_CODE_EXTENSION = ['.so', '.pyd', '.py']

ALLOWED_DATASET_EXTENSION = ['.tfrecords', '.csv', '.txt']

CODE_DIR_NAME = 'code'
DATASET_DIR_NAME = "dataset"
OUTPUT_DIR_NAME = "output"
LOG_DIR_NAME = 'log'

TF_CONFIG = 'TF_CONFIG'

MODEL_WIN_OUT_DIR = ".model.win.out"
MODEL_LINUX_OUT_DIR = ".model.linux.out"

EXTENSION_TAR_GZ = '.tar.gz'

DATASET_TAR_GZ = 'dataset.tar.gz'

# OS types
LINUX = "linux"
WIN = "win"

# File marker name
WORKER_FAILED_MARKER = "worker_run_failed"

REQUIREMENTS_TXT = "requirements.txt"

# TEMP variables
NUMBER_GPU_WORKER = 4
NUMBER_CPU_WORKER = 1

# Master server
DEFAULT_MASTER_SERVER = "http://dtf-masterserver-dev.us-west-1.elasticbeanstalk.com"

# Job contents
JOB_CONTENT_TYPE_CODE = "code"
JOB_CONTENT_TYPE_CUSTOM_DATASET = "dataset"
JOB_CONTENT_TYPE_KNOWN_DATASETS = "known_datasets"
JOB_CONTENT_TYPE_OUTPUT = "output"
JOB_CONTENT_TYPE_SUPPORTED = [JOB_CONTENT_TYPE_CODE,
                              JOB_CONTENT_TYPE_CUSTOM_DATASET,
                              JOB_CONTENT_TYPE_OUTPUT]

# Container settings
DC_WORKER_USER_ID = 9999

# Db settings
DB_CONNECTION_USER_NAME = "USER_NAME"
DB_CONNECTION_DB_NAME = "DB_NAME"
DB_CONNECTION_PASSWORD = "PASSWORD"
DB_CONNECTION_HOST = "HOST"
DB_CONNECTION_PORT = "PORT"

DEFAULT_DB_CONNECTION = {
    DB_CONNECTION_USER_NAME: "dcworker_db_user",
    DB_CONNECTION_DB_NAME: "dcworker_db",
    DB_CONNECTION_PASSWORD: "dcworker_db_user",
    DB_CONNECTION_HOST: "localhost",
    DB_CONNECTION_PORT: 5432
}

SUPPORTED_GPUS = [
    "NVIDIA TITAN V",
    "NVIDIA TITAN Xp",
    "NVIDIA TITAN X",
    "GeForce GTX 1080 Ti",
    "GeForce GTX 1080",
    "GeForce GTX 1070",
    "GeForce GTX 1060",
    "GeForce GTX 1050",
    "GeForce GTX TITAN X",
    "GeForce GTX TITAN Z",
    "GeForce GTX TITAN Black",
    "GeForce GTX TITAN",
    "GeForce GTX 980 Ti",
    "GeForce GTX 980",
    "GeForce GTX 970",
    "GeForce GTX 960",
    "GeForce GTX 950"
]