
import unittest
import logging
from base.multiprocessing_logger import MultiprocessingLogger
import time
import traceback

#relative path from root directory(base dir) of project
LOG_FILE_NAME="log\\finapi_logs.log"

test_data=[
{"log_level":"DEBUG","log_msg":"Test DEBUG 1"},
{"log_level":"INFO","log_msg":"Test INFO 1"},
{"log_level":"ERROR","log_msg":"Test ERROR 1"},
{"log_level":"CRITICAL","log_msg":"Test CRITICAL 1"}
]

class Unit_test_of_multiprocessing_logger(unittest.TestCase):

    def __init__(self,testName,log_file_name,log_level,log_msg):
        super(Unit_test_of_multiprocessing_logger,self).__init__(testName)
        self.logger=None
        self.log_file_name=log_file_name
        self.log_level=log_level
        self.log_msg=log_msg

    def setUp(self):
        self.logger=MultiprocessingLogger()

    def get_last_line_of_log_file(self):
        """
            Returns last line on log File.

            Returns :
                last_line : (type : str) last line on log_file.
        """
        try:
            last_line=""
            last_line.capitalize
            with open(self.log_file_name, 'r') as f:
                lines = f.read().splitlines()
                last_line = lines[-1]
                #print(last_line)
            return last_line
        except Exception as e:
            print(traceback.format_exc())
            return None

    def test_log_records(self):
        if self.log_level=="INFO":
            self.logger.logInfo("E-201","unittest",self.log_msg)
        elif self.log_level=="DEBUG":
            self.logger.logDebug("E-201","unittest",self.log_msg)
        elif self.log_level=="ERROR":
            self.logger.logError("E-201","unittest",self.log_msg)
        elif self.log_level=="CRITICAL":
            self.logger.logCritical("E-201","unittest",self.log_msg)
        time.sleep(3)
        last_line=self.get_last_line_of_log_file()

        log_msg_in_log_file=last_line.split(":")[-1].split("|")[-1].strip()
        log_level_in_log_file=last_line.split(":")[-2].strip().split(" ")[-1]
        #print(log_level_in_log_file,log_msg_in_log_file)

        self.assertEqual(self.log_level+self.log_msg,log_level_in_log_file+log_msg_in_log_file,"Testing log"+self.log_level.capitalize()+"() function.")



def suite():
    suite = unittest.TestSuite()
    for data in test_data:
        log_lvl=data["log_level"]
        log_msg=data["log_msg"]
        suite.addTest(Unit_test_of_multiprocessing_logger("test_log_records",LOG_FILE_NAME,log_lvl,log_msg))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())