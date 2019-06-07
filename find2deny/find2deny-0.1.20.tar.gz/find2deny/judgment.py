# -*- encoding:utf8 -*-

import functools
import re
import urllib
import urllib.error
from abc import ABC, abstractmethod
from typing import List

import ipaddress
import pendulum
from datetime import datetime
import sqlite3
import logging

from ipwhois import IPWhois, exceptions
from importlib_resources import read_text

from . log_parser import LogEntry, DATETIME_FORMAT_PATTERN
from . import log_parser
from . import db_connection


LOGGER = logging.getLogger(__name__)


def init_database(sqlite_db_path: str):
    sql_script = read_text("find2deny", "log-data.sql")
    try:
        with db_connection.get_connection(sqlite_db_path) as conn:
            conn.executescript(sql_script)
    except sqlite3.OperationalError as ex:
        raise JudgmentException(f"Cannot init database in sqlite file {sqlite_db_path}", error=ex)
    pass


def is_ready_blocked(log_entry: LogEntry, conn: sqlite3.Connection) -> (bool, str):
    @functools.lru_cache(maxsize=2024)
    def __cached_query(ip: int):
        try:
            with conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*), cause_of_block cause_of_block FROM block_network WHERE ip = ?", (ip,))
                row = c.fetchone()
                ip_count = row[0]
                cause = row[1]
                return (ip_count == 1), cause
        except sqlite3.OperationalError as ex:
            raise JudgmentException("Access to Sqlite Db caused error; Diagnose: use `find2deny-init-db' to create a Database.", errors=ex)
    return __cached_query(log_entry.ip)


def update_deny(ip_network: str, log_entry: LogEntry, judge:str, cause_of_block:str, sqlite_db_path: str):
    insert_cmd = "INSERT OR IGNORE INTO block_network (ip, ip_network, block_since, judge, cause_of_block) VALUES (?, ?, ?, ?, ?)"
    try:
        with db_connection.get_connection(sqlite_db_path) as conn:
            conn.execute(insert_cmd, (log_entry.ip, ip_network, local_datetime(), judge, cause_of_block))
    except sqlite3.OperationalError as ex:
        raise JudgmentException("Access to Sqlite Db caused error; Diagnose: use `find2deny-init-db' to create a Database.",errors=ex)
    LOGGER.info("(%s) add %s to blocked network", log_entry.ip_str, ip_network)
    pass


class AbstractIpJudgment(ABC):

    @abstractmethod
    def should_deny(self, log_entry: LogEntry, entry_count: int=0) -> (bool, str):
        """
            check if the given ip should be blocked
        :param log_entry: in integer
        :param entry_count: how many entries are processed since python script starts
        :return: (True, cause) if the ip should be blocked, (False,cause) if the firewall should allow ip
        """
        pass


class ChainedIpJudgment(AbstractIpJudgment):

    def __init__(self, conn:sqlite3.Connection, chains: List[AbstractIpJudgment], white_list: List[str] = None):
        self.__white_list:List[str] = white_list or []
        self.__judgment = chains
        # self.__log_db_path = log_db_path
        self.conn = conn # db_connection.get_connection(self.__log_db_path)

    def should_deny(self, log_entry: LogEntry, entry_count=0) -> bool:
        white_list_fn = make_ip_check_fn(log_entry.ip_str)
        white_lister = next((item for item in self.__white_list if white_list_fn(item)), None)
        if white_lister:
            return False, "White listed by {}".format(white_lister)
        else:
            deny, cause = is_ready_blocked(log_entry, self.conn)
            if deny:
                return deny, cause
            for judgment in self.__judgment:
                deny, cause = judgment.should_deny(log_entry, entry_count)
                if deny:
                    ip_network = lookup_ip(log_entry.ip)
                    update_deny(ip_network, log_entry,judgment.__class__.__name__, cause, self.conn)
                    return True, cause
            return False, None


def make_ip_check_fn(ip):
    return lambda white_list: \
        white_list == ip or is_ip_matched_network(ip, white_list) or is_ip_in_white_listed_network(ip, white_list)


def is_ip_in_white_listed_network(ip, white_list_network):
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(white_list_network)
    except Exception:
        return False


def is_ip_matched_network(ip, white_list_ip_reg):
    pattern = re.compile(white_list_ip_reg)
    return pattern.match(ip)


class PathBasedIpJudgment(AbstractIpJudgment):
    """

    """
    def __init__(self, bot_path: set = None):
        self._bot_path = bot_path if bot_path is not None else {}
        pass

    def should_deny(self, log_entry: LogEntry, entry_count: int = 0) -> (bool, str):
        try:
            request_path = log_entry.request.split(" ")[1]
            request_resource = next((r for r in self._bot_path if request_path.startswith(r)), None)
            blocked = request_resource is not None
            cause = None
            if blocked:
                cause = "{} tried to access {} which matches non-existing resource {}".format(
                         log_entry.ip_str, request_path, request_resource)
                LOGGER.info(cause)
            return blocked, cause
        except IndexError:
            if log_entry.request == "-":
                return False, None
            else:
                cause = "{}-s  request >>{}<< is not conform to HTTP".format(
                             log_entry.ip_str, log_entry.request)
                LOGGER.info(cause)
                return True, cause

    def __str__(self):
        return "PathBasedIpJudgment/bot_path:{}".format(self._bot_path)


class TimeBasedIpJudgment(AbstractIpJudgment):

    def __init__(self, sqlite_db_path:str, allow_access: int = 10, interval_second: int = 10):
        """
        :param path: path to a SQLite Database file
        :param allow_access: number of access in a given time interval (next parameter)
        :param interval_second: time interval in seconds
        """
        self.allow_access = allow_access
        self.interval = interval_second
        self._sqlite_db_path = sqlite_db_path
        self.conn = db_connection.get_connection(self._sqlite_db_path)
        self.count_ip = 0

    def __del__(self):
        pass

    def should_deny(self, log_entry: LogEntry, entry_count: int = 0) -> bool:
        """

        :param log_entry:
        :param entry_count:
        :return:
        """
        self.count_ip = entry_count
        if not self._ready_processed(log_entry):
            return self._make_block_ip_decision(log_entry)
        else:
            return self._lookup_decision_cache(log_entry)

    def _ready_processed(self, log_entry: LogEntry) -> bool:
        # TODO read table processed_log_ip to get Info about log_entry
        sql_cmd = "SELECT count(*) FROM processed_log_ip WHERE ip = ? AND line = ? AND log_file = ?"
        try:
            with self.conn as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute(sql_cmd, (log_entry.ip, log_entry.line, log_entry.log_file))
                row = c.fetchone()
            if not row or row is None:
                return False
            else:
                LOGGER.debug("found %d processed ip in database log for entry %s ", row[0], log_entry)
                ip_count = row[0]
                return ip_count == 1
        except sqlite3.OperationalError:
            LOGGER.warning("Cannot make connection to database file %s", self._sqlite_db_path)
            return False

    def _make_block_ip_decision(self, log_entry: LogEntry) -> (bool, str):
        ip_int = log_entry.ip
        try:
            with self.conn as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("INSERT INTO processed_log_ip (ip, line, log_file) VALUES (?, ?, ?)",
                          (log_entry.ip, log_entry.line, log_entry.log_file))
                c.execute("SELECT ip, first_access, last_access, access_count FROM log_ip WHERE ip = ?",
                          (ip_int,))
                row = c.fetchone()
        except sqlite3.OperationalError as ex:
            raise JudgmentException(
                "Access to Sqlite Db caused error; Diagnose: use `find2deny-init-db' to create a Database.", errors=ex)

        if row is None:
            LOGGER.debug("IP %s not found in log_ip", log_entry.ip_str)
            self._add_log_entry(log_entry)
            LOGGER.info("    [%d] added %s to log_ip",self.count_ip, log_entry.ip_str)
            return False, None
        else:
            first_access = datetime.strptime(row['first_access'], DATETIME_FORMAT_PATTERN)
            LOGGER.debug("log time: %s  first access: %s", log_entry.time, first_access)
            delay = (log_entry.time - first_access).total_seconds()
            access_count = row['access_count'] + 1
            LOGGER.debug("%s accessed %s %s times in %d seconds", log_entry.ip_str, log_entry.request, access_count,
                         delay)
            limit_rate = self.allow_access / self.interval
            if delay >= 0:
                try:
                    access_rate = access_count / delay
                    if access_rate >= limit_rate and delay <= self.interval:
                        cause = "{} accessed server {}-times in {} secs which is too much for rate {} accesses / {}".format(
                            log_entry.ip_str, access_count, delay, self.allow_access, self.interval)
                        self._update_deny(log_entry, access_count)
                        LOGGER.info(cause)
                        return True, cause
                    else:
                        self._update_access(log_entry, access_count)
                        return False, None
                    pass
                except ZeroDivisionError as ex:
                    if access_count > self.allow_access:
                        self._update_deny(log_entry, access_count)
                        cause = "{} accessed server {} in less than 0 secs which is too much for rate {} accesses / {}".format(
                            log_entry.ip_str, access_count, delay, self.allow_access, self.interval)
                        LOGGER.info(cause)
                        return True, cause
                    else:
                        self._update_access(log_entry, access_count)
                        return False, None
            else:raise JudgmentException("Logfile is not sorted by modified date: first access: {} last access: {}".
                                        format(row['first_access'], log_entry.time))

    def _lookup_decision_cache(self, log_entry:LogEntry) -> (bool, str):
        try:
            with self.conn as conn:
                for row in conn.execute("SELECT count(*) as count_ip, cause_of_block FROM block_network WHERE ip = ?", (log_entry.ip,)):
                    pass
            count = row['count_ip']
            cause = row['cause_of_block'] or None
            return (count == 1), cause
        except sqlite3.OperationalError as ex:
            raise JudgmentException(
                "Access to Sqlite Db caused error; Diagnose: use `find2deny-init-db' to create a Database.", errors=ex)

    def _add_log_entry(self, log_entry: LogEntry):
        time_iso = log_entry['time'].strftime(DATETIME_FORMAT_PATTERN)
        sql_cmd = """INSERT INTO log_ip (ip, first_access, last_access, access_count) 
                                         VALUES (?, ?, ?, ?)"""
        try:
            with self.conn as conn:
                conn.execute(sql_cmd, (log_entry.ip,
                                       time_iso,
                                       time_iso,
                                       1)
                             )
        except sqlite3.OperationalError:
            LOGGER.warning("Cannot insert new log to log_ip")
        pass

    def _update_deny(self, log_entry: LogEntry, access_count: int):
        """
        :param log_entry:
        :param access_count:
        :return:
        """
        ip_network = lookup_ip(log_entry.ip)
        update_cmd = """UPDATE log_ip SET 
            ip_network = ?,
            last_access = ?,
            access_count = ?,
            status = 1
            WHERE ip = ?
        """
        try:
            with self.conn as conn:
                conn.execute(update_cmd, (ip_network, log_entry.iso_time, access_count, log_entry.ip))
        except sqlite3.OperationalError:
            LOGGER.warning("Cannot update log_ip")
        pass

    def _update_access(self, log_entry: LogEntry, access_count: int):
        """

        :param log_entry:
        :param access_count:
        :return:
        """
        try:
            update_cmd = "UPDATE log_ip SET last_access = ?,  access_count = ? WHERE ip = ?"
            with self.conn as conn:
                conn.execute(update_cmd, (local_datetime(), access_count, log_entry.ip))
            LOGGER.debug("update access_count of %s to %s", log_entry.ip_str, access_count)
        except sqlite3.OperationalError:
            print("Cannot update log_ip")
        pass

    def __str__(self):
        return "TimeBasedIpBlocker/database:{}".format(self._sqlite_db_path)


def local_datetime() -> str:
    return pendulum.now().strftime(DATETIME_FORMAT_PATTERN)


def lookup_ip(ip: str or int) -> str:
    str_ip = ip if isinstance(ip, str) else log_parser.int_to_ip(ip)
    return __lookup_ip(str_ip)


@functools.lru_cache(maxsize=10240)
def __lookup_ip(normed_ip: str) -> str:
    try:
        who = IPWhois(normed_ip).lookup_rdap()
        return who["network"]["cidr"]
    except (urllib.error.HTTPError, exceptions.HTTPLookupError, exceptions.IPDefinedError) as ex:
        LOGGER.warning("IP Lookup for %s fail", normed_ip)
        LOGGER.warning("return ip instead of network")
        LOGGER.debug(ex)
        return normed_ip


class JudgmentException(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super(JudgmentException, self).__init__(message)
