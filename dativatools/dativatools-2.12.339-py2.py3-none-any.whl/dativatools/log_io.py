import logging
import logging.config
import logging.handlers
import os
import time
from datetime import datetime

class Logger(object):
    shared_state = {}
    def __init__(self, log_path, log_filename, task_name, source_date, consumption_type, logger_name="logger", log_level=logging.INFO):
        self.consumption_type = consumption_type
        self.source_date = source_date
        self.file_handler = None
        self.root_logger = None
        self.formatter = None
        if not Logger.shared_state:
            self.logfile(log_path, log_filename)
            Logger.shared_state['log'] = True
        self.task_name = task_name
        self.api_name = None
        self.logger = logging.getLogger('inrlogger.{}'.format(logger_name))
        self.logger.setLevel(log_level)


    def set_format(self):
        ''' sets log message to a predefined format'''
        message_format = "{} [{}]".format(self.source_date, str(int(time.time()))) + " %(levelname)s" " %(message)s "
        self.formatter = logging.Formatter(fmt=message_format)

    def get_file_size(self, file_path):
        '''Returns size of all files in given directory. Does not include size of subdirectories
        
        Args:
            file_path: location at which you want size of all files

        Returns
            str: size of all files in directort with "B" appended to it '''

        if os.path.isfile(file_path):
            return str(os.path.getsize(file_path)) + "B"
        elif os.path.isdir(file_path):
            #non recursive-does not return size of subfolders
            return str(sum(os.path.getsize(f) for f in os.listdir(file_path) if os.path.isfile(f))) + "B"
        else:
            return ''

    def format_message(self, message,status,levelname, file_size='', files_used=''):
        ''' Sets message format as required in logz_io. This method is called internally

        Args:
            message: Message field in logs
            status: State of processing. Currently we used running, failure, completed
            levelname: logging level
            file_size: size of source/export file
            files_used: name of source/export file

        Returns
            str: message to be printed in logs'''
        files_used = os.path.basename(files_used)

        message_format = "[{}] {}".format(str(int(time.time())), levelname)
        return "{} {} {}.{} {} {} {} {} {}".format(message_format, self.consumption_type, self.task_name, self.api_name, status,files_used, self.format_date(self.source_date), file_size, message)

    def info_s3(self, files_used, message, file_size, status="running", *args, **kwargs):
        '''This meassage is to be called when you want to log info level message from s3 library
            It internally calls info method of logging module.

        Args:
            files_used: source/export file being used
            message: message to be printed in log
            file_size: size of source/export file
            status: status of precessing. Default calue is "running" '''

        msg = self.format_message(message,status, "INFO", file_size=file_size, files_used=files_used)
        self.logger.info(msg)
    
    def format_date(self, date):
        '''This method formats date in "%Y-%m-%dT%H:%M" format
        
        Args:
            date: This must be either in "%Y%m%d" or "%Y%m%d%H" format eg 20171001 ir 2017100100

        Returns:
            date in "%Y-%m-%dT%H:%M" format eg 2018-01-15T00:00'''

        if len(date) == 8:
            return datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%dT%H:%M")
        if len(date) == 10:
            return datetime.strptime(date, "%Y%m%d%H").strftime("%Y-%m-%dT%H:%M")

    def info(self, files_used, message, status="running", *args, **kwargs):
        '''This message is to be called when you want to log info level message 
            It internally calls info method of logging module.

        Args:
            files_used: source/export file being used
            message: message to be printed in log
            status: status of precessing. Default calue is "running" '''
        if type(files_used) != list: 
            files_used = [files_used]
        for each_file in files_used:
            if status == "completed":
                file_size = self.get_file_size(each_file)
            else:
                file_size = ""
            if file_size:   
                msg = self.format_message(message,status, "INFO", file_size=file_size, files_used=each_file)
            else:
                msg = self.format_message(message, status, "INFO", files_used=each_file)
            self.logger.info(msg)

    def exception(self, message, files_used = '',status="failed", *args, **kwargs):
        '''This message is to be called when you want to log exception level message 
            It internally calls error method of logging module.

        Args:
            files_used: source/export file being used. Default value is ''.
            message: message to be printed in log
            status: status of precessing. Default calue is "failed" '''

        if  files_used:
            file_size = self.get_file_size(files_used)
        elif not files_used:
            file_size = ''
        msg = self.format_message(message,status,"ERROR", file_size=file_size, files_used=files_used)
        self.logger.error(msg,exc_info=False)

    def error(self, message,status="failed", files_used = None, *args, **kwargs):
        '''This message is to be called when you want to log error level message 
            It internally calls error method of logging module.

        Args:
            files_used: source/export file being used. Default value is None.
            message: message to be printed in log
            status: status of precessing. Default calue is "failed" '''

        if files_used:
            msg = self.format_message(message, status, "ERROR", files_used=files_used)
        else:
            msg = self.format_message(message, status, "ERROR")
        self.logger.error(msg)

    def set_api_name(self, api_name):
        ''' This method can be called when you want change the api name in logs'''

        self.api_name = api_name

    def set_task_name(self,task_name):
        '''This method can be called to change the taks name in the logs'''

        self.task_name = task_name

    def logfile(self, path, log_filename, when='midnight', interval=1, backupCount=0,
                encoding=None, delay=False, utc=False):
        '''This method creates a log file and adds a watchedfile and  timerotating handlers to log file

        Args
            path- Directory path at which the log should be created.
            log_filename - name of log file'''

        if self.root_logger is None:
            self.root_logger = logging.getLogger('inrlogger')
            self.root_logger.setLevel(logging.INFO)
        log_file = os.path.join(path, log_filename)
        
        if not os.path.isfile(log_file):
            open(log_file, 'w').close()
        if when is None:
            fh = logging.handlers.WatchedFileHandler(log_file, delay=delay)
        else:
            fh = logging.handlers.TimedRotatingFileHandler(log_file, when, interval, backupCount, encoding, delay, utc)
        fh.setLevel(logging.INFO)
        fh.setFormatter(self.formatter)
        if not self.root_logger.handlers:
            logging.getLogger('').addHandler(fh)
        logging.getLogger('botocore').setLevel(logging.CRITICAL)
        logging.getLogger('boto3').setLevel(logging.CRITICAL)
        if self.file_handler is not None:
            self.root_logger.removeHandler(self.file_handler)
        self.file_handler = fh

