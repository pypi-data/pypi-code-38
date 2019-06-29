##
#  tagsnag.py
#  tagsnag
#
#  Created by Thomas Johannesmeyer (thomas@geeky.gent) on 01.11.2018.
#  Copyright (c) 2018 www.geeky.gent. All rights reserved.
#

import logging

from tagsnag.git import Git
from tagsnag.gui import GUI

# Needed for CPU Count detection
import re

class Tagsnag():
    """Tagsnag main class"""

    def __init__(self, cwd, should_use_gui = False):
        super(Tagsnag, self).__init__()

        self.cwd = cwd
        self.should_use_gui = should_use_gui

        self.initial_setup()


    def initial_setup(self):
        ##
        # Flags
        self.should_prune = False
        self.should_autostash = False
        self.verbose = False
        self.should_create_logfile = False
        self.should_update = False
        self.cpu_count = self.available_cpu_count()

        # Advanced setup
        self.setup_logger()

        # Initiate GUI
        if self.should_use_gui:
            self.start_gui()



    def run_from_cli(self, should_update, xml_path, tag, directory, destination, filename, extension):
        "This method handles run from CLI"

        self.git = Git(path=self.cwd, cpu_count=self.cpu_count)

        if should_update:
            self.git.update_all_repos()

            if xml_path:
                self.git.start_with_xml(xml_path)

            elif tag and filename and extension:
                self.git.extract_file_from_all_repos(tag=tag,
                                                    filename=filename,
                                                    extension=extension,
                                                    destination=destination)

            elif tag and directory :
                self.git.extract_directory_from_all_repos(tag=tag,
                                                         directory=directory,
                                                         destination=destination)

            elif not should_update:
                # Funky argument combination. Display help:
                self.display_help()


    def display_help(self):
            print("{}".format('Insufficient arguments. For a full description run: tagsnag --help'))


    def start_gui(self):
            self.gui = GUI(path=self.cwd, cpu_count=self.cpu_count)


    def enable_logfile(self):

        if self.log:
            # Create filehandler
            fh = logging.FileHandler('Tagsnag.log')
            fh.setLevel(logging.DEBUG)
            self.log.addHandler(fh)


    def setup_logger(self):
        """ Creating / configuring logger instance """

        logging.basicConfig(level=logging.WARNING, format='%(msg)s')
        self.log = logging.getLogger('logger')


        ##
        # Setting up argument parser
        self.log.debug('Setting up argument parser...')


    def available_cpu_count(self):
        """ Number of available virtual or physical CPUs on this system, i.e.
        user/real as output by time(1) when called with an optimally scaling
        userspace-only program"""

        # cpuset
        # cpuset may restrict the number of *available* processors

        try:
            m = re.search(r'(?m)^Cpus_allowed:\s*(.*)$',
                        open('/proc/self/status').read())
            if m:
                res = bin(int(m.group(1).replace(',', ''), 16)).count('1')
                if res > 0:
                    return res
        except IOError:
            pass

        # Python 2.6+
        try:
            import multiprocessing
            return multiprocessing.cpu_count()
        except (ImportError, NotImplementedError):
            pass

        # https://github.com/giampaolo/psutil
        try:
            import psutil
            return psutil.cpu_count()   # psutil.NUM_CPUS on old versions
        except (ImportError, AttributeError):
            pass

        # POSIX
        try:
            res = int(os.sysconf('SC_NPROCESSORS_ONLN'))

            if res > 0:
                return res
        except (AttributeError, ValueError):
            pass

        # Windows
        try:
            res = int(os.environ['NUMBER_OF_PROCESSORS'])

            if res > 0:
                return res
        except (KeyError, ValueError):
            pass

        # jython
        try:
            from java.lang import Runtime
            runtime = Runtime.getRuntime()
            res = runtime.availableProcessors()
            if res > 0:
                return res
        except ImportError:
            pass

        # BSD
        try:
            sysctl = subprocess.Popen(['sysctl', '-n', 'hw.ncpu'],
                                    stdout=subprocess.PIPE)
            scStdout = sysctl.communicate()[0]
            res = int(scStdout)

            if res > 0:
                return res
        except (OSError, ValueError):
            pass

        # Linux
        try:
            res = open('/proc/cpuinfo').read().count('processor\t:')

            if res > 0:
                return res
        except IOError:
            pass

        # Solaris
        try:
            pseudoDevices = os.listdir('/devices/pseudo/')
            res = 0
            for pd in pseudoDevices:
                if re.match(r'^cpuid@[0-9]+$', pd):
                    res += 1

            if res > 0:
                return res
        except OSError:
            pass

        # Other UNIXes (heuristic)
        try:
            try:
                dmesg = open('/var/run/dmesg.boot').read()
            except IOError:
                dmesgProcess = subprocess.Popen(['dmesg'], stdout=subprocess.PIPE)
                dmesg = dmesgProcess.communicate()[0]

            res = 0
            while '\ncpu' + str(res) + ':' in dmesg:
                res += 1

            if res > 0:
                return res
        except OSError:
            pass

        raise Exception('Can not determine number of CPUs on this system')


    ##
    # Setter and getter

    def set_verbose(self, flag):
        """ Verbose Flag Setter """
        self.verbose = flag

        if flag:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)


    def set_should_prune(self, flag):
        """ Should Prune Setter """

        self.should_prune = flag


    def set_should_autostash(self, flag):
        """ Autostash Setter """

        self.should_autostash = flag


    def set_create_logfile(self, flag):
        """ Create Logfile Setter """

        self.should_create_logfile = flag

        if flag:
            self.enable_logfile()

