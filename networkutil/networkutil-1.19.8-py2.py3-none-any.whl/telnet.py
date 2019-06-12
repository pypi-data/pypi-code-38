# encoding: utf-8

import time
import telnetlib
import logging_helper

logging = logging_helper.setup_logging()


class TelnetObj(object):

    def __init__(self,
                 ip,
                 timeout=5,
                 retry=3,
                 retry_timeout=10):

        self.tn = None
        self.ip = ip

        self.__timeout = timeout
        self.__retry = retry
        self.__retry_timeout = retry_timeout

        self.__connect()

    def __connect(self):
        logging.info(u"Connecting to " + self.ip + u"...")

        while self.tn is None and self.__retry > 0:
            try:
                self.tn = telnetlib.Telnet(self.ip, timeout=self.__timeout)
                self.tn.read_until("login: ")
                self.tn.write("root" + "\n")
                self.tn.read_until("# ")
                logging.info(u"Connected!")

            except Exception:
                self.tn = None
                logging.warning(u"Unable to connect to " + self.ip)
                logging.warning(u'Retrying connection in {t} sec...'.format(t=self.__retry_timeout))
                time.sleep(self.__retry_timeout)

            self.__retry -= 1

        if self.__retry == 0:
            raise Exception(u'Aborting telnet to {ip}: Timed out'.format(ip=self.ip))

    def send_command(self,
                     command):

        # run the command
        try:
            self.tn.write(command + "\n")

        except Exception:
            logging.error(u"Unable to send the command to device")
            return

        return self.tn.read_until("# ")

    def readline(self):
        return self.tn.read_until("\n")
