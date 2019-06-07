import sys, os
import toml
from typing import Dict

# cli
# Verbosity of program
VERBOSITY = "verbosity"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
CONF_FILE = "config_file"


# Apache Log file to be analysed
LOG_FILES = "log_files"
LOG_PATTERN = "log_pattern"
DATABASE_PATH = "database_path"

# Whitelist
WHITE_LIST = "white_list"

# Judgments configuration
JUDGMENT = "judgment"
RULES = "rules"

# Configuration keys for path-based-judgment
BOT_REQUEST = "bot_request"

# Configuration keys for time based judgment
MAX_REQUEST = "max_request"
INTERVAL_SECONDS = "interval_seconds"

# execute
EXECUTION = "execution"
SCRIPT = "script"


def parse_config_file(file_path:str) -> Dict:
    try:
        return toml.load(file_path)
    except IOError as ex:
        raise ParserConfigException(f"File {file_path} not exist (working dir {os.getcwd()})", ex)


class ParserConfigException(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super(ParserConfigException, self).__init__(message)

