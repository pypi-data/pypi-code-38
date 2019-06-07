import sys
from  os import path
import argparse
import logging
import sqlite3
import glob
import hashlib

from typing import List, Dict
from pprint import pprint, pformat

from . config_parser import ParserConfigException, \
    VERBOSITY, LOG_LEVELS, CONF_FILE, \
    LOG_FILES, LOG_PATTERN, DATABASE_PATH, \
    WHITE_LIST, \
    JUDGMENT, RULES, \
    BOT_REQUEST, MAX_REQUEST, INTERVAL_SECONDS, \
    EXECUTION, SCRIPT, \
    parse_config_file

from . import log_parser
from . import judgment
from . import execution
from . import db_connection


LOGGER = logging.getLogger(__name__)

# work-flow
# 1. suche alle IP in Logfile nach Merkmale eines Angriff
# 2. generiert UFW Befehlen aus der IPs im Schritte 1
# 3. gebe die Befehlen aus, oder sonstiges weiter Verarbeitung

# CLI options:

# [judgment]

# []

_parser = None


def main():
    global _parser
    argv = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument(f"{CONF_FILE}", type=str, nargs="?",
                        help="Configuration file, configuration must be given by a configuration file "
                        f"(the positional argument {CONF_FILE}). The Debug level can be changed by "
                        f"optional argument --{VERBOSITY}.")

    parser.add_argument("-v", f"--{VERBOSITY}",
                        choices=LOG_LEVELS,
                        help="how much information is printed out during processing log files")
    _parser = parser
    cli_arg = vars( parser.parse_args(argv[1:]) )
    verbosity = cli_arg[VERBOSITY]
    if verbosity is not None:
        apply_log_config(verbosity)
    file_based_config = parse_config_file(cli_arg[CONF_FILE])
    if verbosity is not None:
        file_based_config[VERBOSITY] = verbosity
    if logging.getLogger("root").isEnabledFor(logging.DEBUG): LOGGER.debug(pformat(file_based_config))
    validate_config(file_based_config)
    try:
        apply_log_config(file_based_config[VERBOSITY])
        return analyse_log_files(file_based_config)
    except judgment.JudgmentException as ex:
        print(ex, file=sys.stderr)


def apply_log_config(verbosity: str):
    log_level = logging.getLevelName(verbosity)
    logging.getLogger().setLevel(level=log_level)
    logging.basicConfig(
        format='%(relativeCreated)d %(levelname)s %(module)s : %(message)s',
        datefmt='%H:%M:%S',
    )
    LOGGER.info("Verbosity: %s %d", verbosity, log_level)


def validate_config(config: Dict):
    if LOG_FILES not in config:
        raise ParserConfigException("Log files are not configured")


# TODO: test this method
def analyse_log_files(config: Dict):
    log_files = expand_log_files(config[LOG_FILES])
    conn = db_connection.get_connection(config[DATABASE_PATH])
    log_files = filter_processed_files(log_files, conn)
    LOGGER.info("Analyse %d file(s)", len(log_files))
    judge = construct_judgment(config)
    executor = execution.FileBasedUWFBlock(config[EXECUTION][0][RULES][SCRIPT])
    executor.begin_execute()
    log_pattern = config[LOG_PATTERN]
    i = 0
    try:
        for file_path in log_files:
            LOGGER.info("Analyse file %s", file_path)
            update_processed_file(file_path[0], file_path[1], conn)
            logs = log_parser.parse_log_file(file_path[1], log_pattern)
            for log in logs:
                i += 1
                LOGGER.debug("                       [%d] Process `%s'", i, log)
                blocked, cause = judgment.is_ready_blocked(log, conn)
                if blocked:
                    LOGGER.info("IP %s is ready blocked", log.ip_str)
                else:
                    deny, cause = judge.should_deny(log, i)
                    if deny:
                        network = judgment.lookup_ip(log.ip_str)
                        log.network = network
                        executor.block(log, cause)
    except KeyboardInterrupt:  # Will not work with python -m cProfile
        LOGGER.warning("Stop processing log files")
        LOGGER.info("current log files: {}".format(file_path))
        LOGGER.info("Write ready processed log entries to files")
        executor.end_execute()
        try:
            conn.close()
        except Exception as ex:
            LOGGER.warning("Cannot close Sql DbConnection {}", ex)
        return 1
    executor.end_execute()
    return 0


def expand_log_files(config_log_file: List[str]) -> List[str]:
    log_files = []
    for p in config_log_file:
        expand_path = glob.glob(p)
        LOGGER.debug("expand glob '%s' to %s", p, expand_path)
        if len(expand_path) == 0:
            LOGGER.warn("Glob path '%s' cannot be expanded to any real path", p)
        log_files = log_files + expand_path
    return log_files


def apache_access_log_file_chronological_decode(file_name):
    base_name = path.basename(file_name).split('.')
    return -int(base_name[2]) if len(base_name) > 2 else 0


def filter_processed_files(log_files:List[str], conn: sqlite3.Connection, key=apache_access_log_file_chronological_decode)->List[str]:
    processed_files = []
    try:
        with conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            for row in c.execute("SELECT content_hash, path FROM processed_log_file"):
                processed_files.append(row[0])
    except sqlite3.OperationalError:
        LOGGER.warning(
            "Cannot read table processed_files in database so use all expanded files")
    log_files_hash = map(lambda f: (content_hash(f), f), log_files)
    effective_log_files = sorted(filter(lambda hf: hf[0] not in processed_files, log_files_hash), key=lambda hf: key(hf[1]))
    return list(effective_log_files)


def update_processed_file(hash_content, file_path, conn: sqlite3.Connection):    # TODO: UNIT TEST
    if file_path.endswith("gz"):
        try:
            with conn:
                c = conn.cursor()
                c.execute("""
                    INSERT OR REPLACE INTO processed_log_file (content_hash, path) 
                    VALUES (?,
                        COALESCE((SELECT path FROM processed_log_file WHERE content_hash = ? AND path = ?), ?)
                    )
                    """,
                    (hash_content,hash_content,file_path, file_path)
                )
        except sqlite3.OperationalError as ex:
            LOGGER.warning("Cannot update table processed_files %s", ex)
    else:
        LOGGER.info("File %s is not compressed, so not mark it as processed", file_path)


def content_hash(file_path):
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def construct_judgment(config) -> judgment.AbstractIpJudgment:
    judgments_chain = config[JUDGMENT] if JUDGMENT in config else []
    if len(judgments_chain) < 1:
        _parser.error(f"At least one entry in {JUDGMENT} must be configured")
    list_of_judgments = []
    for judge in judgments_chain:
        list_of_judgments += [judgment_by_name(judge, config)]
    LOGGER.info("Use %d judgments", len(list_of_judgments))
    return judgment.ChainedIpJudgment(db_connection.get_connection(config[DATABASE_PATH]), list_of_judgments, config[WHITE_LIST])


def judgment_by_name(judge, config):
    name = judge['name']
    rules = judge[RULES]
    if name == "path-based-judgment":
        bot_request_path = rules[BOT_REQUEST] if BOT_REQUEST in rules else []
        if len(bot_request_path) > 0:
            return judgment.PathBasedIpJudgment(bot_request_path)
        else:
            _parser.error(f"At least one path in {BOT_REQUEST} must be configured if Judgment {name} is used")
    elif name == "time-based-judgment":
        if DATABASE_PATH in config:
            database_path = config[DATABASE_PATH]
            conn = db_connection.get_connection(database_path)
            max_request = rules[MAX_REQUEST] if MAX_REQUEST in rules else 500
            interval = rules[INTERVAL_SECONDS] if INTERVAL_SECONDS in rules else 60
            return judgment.TimeBasedIpJudgment(conn, max_request, interval)
        else:
            _parser.error(f"A SQLite database ({DATABASE_PATH}) must be configured in global section if Judgment {name} is used")
    else:
        raise ParserConfigException(f"Unknown judgment {name}")


#############################################################################
#############################################################################
#############################################################################
def init_db():
    global _parser
    argv = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path",
                        help="Path to an Sqlite Database")
    _parser = parser
    cli = parser.parse_args(argv[1:])
    db_path = cli.db_path
    judgment.init_database(db_path)
    pass