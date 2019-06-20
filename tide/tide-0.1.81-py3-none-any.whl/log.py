import datetime
import filter as Filter
from config import Config
from logging_decorator import logging

LOGGING_SETTINGS = Config().get()["settings"]["logging"]
USE_SESSION_LOG_FILE = LOGGING_SETTINGS["use_session_log_file"]
SESSION_LOG_FILENAME = LOGGING_SETTINGS["session_log_filename"]
SESSION_BUFFER_NAME = LOGGING_SETTINGS["session_buffer_name"]
ADD_TIMESTAMP = LOGGING_SETTINGS["add_timestamp"]

if USE_SESSION_LOG_FILE:
    LOG_FILE_HANDLE = open(SESSION_LOG_FILENAME, "w+")

@logging
def write_to_log(log_string):
    if USE_SESSION_LOG_FILE:
        if ADD_TIMESTAMP:
            LOG_FILE_HANDLE.write("--- {0} ---".format(datetime.datetime.utcnow()) + "\n")
        LOG_FILE_HANDLE.write(log_string)
    log_lines = Filter.filter_string(log_string, SESSION_BUFFER_NAME)
    full_cache = Config().get()["internal"]["buffer_caches"][SESSION_BUFFER_NAME]
    if ADD_TIMESTAMP:
        full_cache.append("--- {0} ---".format(datetime.datetime.utcnow()))
    full_cache.extend(log_lines)
    Config().get()["internal"]["buffer_caches"][SESSION_BUFFER_NAME] = full_cache
