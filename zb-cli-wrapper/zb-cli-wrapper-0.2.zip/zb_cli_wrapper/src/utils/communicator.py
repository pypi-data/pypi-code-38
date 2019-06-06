#
# Copyright (c) 2019, Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import ipaddress
import threading
import logging
import time
import re
import string

class TimeoutError(Exception):
    pass

class CommandError(Exception):
    pass

class CommunicatorError(Exception):
    pass

class BaseCommunicator(threading.Thread):

    def __newline_handler(self, line):
        print(line)

    def __init__(self, conn, newline_handler=__newline_handler, read_size=128, wait_time=0.001):
        super(BaseCommunicator, self).__init__()

        self.daemon = True
        self.logger = logging.getLogger(__name__)

        self._conn = conn
        self._newline_handler = newline_handler
        self._read_size = read_size
        self._wait_time = wait_time

        self._line = ""

        self._reading_active = threading.Event()

    def __del__(self):
        self.stop()

    def run(self):
        self._reading_active.set()

        while self._reading_active.is_set():

            for c in self._conn.read(self._read_size):
                self._line += c

                if c == "\n":
                    log_line = self._line.encode("ascii", "ignore").decode("ascii", "ignore").strip("\r\n")
                    self.logger.debug("{}: Rcvd line: '{}'".format(self, log_line))

                    self._newline_handler(self._line)
                    self._line = ""

            time.sleep(self._wait_time)

    def write(self, b):
        try:
            log_data = b.encode('utf-8')
        except AttributeError:
            log_data = b
        self.logger.debug("{}: written: {}".format(self, log_data))
        return self._conn.write(b)

    def stop(self):
        self._reading_active.clear()
        self.join()

        self.logger.debug("Data left in the buffer: '{}'".format(self._line))

    def __repr__(self):
        return repr(self._conn)


class LineCommunicator(BaseCommunicator):

    ASYNC_LOGS = []

    def __newline_handler(self, line):
        if line == "\r\n":
            return

        self._lines_lock.acquire()

        if self.is_async(line):
            self._async_lines.append(line)
        else:
            self._lines.append(line)

        self._lines_lock.release()

    def __init__(self, conn, newline_handler=None, read_size=128, wait_time=0.001):
        if newline_handler is None:
            newline_handler = self.__newline_handler

        super(LineCommunicator, self).__init__(conn, newline_handler, read_size, wait_time)

        self._lines = []
        self._async_lines = []
        self._lines_lock = threading.Lock()

    def is_async(self, line):
        """
        Checks whether or not given line is an asynchronous log. Uses ASYNC_LOGS variable

        Args:
            line (str): line to be checked

        Returns:
            True is line is an asynchronous log, False otherwise.

        """
        for r in self.ASYNC_LOGS:
            if r.search(line):
                return True

        return False

    def readlines(self, async_log=False):
        """
        Returns all entries from line buffer or from asynchronous line buffer

        Args:
            async_log (bool): if True, uses asynchronous buffer

        Returns:
            List with lines or empty list if buffer is empty
        """
        if async_log:
            buffer = self._async_lines
        else:
            buffer = self._lines

        self._lines_lock.acquire()

        lines = [line for line in buffer]
        buffer.clear()

        self._lines_lock.release()

        return lines

    def readline(self, async_log=False):
        """
        Returns first entry from line buffer or from asynchronous buffer

        Args:
            async_log (bool): if True, uses asynchronous buffer

        Returns:
            Str with line or None if buffer is empty
        """
        if async_log:
            buffer = self._async_lines
        else:
            buffer = self._lines

        line = None

        self._lines_lock.acquire()

        if len(buffer):
            line = buffer.pop(0)

        self._lines_lock.release()

        return line

    def __read(self, size):
        result = ""

        self._lines_lock.acquire()

        while self._lines and len(result) < size:
            line = self._lines.pop(0)

            left = (size - len(result))

            if len(line) > left:
                self._lines.insert(0, line[left:])

            result += line[:left]

        self._lines_lock.release()

        return result

    def read(self, size=-1):
        if size == -1:
            return "".join(self.readlines())

        return self.__read(size)

    def write(self, data):
        return super(LineCommunicator, self).write("{}\r\n".format(data))

    def stop(self):
        super().stop()
        while True:
            lines = self.readlines()
            async_lines = self.readlines(async_log=True)
            if not lines and not async_lines:
                break
            if lines:
                self.logger.debug(f"Data left in the lines buffer: '{lines}'")
            if async_lines:
                self.logger.debug(f"Data left in the asynchronous lines buffer: '{async_lines}'")


class PingError(Exception):
    pass


class BorderRouterCommunicator(LineCommunicator):

    PING_CMDS = {
        4: "ping",
        6: "ping6"
    }

    PING_RE = re.compile(r"(\d+)\sbytes\sfrom\s(.*):\sicmp_[r|s]eq=(\d+)\sttl=(\d+)\stime=(\d+\.?\d*)\sms")

    def __init__(self, conn, read_size=1280, wait_time=0.001):
        super(BorderRouterCommunicator, self).__init__(conn, None, read_size, wait_time)

        self._lines = []
        self._lines_lock = threading.Lock()

    def _wait_while_check_function_returns_false(self, check_function, timeout=1.0):
        end_time = time.time() + timeout

        checked_lines = []

        while time.time() < end_time:
            lines = self.readlines()

            checked_lines.extend(lines)

            matches = [check_function(line) is not None for line in lines]

            if any(matches):
                return sum(matches)

            time.sleep(0.1)

        else:
            for line in checked_lines:
                print(line)

            raise TimeoutError("Check function has not returned True in the expected period of time.")

    def ping(self, address, count=1, timeout=1.0):
        ip = ipaddress.ip_address(address)

        end_time = time.time() + (count * timeout)

        self.write("{} -c {} {}".format(self.PING_CMDS[ip.version], count, address))

        time.sleep(end_time - time.time())

        try:
            return self._wait_while_check_function_returns_false(self.PING_RE.match, timeout=0.1)

        except TimeoutError:
            raise PingError("Could not ping: {}".format(address))


class RfSwitchCommunicator(LineCommunicator):

    BOOL_MAP = {"1\n": True, "0\n": False}

    def __init__(self, conn, read_size=2):
        super(RfSwitchCommunicator, self).__init__(conn, None, read_size)
        self.lock_panel()
        self.display_string("RF SWITCH")

    def _wait_for_response(self, timeout=1.0):
        end_time = time.time() + timeout

        while time.time() < end_time:
            line = self.readline()

            if line != None:
                return line

            time.sleep(0.1)
        else:
            raise TimeoutError("Response has not been received in the expected period of time.")

    def lock_panel(self):
        self.write("SYSTEM:RWLOCK")

    def unlock_panel(self):
        self.write("SYSTEM:LOCAL")

    def display_off(self):
        self.write("DIAGNOSTIC:DISPLAY:STATE OFF")

    def display_on(self):
        self.write("DIAGNOSTIC:DISPLAY:STATE ON")

    def display_string(self, string):
        self.write("DIAGNOSTIC:DISPLAY \"{}\"".format(string))

    def close_channel(self, channel):
        self.write("CLOSE (@{})".format(channel))

    def open_channel(self, channel):
        self.write("OPEN (@{})".format(channel))

    def is_channel_open(self, channel):
        self.readlines()
        self.write("OPEN? (@{})".format(channel))
        response = self._wait_for_response()
        return self.BOOL_MAP[response]

    def is_channel_closed(self, channel):
        self.readlines()
        self.write("CLOSE? (@{})".format(channel))
        response = self._wait_for_response()
        return self.BOOL_MAP[response]


class OpenThreadBorderRouterCommunicator(BorderRouterCommunicator):

    LOGIN_RE = re.compile(r"\w+\slogin:")
    PASSWD_RE = re.compile(r"Password:")

    PROMPT_RE = re.compile(r"\w+@\w+:~\$\s?\w*")

    WELCOME_BANNER_RE = re.compile(r"^Raspbian\s+GNU/Linux\s+\d+\s+[\w\d]*\s+ttyS\d+")

    def __init__(self, conn, read_size=1280, wait_time=0.001):
        super(OpenThreadBorderRouterCommunicator, self).__init__(conn, read_size, wait_time)

    def wait_for_boot(self, timeout=120):
        timeout_time = time.time() + timeout

        while time.time() < timeout_time:
            matches = [self.WELCOME_BANNER_RE.match(line) is not None for line in self.readlines()]

            if any(matches):
                break

            time.sleep(0.1)
        else:
            raise TimeoutError("Could not find welcome banner.")

    def _wait_for_string_in_line_buffer(self, match_func, timeout=30):
        timeout_time = time.time() + timeout

        while time.time() < timeout_time:
            if match_func(self._line):
                break

            time.sleep(0.1)

        else:
            raise TimeoutError("Could not find matching string in the line buffer.")

    def _login(self, username, password, timeout=30):
        self._wait_for_string_in_line_buffer(self.LOGIN_RE.match, timeout)

        self._conn.write("{}\n".format(username))

        self._wait_for_string_in_line_buffer(self.PASSWD_RE.match, timeout)

        self._conn.write("{}\n".format(password))

    def login(self, username, password, timeout=30):
        timeout_time = time.time() + timeout

        while time.time() < timeout_time:
            try:
                self._login(username, password, timeout=0.5)

            except TimeoutError:
                if any([self.PROMPT_RE.match(line) is not None for line in self.readlines()]):
                    break

                self._conn.write("\n")

        else:
            raise TimeoutError("Could not to login to the Border Router.")

    def run_command(self, command, wait_for_exit_code=True, stdout=None, timeout=30):
        stdout = [] if stdout is None else stdout

        stdout.extend([line.strip("\r\n") for line in self.readlines()])

        if not wait_for_exit_code:
            self._conn.write("{}\n".format(command))
            return 0

        self._conn.write("{}; echo \"Exit code: $?\"\n".format(command))

        exit_code_re = re.compile(r"^Exit\scode:\s+(\d+)\s+")

        timeout_time = time.time() + timeout

        while time.time() < timeout_time:
            matches = []

            for line in self.readlines():
                stdout.append(line.strip("\r\n"))
                matches.append(exit_code_re.match(line))

            matches = [match for match in matches if match is not None]

            if any(matches):
                return matches[0].group(1)

            time.sleep(0.5)

        else:
            raise TimeoutError("Command has not been finished in the expected time period.")


class AdvancedLineCommunicator(LineCommunicator):
    """ Advanced CLI line communicator.

        This class allows to create an interface for sending commands and receiving
        responses from colorful CLI with error and success messages.
    """
    CLI_NEWLINE_ESC_CHAR = "\x1bE"
    CLI_COLOR_RE = r"(.*)\x1b\[[^m]{1,7}m(.*)"
    RETRY_ATTEMPTS = 1
    VT100_CURSOR_RE = r"(.*)\x1b\[\d+D\x1b\[J(.*)"
    LOG_RE = r"^.*<(info|debug|warning|error|none)> (.+?): (.+)"

    def __init__(self, conn, read_size=128, wait_time=0.001, prompt=None, success_prefix="done", error_prefix="error:", retry_on=None):
        """ Create Advanced CLI line communicator.

            Args:
                conn (connection object): connection object that will be used to send commands
                read_size (int): the size of a buffer for a single read attempt
                wait_time (float): delay, in seconds, between input stream availability checks
                prompt (str): CLI prompt string
                success_prefix (str): case insensitive prefix, that is returned on successful command execution
                error_prefix (str): case insensitive prefix, that is returned on command error, followed by error description
                retry_on (str, list(str)): if a command prints a line matching any string in retry_on, it will be repeated
        """
        super(AdvancedLineCommunicator, self).__init__(conn, self.__newline_handler, read_size, wait_time)

        self._prompt_re = re.compile(r"^{}\s+(.*)".format(prompt if prompt is not None else ".*~\$"))
        self._color_re = re.compile(self.CLI_COLOR_RE)
        self._vt100_cursor_re = re.compile(self.VT100_CURSOR_RE)
        self._log_re = re.compile(self.LOG_RE)
        self._success_prefix = success_prefix.lower()
        self._error_prefix = error_prefix.lower()
        self._last_command = ""

        self._retry_on = []

        if retry_on:
            if not isinstance(retry_on, list):
                retry_on = [retry_on]
            self._retry_on = retry_on
        self._received_logs = []

        self.clear()

    def __newline_handler(self, line):
        """ Looks for empty lines or VT100 newline escape sequence in a single line,
            breaks it into list of strings representing received lines and puts into
            internal line buffer or asynchronous line buffer (depending on is_async check)

            Args:
                line (str): line received over connection
        """
        if line == "\r\n":
            return

        new_lines = line.split(self.CLI_NEWLINE_ESC_CHAR)
        self._lines_lock.acquire()
        for new_line in new_lines:
            if self.is_async(new_line):
                self._async_lines.append(new_line)
            else:
                self._lines.append(new_line)
        self._lines_lock.release()

    def _remove_eol_characters(self, line):
        """ Removes every "\r" and "\n" character from input string.

            Args:
                line (str): input line

            Returns:
                str: line without "\r" and "\n" characters
        """
        return "".join([c if c != "\r" and c != "\n" else "" for c in line])

    def _remove_colors(self, line):
        """ Removes every VT100 color escape sequence from input string.

            Args:
                line (str): input line

            Returns:
                str: line without VT100 color escape sequences
        """
        colors_found = self._color_re.match(line)
        while colors_found:
            line = "".join(colors_found.groups())
            colors_found = self._color_re.match(line)

        return line

    def _remove_prompt(self, line):
        """ Removes every string prefix, equal to the prompt CLI prompt.

            Args:
                line (str): input line

            Returns:
                str: line without CLI prompt
        """
        found_prompt = self._prompt_re.match(line)

        if found_prompt:
            return found_prompt.group(1)

        return line

    def _gather_logs(self, line):
        """ Checks if the line is a log and retrieves it.

            Args:
                line (str): input line

            Returns:
                str: input line if not a log, empty string otherwise
        """
        # Remove the screen clearing
        found = self._vt100_cursor_re.match(line)
        if found:
            line = found.group(2)

        # Find the log themselves
        found = self._log_re.match(line)
        if found:
            self._received_logs.append({"level"  : found.group(1),
                                        "module" : found.group(2),
                                        "string" : found.group(3)})
            return ""

        return line

    def _remove_non_printable_characters(self, line):
        """ Removes all ASCII non-printable characters in a line.

            Args:
                line (str): input line

            Returns:
                str: input line without all non-printable characters
        """
        return ''.join([x if x in string.printable else '' for x in line])

    def _wait_until_true(self, check_function, timeout):
        """ Wait until check_function returns True or timeout occurs.

            Args:
                check_function (function): function to be called
                timeout (float): maximum time, in seconds, within which check_function will be checked against returned value

            Returns:
                bool: True of called function returns False, False if timeout occurred.
        """
        timeout_time = time.time() + timeout
        while time.time() < timeout_time:
            lines = self.readlines()
            if any([check_function(line) for line in lines]):
                return True

            time.sleep(0.01)

        return False

    def _check_if_command_finished(self, line):
        """ Receives a single line, filters it and checks if success message or failure
            prefix was received.

            Returns:
                bool: True if success message was received.

            Raises:
                CommandError: if parsed line contains error message
        """
        line = self._remove_colors(line)                     # Remove color escape characters
        line = self._remove_eol_characters(line)             # Remove Additional \r and \n characters
        line = self._remove_prompt(line)                     # Prompt prefix
        line = self._gather_logs(line)                       # Retrieve the logs
        line = self._remove_non_printable_characters(line)   # Remove the non-printable characters
        self.logger.debug("CLI::{} RX: {}".format(self._conn, line))

        if line.lower().startswith(self._success_prefix):
            return True

        elif line == self._last_command:
            return False

        elif line == "":
            return False

        elif any(r in line for r in self._retry_on):
            self.logger.error("Error data detected: {}".format(line))
            raise CommunicatorError()

        elif line.lower().startswith(self._error_prefix):
            raise CommandError(line[len(self._error_prefix):].strip())

        else:
            self.return_value.append(line)
            return False

    def write_command(self, command, wait_for_success=True, timeout=1.0):
        """ Writes a command through CLI connection and wait either for success
            message, error prefix or timeout event.

            Args:
                command (str): command to be called on CLI
                wait_for_success (bool): if False, suppresses timeout event
                timeout (float): maximum time, in seconds, within witch CLI should return command status

            Returns:
                list: containing received lines or None if no command output received.

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
        """
        self._last_command = command
        attempts = self.RETRY_ATTEMPTS + 1
        while attempts:
            try:
                self.write(command)
                self.logger.debug("CLI::{} TX: {}".format(self._conn, command))

                self.return_value = []
                # TODO: KRKNWK-3707 add support for asynchronous logs in write_command
                self.received_done = self._wait_until_true(self._check_if_command_finished, timeout)
                if wait_for_success and not self.received_done:
                    raise TimeoutError("{}: '{}' did not receive '{}'. So far got: {}".format(self, command, self._success_prefix, self.return_value))
                return self.return_value if self.return_value else None
            except CommunicatorError:
                attempts -= 1
                self.logger.error("{}: retrying to run cmd: '{}'".format(self, command))

    def retrieved_logs(self, aquisition_time=0):
        """ Returns the collected logs. 
        
            Args:
                aquisition_time:    time to collect logs
        """
        self.clear()
        time.sleep(aquisition_time)
        self.clear()
        return self._received_logs

    def empty_logs(self):
        self._received_logs = []

    def clear(self):
        """ Writes a new line character and reads all input lines in order to get
            clean input for further CLI commands.
        """
        logging.info("CLI: {} flushing IO".format(self._conn))
        self.write("")
        self.return_value = []
        self._wait_until_true(self._check_if_command_finished, timeout=1.0)
