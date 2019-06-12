import datetime
import logging
import os

from fastqcReports.settings import PROJECT_NAME

FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

root_logger = logging.getLogger(PROJECT_NAME)
root_logger.setLevel(logging.DEBUG)

def add_run_log_handlers(logs_dir):
    # create handler for outputting to console
    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.INFO)
    stderr_handler.setFormatter(FORMATTER)
    root_logger.addHandler(stderr_handler)

    # create application log file
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(logs_dir, '%s.%s.log' %(PROJECT_NAME, now))
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(FORMATTER)
    root_logger.addHandler(file_handler)

    # create error log file
    error_log_filename = os.path.join(logs_dir, 'error.%s.log' %(now,))
    error_file_handler = logging.FileHandler(error_log_filename)
    error_file_handler.setLevel(logging.WARNING)
    error_file_handler.setFormatter(FORMATTER)
    root_logger.addHandler(error_file_handler)
