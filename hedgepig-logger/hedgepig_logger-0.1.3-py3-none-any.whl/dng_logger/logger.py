import sys
import time
import codecs
from datetime import datetime
from collections import OrderedDict

class log:
    logfile_path=None
    logfile=sys.stdout
    stdout_also=False
    stopped=False
    tracker=None
    timer=None
    autoflush=True

    @staticmethod
    def start(logfile=None, message=None, args=None, stdout_also=True):
        if logfile and type(logfile) == type('a'):
            log.logfile_path=logfile
            log.logfile=open(logfile, 'w')
        if message and type(message) == type(lambda x: x):
            if args: message(args)
            else: message()
        elif message and type(message) == type('str'):
            log.writeln(message)
        log.stdout_also=stdout_also
    @staticmethod
    def stop(message=None, suppress=False):
        if message:
            log.writeln(message)
        if log.logfile != sys.stdout: 
            if (not suppress) and log.logfile_path:
                log.writeln('\nLog output saved to %s' % log.logfile_path)
            log.logfile.close()
        log.stopped = True
    @staticmethod
    def getstream():
        return log.logfile
    @staticmethod
    def write(message, stdoutOnly=False):
        if log.stdout_also and (log.getstream() != sys.stdout):
            sys.stdout.write(message)
        if stdoutOnly and log.getstream() != sys.stdout:
            return
        if not log.stopped:
            log.getstream().write(message)
            if log.autoflush: log.getstream().flush()
        else:
            raise Exception("Log has stopped!")
    @staticmethod
    def writeln(message='', stdoutOnly=False):
        log.write(message, stdoutOnly=stdoutOnly); log.write('\n', stdoutOnly=stdoutOnly)
    @staticmethod
    def progress(current, total, numDots=0, stdoutOnly=False):
        line = str.format('\r{0}{1}%', numDots*'.', int((float(current)/total)*100))
        log.write(line, stdoutOnly=stdoutOnly)
    @staticmethod
    def yesno(bln):
        if bln: return 'Yes'
        else: return 'No'

    @staticmethod
    def redirect_stderr():
        '''Redirect output from STDERR to the log
        '''
        sys.stderr = log.getstream()

    @staticmethod
    def track(message='{0:,}', total=None, writeInterval=1, stdoutOnly=False):
        # if message was given as a string, convert it to a lambda function
        if type(message) == type('str'):
            msgFormat = message 
            # default to percentage with a total
            if total: message = lambda current, total, args: str.format(msgFormat, int((float(current)/total)*100), *args)
            # default to printing current with no total
            else: message = lambda current, args: str.format(msgFormat, current, *args)

        # set up the onIncrement lambda for current/total or current only
        if total:
            onIncrement = lambda current, total, args: log.write(
                str.format('\r{0}', message(current, total, args)), stdoutOnly=True
            )
            onFlush = lambda current, total, args: log.write(
                str.format('\r{0}', message(current, total, args)), stdoutOnly=stdoutOnly
            )
        else:
            onIncrement = lambda current, args: log.write(
                str.format('\r{0}', message(current, args)), stdoutOnly=True
            )
            onFlush = lambda current, args: log.write(
                str.format('\r{0}', message(current, args)), stdoutOnly=stdoutOnly
            )

        log.tracker = ProgressTracker(total, onIncrement=onIncrement, onFlush=onFlush, writeInterval=writeInterval)

    @staticmethod
    def tick(*args):
        if log.tracker != None:
            if not log.tracker.total or log.tracker.current < log.tracker.total:
                log.tracker.increment(*args)
            else:
                raise Exception('Tracker is complete!')

    @staticmethod
    def flushTracker(*args, **kwargs):
        message = kwargs.get('message', '')
        newline = kwargs.get('newline', True)
        if log.tracker != None:
            log.tracker.flush(*args)
            if newline: log.writeln('\n%s' % message)
            else: log.writeln(message)

    @staticmethod
    def reset():
        if log.tracker != None:
            log.tracker.reset()

    @staticmethod
    def startTimer(message=None, newline=True):
        if message:
            if newline: log.writeln(message)
            else: log.write(message)
        log.timer = Timer()
        log.timer.start()
        return log.timer

    @staticmethod
    def stopTimer(timer=None, message='>>Completed in {0} sec.\n'):
        if timer or log.timer:
            if not timer: timer = log.timer
            timer.stop()
            elpsed = timer.elapsed()
            log.writeln(str.format(message, elpsed))
        else:
            raise Exception('No timer to stop!')

    @staticmethod
    def writeConfig(settings, title=None, start_time=None, end_time=None):
        '''Write an experimental configuration to the log.

        Always writes the current date and time at the head of the file.

        The optional title argument is a string to write at the head of the file,
            before date and time.

        Settings should be passed in as a list, in the desired order for writing.
        To write the value of a single setting, pass it as (name, value) pair.
        To group several settings under a section, pass a (name, dict) pair, where
            the first element is the name of the section, and the second is a
            dict (or OrderedDict) of { setting: value } format.

        For example, the following call:
            log.writeConfig([
                ('Value 1', 3),
                ('Some other setting', True),
                ('Section 1', OrderedDict([
                    ('sub-value A', 12.4),
                    ('sub-value B', 'string')
                ]))
            ], title='My experimental configuration')
        will produce the following configuration log:
            
            My experimental configuration
            Run time: 1970-01-01 00:00:00

            Value 1: 3
            Some other setting: True

            ## Section 1 ##
            sub-value A: 12.4
            sub-value B: string


        Arguments:

            settings   :: (described above)
            title      :: optional string to write at start of config file
            start_time :: a datetime.datetime object indicating when the program started
                          execution; if not provided, defaults to datetime.now()
            end_time   :: a datetime.datetime object indicating when the program ended
                          execution; if provided, also writes elapsed execution time
                          between start_time and end_time
        '''

        group_set = set([dict, OrderedDict, list, tuple])
        dict_set = set([dict, OrderedDict])

        # headers
        if title:
            log.write('%s\n' % title)

        time_fmt = '%Y-%m-%d %H:%M:%S'

        if start_time is None:
            start_time = datetime.now()
            header = 'Run'
        else:
            header = 'Start'
        log.write('%s time: %s\n' % (header, start_time.strftime(time_fmt)))

        if end_time:
            log.write('End time: %s\n' % end_time.strftime(time_fmt))
            log.write('Execution time: %f seconds\n' % (end_time - start_time).total_seconds())
        log.write('\n')

        for (key, value) in settings:
            if type(value) in group_set:
                log.write('\n## %s ##\n' % key)
                if type(value) in dict_set:
                    iterator = value.items()
                else:
                    iterator = iter(value)
                for (sub_key, sub_value) in iterator:
                    log.write('%s: %s\n' % (sub_key, str(sub_value)))
                log.write('\n')
            else:
                log.write('%s: %s\n' % (key, str(value)))

        log.write('\n')

class ProgressTracker:
    def __init__(self, total=None, onIncrement=None, onFlush=None, writeInterval=1):
        self.total = total
        self.current = 0
        self.sinceLastWrite = 0
        self.onIncrement = onIncrement
        self.onFlush = onFlush
        self.writeInterval = writeInterval

    def increment(self, *args):
        self.current += 1
        self.sinceLastWrite += 1
        if self.sinceLastWrite >= self.writeInterval:
            self.sinceLastWrite = 0
            self.showProgress(*args)

    def reset(self):
        self.current = 0
        self.sinceLastWrite = 0

    def showProgress(self, *args):
        if self.onIncrement:
            # only call 3-arg onIncrement if we have a total we're counting towards
            if self.total: self.onIncrement(self.current, self.total, args)
            else: self.onIncrement(self.current, args)

    def flush(self, *args):
        if self.onFlush:
            # only call 3-arg onIncrement if we have a total we're counting towards
            if self.total: self.onFlush(self.current, self.total, args)
            else: self.onFlush(self.current, args)

class Timer:
    def __init__(self):
        self.startTime = 0
        self.stopTime = 0
        self.started = False

    def start(self):
        if not self.started:
            self.startTime = time.time()
            self.started = True
        else:
            raise Exception('Timer already started!')

    def stop(self):
        if self.started:
            self.stopTime = time.time()
            self.started = False
        else:
            raise Exception('Timer already stopped!')

    def elapsed(self):
        if not self.started:
            return self.stopTime - self.startTime
        else:
            return time.time() - self.startTime
