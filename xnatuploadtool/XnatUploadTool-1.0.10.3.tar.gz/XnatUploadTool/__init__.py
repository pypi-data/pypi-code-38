from __future__ import print_function

import base64
import datetime
import json
import logging
import os
import re
import sys
import uuid
import zipfile
from distutils.spawn import find_executable
from shutil import rmtree

import easyprocess
import magic
import pathos
import pydicom
import requests
from pyunpack import Archive
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class XnatUploadTool:
    def __init__(self, **kwargs):
        # Designed to be called from script using argparse, otherwise dict must be passed in as kwargs with
        # all following variables set
        try:
            self.args = kwargs
            self.starttime = None
            self.httpsess = None
            self.lastrenew = None
            self.logger = None
            self.prearcdate = False
            self.host = kwargs['host']
            self.localval = dict()
            self.upload_time = int()
            self.build_time = int()
            self.archive_time = int()

            # Pull u/p from env if not set in args
            if kwargs['username'] is None or kwargs['password'] is None:
                (self.username, self.password) = os.environ['XNATCREDS'].split(':', 2)
            else:
                self.username = kwargs['username']
                self.password = kwargs['password']

            self.timeout = kwargs['timeout']
            self.sessiontimeout = datetime.timedelta(minutes=kwargs['sessiontimeout'])

            self.target = kwargs['target']
            self.project = kwargs['project']
            self.session = kwargs['session']
            self.subject = kwargs['subject']
            self.scan = kwargs['scan']
            self.datatype = kwargs['datatype']
            self.xmlnamespace = kwargs['xmlnamespace']
            self.deletesessions = kwargs['deletesessions']
            self.subjectfields = None
            self.sessionfields = None
            self.scanfields = None

            if kwargs['bsubjectfields']:
                self.subjectfields = json.loads(base64.b64decode(kwargs['bsubjectfields']))
            elif kwargs['subjectfields']:
                self.subjectfields = json.loads(kwargs['subjectfields'])

            if kwargs['bsessionfields']:
                self.sessionfields = json.loads(base64.b64decode(kwargs['bsessionfields']))
            elif kwargs['sessionfields']:
                self.sessionfields = json.loads(kwargs['sessionfields'])

            if kwargs['bscanfields']:
                self.scanfields = json.loads(base64.b64decode(kwargs['bscanfields']))
            elif kwargs['scanfields']:
                self.scanfields = json.loads(kwargs['scanfields'])

            self.resource = kwargs['resource']

            if 'jobs' in kwargs and kwargs['jobs'] is not None:
                self.threads = kwargs['jobs']
            else:
                self.threads = 1
            self.logfile = kwargs['logfile']
            self.tmpdir = kwargs['tmpdir']
            self.validate = kwargs['validate']
            self.raw = kwargs['raw']
            self.verbose = kwargs['verbose']

            self.filetree = {self.target: {}}
            self.ingestconfig = None
            self.ingestpatterns = None
            self.ingestdata = dict()
            self.ingestion_required_fields = ['xmlnamespace', 'datatype', 'resource', 'subject', 'session', 'scan']

            self.newerthan = kwargs['newerthan']
            self.olderthan = kwargs['olderthan']

            # Ingest config is a separate file defining fields based on filepath/name
            self.ingestconfig = kwargs['ingestconfig']

            # Set up logging
            self.setup_logger()

            # Initialize Sessions
            self.renew_session()
        except KeyError as e:
            logging.error('Unable to initialize uploader, missing argument: %s' % str(e))
            exit(1)

    def setup_logger(self):
        # Set up logging
        if self.logfile is not None:
            if os.path.exists(os.path.realpath(self.logfile)):
                hdlr = logging.FileHandler(self.logfile)
            else:
                logging.error('Log path %s does not exists' % str(self.logfile))
                exit(1)
        else:
            hdlr = logging.StreamHandler(sys.stdout)

        self.logger = logging.getLogger(__name__)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        if self.verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        return True

    def setup_upload(self):
        # If not running configured for filesystem ingestion
        # Check for subject and session, attempt to create for non dicom
        # Ingestion will handle the whole filesystem processing differently
        if self.ingestconfig is None and self.datatype != 'dicom':
            self.logger.debug('Preparing for upload to %s from %s as %s: declared type %s' %
                              (self.host, self.target, self.username, self.datatype))
            self.logger.debug('Checking status for %s/%s/%s' % (self.project, self.subject, self.session))
            if self.check_project() is not True:
                self.logger.error("Project %s does not exist" % self.project)
                exit(1)
            if self.check_subject(create=True, fields=self.subjectfields, subject=self.subject) is not True:
                self.logger.error("Subject %s does not exist and cannot be created on project %s" %
                                  (self.subject, self.project))
                exit(1)

            if self.deletesessions and self.subject and self.session:
                self.delete_session(subject=self.subject, session=self.session)

            if self.check_session(create=True, fields=self.sessionfields, subject=self.subject,
                                  session=self.session, datatype=self.datatype,
                                  xmlnamespace=self.xmlnamespace) is not True:
                self.logger.error("Session %s does not exist and cannot be created for project %s/subject %s" %
                                  (self.session, self.project, self.subject))
                exit(1)

            if self.check_scan(create=True, fields=self.scanfields, subject=self.subject, session=self.session,
                               scan=self.scan, datatype=self.datatype, xmlnamespace=self.xmlnamespace) is not True:
                self.logger.error("Scan %s does not exist and cannot be created for project %s/subject %s/session %s" %
                                  (self.scan, self.project, self.subject, self.session))
                exit(1)
        else:
            self.logger.debug('Preparing for ingestion of %s to %s as %s' %
                              (self.target, self.host, self.username))
            self.logger.debug('Checking status for %s' % self.project)
            if self.check_project() is not True:
                self.logger.error("Project %s does not exist" % self.project)
                exit(1)
            if self.deletesessions and self.subject and self.session:
                self.delete_session(subject=self.subject, session=self.session)
        return True

    def start_upload(self):
        self.setup_upload()

        self.starttime = datetime.datetime.now()

        if self.ingestconfig is not None:
            self.logger.info("Starting upload of %s to %s project %s" % (self.target, self.host, self.project))
            (totalsuccess, totalfiles, totalsize) = self.start_ingestion()
            self.logger.info("Transferred %d/%d files (%s)" % (totalsuccess, totalfiles, self.bytes_format(totalsize)))
        else:
            self.logger.info("Starting upload of %s to %s/%s/%s/%s" % (self.target, self.host, self.project,
                                                                       self.subject, self.session))

            # Analyze dir structure to see if tar.gz is present
            self.logger.debug("Analyzing target %s" % self.target)
            # If scan, expect single dir with files in it for a scan
            if self.scan is True:
                self.analyze_dir(self.target + '/' + self.scan)
            else:
                self.analyze_dir(self.target)

            results = list()
            if os.path.isfile(self.target):
                # If a single file fire it off
                results.append(self.upload_singlefile(self.scan))
            elif self.scan or self.threads < 2:
                # If a single scan or a single thread don't use mp pool
                if self.scan:
                    # Expect a single dir with files in it for a scan
                    results.append(self.process_scan(self.target, self.filetree))
                else:
                    # Expect a subdir for each scan and parallelize
                    for scan in self.filetree[self.target]:
                        results.append(self.process_scan(scan, self.filetree))
            else:
                # Execute as multiprocessor job
                p = pathos.pools.ProcessPool(self.threads)
                scans = list()
                filetrees = list()
                for scan in self.filetree[self.target]:
                    scans.append(scan)
                    filetrees.append(self.filetree)

                # Launch pool and collect results
                results = p.map(self.process_scan, scans, filetrees)

            # Tally results
            for thisresult in results:
                if len(thisresult) > 1 and thisresult[2] is not None and re.match(r'[0-9]+_[0-9]+', str(thisresult[2])):
                    self.prearcdate = thisresult[2]
                    self.localval.update(thisresult[1])

            self.upload_time = (datetime.datetime.now() - self.starttime).total_seconds()
            self.logger.info('All uploads complete in %ds [Proj %s Sub %s Sess %s]' % (
                self.upload_time, self.project, self.subject, self.session))
            lastend = datetime.datetime.now()

            # Check that prearcdate is set and has proper format, then build and archive session
            if self.datatype == 'dicom':
                if self.prearcdate is not False and re.match(r'[0-9]+_[0-9]+', str(self.prearcdate)):
                    self.logger.info('Starting post processing')
                    prearcpathfinal = "/data/prearchive/projects/%s/%s/%s" % \
                                      (self.project, self.prearcdate, self.session)
                    proctime = datetime.datetime.now()
                    self.renew_session()
                    r = None
                    try:
                        r = self.httpsess.post(url=self.host + prearcpathfinal, params={'action': 'build'},
                                               timeout=(30, self.timeout))
                    except requests.exceptions.ReadTimeout:
                        self.logger.error("[%s] Failed to build due to read timeout, increase default from %d" % (
                            self.session, self.timeout))
                        exit(1)
                    except requests.exceptions.ConnectionError:
                        self.logger.error("[%s] failed to build due to connect timeout, increase default from %d" %
                                          (scan, self.timeout))
                    except Exception as e:
                        self.logger.error("[%s] failed to build due to unknown error: %s" %
                                          (scan, e))

                    if r is not None and r.status_code == 200:
                        self.build_time = (datetime.datetime.now() - lastend).total_seconds()
                        self.logger.info('Build Successful in %ds: %s' % (self.build_time, prearcpathfinal))
                        lastend = datetime.datetime.now()
                    else:
                        self.logger.error('Build Failed: %s, (%s)', prearcpathfinal, r.status_code)

                    self.renew_session()
                    r = None
                    try:
                        r = self.httpsess.post(url=(self.host + "/data/services/archive"), params={'src': prearcpathfinal},
                                               timeout=(30, self.timeout))
                    except requests.exceptions.ReadTimeout:
                        self.logger.error("[%s] Failed to archive due to read timeout, increase default from %d" % (
                            self.session, self.timeout))
                        exit(1)
                    except requests.exceptions.ConnectionError:
                        self.logger.error("[%s] Failed to archive due to read timeout, increase default from %d" %
                                          (scan, self.timeout))
                    except Exception as e:
                        self.logger.error("[%s] Failed to archive due to unknown error: %s" %
                                          (scan, e))

                    if r is not None and r.status_code == 200:
                        self.archive_time = (datetime.datetime.now() - lastend).total_seconds()
                        self.logger.info('Archive Successful in %ds: %s' % (self.archive_time, prearcpathfinal))
                    else:
                        self.logger.error('Archive Failed: %s, (%s)', prearcpathfinal, r.reason)

                    self.logger.info('Processing complete, runtime %ds [Proj %s Sub %s Sess %s]' %
                                     ((datetime.datetime.now() - proctime).total_seconds(), self.project, self.subject,
                                      self.session))
                else:
                    self.logger.error('Unable to build and archive, no uploads succeeded [Proj %s Sub %s Sess %s]' %
                                      (self.project, self.subject, self.session))
                    exit(1)

                if self.validate:
                    self.validate_uploads()
                else:
                    self.logger.info('Validation disabled, assuming success')

        self.logger.info("Completed upload of %s in %ss" % (
            self.target, str(datetime.datetime.now() - self.starttime).split('.')[0],))

        return True

    def start_ingestion(self):
        totalsuccess = 0
        totalfiles = 0
        totalsize = 0
        # Load and Validate pattern
        self.load_ingestion_patterns()

        # Analyze targets and suss out required subjects, sessions, and fields per config file
        self.analyze_ingestion_targets()

        # Cycle through subjects and subjects and scans, create. Parallelize upload of resource files.
        for mysubject, mysubjectdata in self.ingestdata.items():
            if self.check_subject(create=True, subject=mysubject, fields=mysubjectdata['fields']) is not True:
                self.logger.error("Subject %s does not exist and cannot be created for project %s" %
                                  (mysubject, self.project))
                exit(1)
            for mysession, mysessiondata in mysubjectdata['sessions'].items():
                if self.check_session(create=True, subject=mysubject, session=mysession,
                                      datatype=mysessiondata['datatype'], xmlnamespace=mysessiondata['xmlnamespace'],
                                      fields=mysessiondata['fields'], custom=mysessiondata['custom']) is not True:
                    self.logger.error("Session %s does not exist and cannot be created for project %s/subject %s, " 
                                      "skipping" % (mysession, self.project, mysubject))
                    continue

                for myscan, myscandata in mysessiondata['scans'].items():
                    for thisfile in myscandata:
                        self.check_scan(create=True, subject=mysubject, session=mysession, scan=myscan,
                                        datatype=mysessiondata['datatype'], xmlnamespace=mysessiondata['xmlnamespace'],
                                        fields=thisfile['fields'])

                        try:
                            (success, total, size) = self.upload_ingestedfile(subject=mysubject,
                                                                              session=mysession,
                                                                              scan=myscan,
                                                                              scandata=thisfile,
                                                                              resource=mysessiondata['resource'])
                        except Exception as e:
                            success, total, size = 0, 0, 0
                            self.logger.error("Scan %s [%s] upload skipped due to errors" % (myscan, thisfile))
                        totalsuccess += success
                        totalfiles += total
                        totalsize += size

                if mysessiondata['resource'] == 'DICOM':
                    self.server_pull_dicomheaders(self.project, mysubject, mysession)

        return totalsuccess, totalfiles, totalsize

    def archive_test(self, filepath, timeout=10):
        # Tests archive validity
        patool_path = find_executable("patool")
        if not patool_path:
            raise ValueError('patool not found! Please install patool!')
        p = easyprocess.EasyProcess([
            sys.executable,
            patool_path,
            '--non-interactive',
            'test',
            filepath
        ]).call(timeout=timeout)
        if p.return_code:
            return False
        return True

    def analyze_dir(self, directory):
        # Analyzes a directory structure to find dicom files for upload
        # Don't bother with single file
        if os.path.isfile(self.target):
            return True
        # Analyze directory tree to find map of uploadable files
        if os.path.exists(directory):
            for d, r, f in os.walk(directory):
                # Cycle through directories
                for subdir in r:
                    if subdir.startswith(".") is not True and subdir not in self.filetree:
                        self.filetree[directory][subdir] = {'dcmfiles': list(), 'archives': list(),
                                                            'otherfiles': list()}
                for subfile in f:
                    if subfile.startswith('.'):
                        self.logger.debug('Hidden file %s skipped' % subfile)
                    else:
                        mysubdir = os.path.basename(os.path.normpath(d))
                        mypath = os.path.join(d, subfile)
                        mime_type = magic.from_file(mypath, mime=True)
                        if mysubdir not in self.filetree[directory]:
                            self.filetree[directory][mysubdir] = {'dcmfiles': list(), 'archives': list(),
                                                                  'otherfiles': list()}
                        if mime_type == 'application/dicom':
                            self.filetree[directory][mysubdir]['dcmfiles'].append(subfile)

                            session_fields = None
                            subject_fields = None
                            # Check if user wants to pull subject and/or session from first dicom file
                            if self.subject is not None:
                                subject_fields = re.search('\(([0-9a-fA-F]+),([0-9a-fA-F]+)\)', self.subject)

                            if self.session is not None:
                                session_fields = re.search('\(([0-9a-fA-F]+),([0-9a-fA-F]+)\)', self.session)

                            td = pydicom.read_file(os.path.join(directory, mysubdir, subfile))
                            if subject_fields is not None:
                                # Set subject
                                self.logger.info('Dicom tag %s specified for subject' % self.subject)
                                self.subject = td[hex(int(subject_fields.group(1), 16)),
                                                  hex(int(subject_fields.group(2), 16))].value.replace(" ", "_")
                                self.logger.info('Subject set to tag value: %s ' % self.subject)
                            if session_fields is not None:
                                # Set session
                                self.logger.info('Dicom tag %s specified for session' % self.session)
                                self.session = td[hex(int(session_fields.group(1), 16)),
                                                  hex(int(session_fields.group(2), 16))].value.replace(" ", "_")
                                self.logger.info('Session set to tag value: %s' % self.session)
                        elif self.archive_test(mypath):
                            if d == directory:
                                self.filetree[directory][subfile] = {'dcmfiles': list(), 'archives': [subfile],
                                                                     'otherfiles': list()}
                            else:
                                self.filetree[directory][mysubdir]['archives'].append(subfile)
                        else:
                            self.logger.debug("File %s/%s non-dicom or archive: %s" % (d, subfile, str(mime_type)))
                            self.filetree[directory][mysubdir]['otherfiles'].append(subfile)
        else:
            self.logger.error('Directory %s does not exist' % (os.path.abspath(directory)))
            exit(1)

        return True

    def analyze_ingestion_targets(self):
        # Analyzes directory of non-dicom files using json definition file to determine parameters and labels
        self.logger.info("Analyzing filesystem: %s" % self.target)
        totalfiles = 0
        totalsize = 0

        # TODO Add support for multiple matches or excludes via list passed in
        match_reg = None
        if 'match' in self.ingestpatterns:
            try:
                match_reg = re.compile(r"%s" % self.ingestpatterns['match'])
            except Exception as e:
                print(e)
                exit(1)

        exclude_reg = None
        if 'exclude' in self.ingestpatterns:
            try:
                exclude_reg = re.compile(r"%s" % self.ingestpatterns['exclude'])
            except Exception as e:
                print ("Exclude Regex error: %s" % e)
                exit(1)

        if os.path.exists(self.target):
            for d, r, f in os.walk(self.target):
                # Cycle through directories
                for subdir in r:
                    if subdir.startswith(".") is not True and subdir not in self.filetree:
                        self.filetree[self.target][subdir] = {'files': {}}
                for subfile in f:
                    if subfile.startswith('.'):
                        self.logger.debug('Hidden file %s skipped' % subfile)
                    else:
                        mypath = os.path.join(d, subfile)
                        relpath = os.path.relpath(mypath, self.target)
                        mime_type = magic.from_file(mypath, mime=True)
                        thisingest = {'subjectfield': {}, 'scanfield': {}, 'sessionfield': {},
                                      'sessionfield-custom': {}, 'scanfield-custom': {}}
                        totalsize += os.path.getsize(mypath)
                        if os.path.getsize(mypath) < 1:
                            self.logger.debug('File %s is smaller than 1 byte, skipping.' % relpath)
                            continue

                        totalfiles += 1

                        if self.newerthan is not None:
                            if datetime.datetime.fromtimestamp(os.path.getmtime(mypath)) <= \
                                    (datetime.datetime.now() - (datetime.timedelta(minutes=int(self.newerthan)))):
                                self.logger.debug('File %s is older than %s minutes, skipping.' %
                                                  (relpath, self.newerthan))
                                continue

                        if self.olderthan is not None:
                            if datetime.datetime.fromtimestamp(os.path.getmtime(mypath)) > \
                                    (datetime.datetime.now() - (datetime.timedelta(minutes=int(self.olderthan)))):
                                self.logger.debug('File %s is newer than %s minutes, skipping.' %
                                                  (relpath, self.olderthan))
                                continue

                        if match_reg is not None and re.match(match_reg, relpath) is None:
                            # Skip file, does not match
                            self.logger.debug('File %s does not match pattern match %s, skipping.' %
                                              (relpath, self.ingestpatterns['match']))
                            continue

                        if exclude_reg is not None and re.match(exclude_reg, relpath):
                            # Skip file, matches exclude
                            self.logger.debug('File %s exclude by match pattern match %s, skipping.' %
                                              (relpath, self.ingestpatterns['exclude']))
                            continue

                        for thispattern in self.ingestpatterns['patterns']:
                            if thispattern['type'] == 'scanfield' or thispattern['type'] == 'sessionfield' or \
                                    thispattern['type'] == 'subjectfield' or \
                                    thispattern['type'] == 'sessionfield-custom' or \
                                    thispattern['type'] == 'scanfield-custom':
                                thisingest[thispattern['type']][thispattern['fieldname']] = \
                                    self.pull_ingestion_field(thispattern, relpath)
                            else:
                                thisingest[thispattern['type']] = self.pull_ingestion_field(thispattern, relpath)

                        # If required fields are missing, use defaults
                        for thisdefault in self.ingestion_required_fields:
                            if thisdefault not in thisingest:
                                thisingest[thisdefault] = self.ingestpatterns['defaults'][thisdefault]

                        # Create subject index
                        if thisingest['subject'] not in self.ingestdata:
                            self.ingestdata[thisingest['subject']] = {'fields': thisingest['subjectfield'],
                                                                      'sessions': {}}

                        # Create session index
                        if thisingest['session'] not in self.ingestdata[thisingest['subject']]['sessions']:
                            self.ingestdata[thisingest['subject']]['sessions'][thisingest['session']] = \
                                {'xmlnamespace': thisingest['xmlnamespace'],
                                 'datatype': thisingest['datatype'],
                                 'resource': thisingest['resource'],
                                 'fields': thisingest['sessionfield'],
                                 'custom': thisingest['sessionfield-custom'],
                                 'scans': {}}
                        # Add scan to scans list
                        if thisingest['scan'] not in \
                                self.ingestdata[thisingest['subject']]['sessions'][thisingest['session']]['scans']:
                            self.ingestdata[thisingest['subject']]['sessions'][thisingest['session']]['scans']\
                                [thisingest['scan']] = []

                        self.ingestdata[thisingest['subject']]['sessions']\
                            [thisingest['session']]['scans'][thisingest['scan']].append({
                                'type': mime_type,
                                'path': mypath,
                                'fields': thisingest['scanfield']
                            })

            self.logger.info("Analyzed ingestion target: %s files @ %s" % (totalfiles, self.bytes_format(totalsize)))
            return True
        else:
            self.logger.error('Target directory %s does not exist' % (os.path.abspath(self.target)))
            exit(1)

    def pull_ingestion_field(self, pattern, filename):
        myoutput = ''

        # Filepath analysis here
        if 'split' in pattern:
            parts = []
            if pattern['source'] == 'filename':
                parts = os.path.basename(filename).split(pattern['split'][0])
            elif pattern['source'] == 'filename-no-ext':
                parts = os.path.basename(filename.rsplit(".", 1)[0]).split(pattern['split'][0])
            elif pattern['source'] == 'filepath':
                parts = filename.split('/')

            # 2nd split argument is list of fields
            try:
                if len(pattern['split']) > 1:
                    myjoin = ''
                    # 3rd split argument is a rejoin character for fields
                    if len(pattern['split']) > 2:
                        myjoin = pattern['split'][2]
                    for thisfield in pattern['split'][1]:
                        myoutput += parts[int(thisfield)-1] + myjoin
                    if len(myjoin) > 0:
                        myoutput = myoutput[:-(len(myjoin))]
                else:
                    myoutput += parts[pattern['split'][0]-1]

                # Subsplit does it again
                if 'subsplit' in pattern:
                    if pattern['source'] == 'filename-no-ext':
                        parts = (myoutput.rsplit(".", 1)[0]).split(pattern['subsplit'][0])
                    else:
                        parts = myoutput.split(pattern['subsplit'][0])

                    # 2nd split argument is list of fields
                    if len(pattern['subsplit']) > 1:
                        myjoin = ''
                        mynewoutput = ''
                        # 3rd split argument is a rejoin character for fields
                        if len(pattern['subsplit']) > 2:
                            myjoin = pattern['subsplit'][2]
                        for thisfield in pattern['subsplit'][1]:
                            mynewoutput += parts[int(thisfield) - 1] + myjoin
                        if len(myjoin) > 0:
                            mynewoutput = mynewoutput[:-(len(myjoin))]
                    myoutput = mynewoutput
            except Exception as e:
                # Error pulling field, return original string

                return myoutput
        else:
            if pattern['source'] == 'filename':
                myoutput = os.path.basename(filename)
            elif pattern['source'] == 'filename-ext':
                myoutput = os.path.basename(filename.rsplit(".", 1)[1])
            elif pattern['source'] == 'filename-no-ext':
                myoutput = os.path.basename(filename.rsplit(".", 1)[0])
            elif pattern['source'] == 'filepath':
                myoutput = os.path.dirname(filename)
            else:
                myoutput = filename

        # Range logic
        if 'range' in pattern:
            if len(pattern['range']) == 1:
                myoutput = myoutput[(pattern['range'][0]-1):]
            else:
                myoutput = myoutput[(pattern['range'][0]-1):(pattern['range'][1]-1)]

        if 'modifiers' in pattern:
            for thismodifier in pattern['modifiers']:
                myoutput = getattr(myoutput, thismodifier)()

        if 'replace' in pattern:
            myoutput = myoutput.replace(pattern['replace'][0], pattern['replace'][1])

        if 'timefmt' in pattern:
            hour = myoutput[0:2]
            minute = myoutput[2:4]
            sec = myoutput[4:6]
            myoutput = hour + ':' + minute + ':' + sec

        if 'datefmt' in pattern:
            month = myoutput[0:2]
            day = myoutput[2:4]
            year = myoutput[4:8]
            myoutput = month + '/' + day + '/' + year

        if 'adatefmt' in pattern:
            year = myoutput[0:4]
            month = myoutput[4:6]
            day = myoutput[6:8]
            myoutput = month + '/' + day + '/' + year

        return myoutput

    def process_scan(self, scan, filetree):
        valdata = dict()
        prearcdate = None
        filecount = 0
        zcount = 0

        if scan == '.':
            self.logger.debug("[%s] Starting upload", self.target)
        else:
            self.logger.debug("[%s] Starting upload", scan)

        if self.raw is True:
            # If raw is set, decompress archive files and upload individually
            if os.path.isfile(self.target):
                self.upload_singlefile(scan)
                filecount = 1
            elif self.scan:
                # What does this do?
                self.upload_datafiles(targetdir=self.target, scan=scan)
            else:
                for thisarchive in filetree[self.target][scan]['archives']:
                    mytmpdir = self.tmpdir + '/xnat-upload-' + uuid.uuid4().hex
                    os.mkdir(mytmpdir)
                    targetarchive = os.path.join(self.target, scan, thisarchive)

                    # Decompression
                    self.logger.debug("[%s] Decompressing %s to %s" % (scan, targetarchive, mytmpdir))
                    Archive(targetarchive).extractall(mytmpdir)

                    # Gather source data information for later validation of upload
                    if self.validate:
                        (zcount, valdata[scan]) = self.validate_dicom_session(mytmpdir, scan)
                        filecount += zcount

                    # Upload
                    self.renew_session()
                    prearcdate = self.upload_rawscan(targetdir=mytmpdir, scan=scan)

                    # Cleanup
                    self.logger.debug("[%s] Cleaning up %s " % (scan, mytmpdir))
                    rmtree(mytmpdir)

                if self.datatype == 'dicom':
                    if len(self.filetree[self.target][scan]['dcmfiles']) > 0:
                        self.renew_session()
                        # Gather source data information for later validation of upload
                        if self.validate:
                            valdata[scan] = self.validate_dicom_session(os.path.join(self.target, scan), scan)
                        # Upload all files in scan dir
                        prearcdate = self.upload_rawscan(targetdir=os.path.join(self.target, scan), scan=scan)
                elif len(self.filetree[self.target][scan]['otherfiles']) > 0:
                    self.renew_session()
                    # Upload all files in scan dir
                    self.upload_datafiles(targetdir=os.path.join(self.target, scan), scan=scan)

        else:
            # Decompress existing archives and rezip files to take advantage of zip handler
            for thisarchive in filetree[self.target][scan]['archives']:
                # Decompress in order to analyze contents
                if scan == thisarchive:
                    targetarchive = os.path.join(self.target, thisarchive)
                else:
                    targetarchive = os.path.join(self.target, scan, thisarchive)
                mytmpdir = self.tmpdir + '/xnat-upload-' + uuid.uuid4().hex
                os.mkdir(mytmpdir)
                self.logger.debug("[%s] Decompressing %s to %s" % (scan, targetarchive, mytmpdir))
                Archive(targetarchive).extractall(mytmpdir)
                # Gather source data information for later validation of upload
                if self.validate:
                    (zcount, valdata) = self.validate_dicom_session(mytmpdir, scan)
                    filecount += zcount
                # Recompress for upload
                myzipfile = ("%s/%s.zip" % (self.tmpdir, uuid.uuid4().hex))
                self.logger.debug("[%s] Recompressing %s (%s files) as %s" %
                                  (scan, mytmpdir, len(os.listdir(mytmpdir)), myzipfile))
                self.zipdir(path=mytmpdir, targetzip=myzipfile)
                dccount = str()
                if zcount > 0:
                    dccount = (" w/ (%s valid dicom files)", zcount)
                self.logger.debug("[%s] Recompressed %s%s as %s" %
                                  (scan, mytmpdir, dccount, myzipfile))
                # Upload to server
                self.renew_session()
                try:
                    prearcdate = self.upload_zipscan(targetzip=myzipfile, scan=scan)

                except requests.exceptions.ReadTimeout:
                    self.logger.error("[%s] failed to upload due to read timeout, increase default from %d" %
                                      (scan, self.timeout))
                except requests.exceptions.ConnectionError:
                    self.logger.error("[%s] failed to upload due to connect timeout, increase default from %d" %
                                      (scan, self.timeout))
                except Exception as e:
                    self.logger.error("[%s] failed to upload due to unknown error: %s" %
                                      (scan, e))

                # Cleanup
                self.logger.debug("[%s] Cleaning up %s & %s" % (scan, mytmpdir, myzipfile))
                rmtree(mytmpdir)
                os.remove(myzipfile)

            # Zip raw files to take advantage of zip handler
            if len(self.filetree[self.target][scan]['dcmfiles']) > 0:
                # Gather source data information for later validation of upload
                mytmpdir = self.tmpdir + '/xnat-upload-' + uuid.uuid4().hex
                os.mkdir(mytmpdir)
                myzipfile = ("%s/%s.zip" % (mytmpdir, scan))
                mysourcedir = os.path.join(self.target, scan)
                self.logger.debug("[%s] Recompressing %s as %s" % (scan, mysourcedir, myzipfile))
                if self.validate:
                    (zcount, valdata) = self.validate_dicom_session(mysourcedir, scan)
                    filecount += zcount
                # Compress
                self.zipdir(path=mysourcedir, targetzip=myzipfile)
                dccount = str()
                if zcount > 0:
                    dccount = (" w/ (%s valid dicom files)", zcount)
                self.logger.debug("[%s] Recompressed %d files from %s%s as %s" %
                                  (scan, len(os.listdir(mytmpdir)), mytmpdir, dccount, myzipfile))
                # Upload
                self.renew_session()
                prearcdate = self.upload_zipscan(targetzip=myzipfile, scan=scan)

                # Cleanup
                self.logger.debug("[%s] Cleaning up %s" % (scan, myzipfile))
                rmtree(mytmpdir)
        return scan, valdata, prearcdate, filecount

    def upload_zipscan(self, targetzip, scan):
        # Uploads a compressed zipfile of scans
        zipsize = os.path.getsize(targetzip)

        self.logger.info('[%s] Uploading zipfile %s (%s) to [Proj %s Sub %s Sess %s Scan %s]' %
                         (scan, targetzip, self.bytes_format(zipsize), self.project, self.subject, self.session, scan))

        bwstarttime = datetime.datetime.now()
        mypayload = dict()
        mydata = open(targetzip, 'rb')
        mypayload['import-handler'] = 'DICOM-zip'
        mypayload['inbody'] = 'true'
        mypayload['PROJECT_ID'] = self.project
        mypayload['SUBJECT_ID'] = self.subject
        mypayload['EXPT_LABEL'] = self.session

        r = None
        try:
            r = self.httpsess.post(url=(self.host + "/data/services/import"), params=mypayload, data=mydata,
                                   timeout=(30, self.timeout))
        except requests.exceptions.ReadTimeout:
            self.logger.error("[%s] failed to upload due to read timeout, increase default from %d" %
                              (scan, self.timeout))
        except requests.exceptions.ConnectionError:
            self.logger.error("[%s] failed to upload due to connect timeout, increase default from %d" %
                              (scan, self.timeout))
        except Exception as e:
            self.logger.error("[%s] failed to upload due to unknown error: %s" %
                              (scan, e))

        if r is not None and r.status_code == 200 and (len(r.text.split('/')) > 4):
            prearcdate = r.text.split('/')[5]
            if self.session is None:
                self.session = r.text.split('/')[6]
                self.session = self.session.strip('\n')
                self.session = self.session.strip('\r')
            transtime = (datetime.datetime.now() - bwstarttime).total_seconds()
            self.logger.info('[%s] Uploaded zipfile (runtime %ds)' % (scan, transtime))
            return prearcdate
        else:
            transtime = (datetime.datetime.now() - bwstarttime).total_seconds()
            self.logger.error('[%s] Failed to upload zipfile (runtime %ds): %s' %
                              (scan, transtime, r.reason))
            return False

    def upload_subzip(self, targetzip, scan):
        # Uploads a compressed file directly from scan subdir, taking dir name as scan name
        zipsize = os.path.getsize(os.path.join(targetzip))

        self.logger.info('[%s] Uploading zipfile %s (%s) to [Proj %s Sub %s Sess %s Scan %s]' %
                         (scan, targetzip, self.bytes_format(zipsize), self.project, self.subject, self.session, scan))

        bwstarttime = datetime.datetime.now()
        mypayload = dict()
        mydata = open(targetzip, 'rb')
        mypayload['import-handler'] = 'DICOM-zip'
        mypayload['inbody'] = 'true'
        mypayload['PROJECT_ID'] = self.project
        mypayload['SUBJECT_ID'] = self.subject
        mypayload['EXPT_LABEL'] = self.session

        r = None
        try:
            r = self.httpsess.post(url=(self.host + "/data/services/import"), params=mypayload, data=mydata,
                                   timeout=(30, self.timeout))
        except requests.exceptions.ReadTimeout:
            self.logger.error("[%s] failed to upload due to read timeout, increase default from %d" %
                              (scan, self.timeout))
            return False
        except requests.exceptions.ConnectionError:
            self.logger.error("[%s] failed to upload due to connect timeout, increase default from %d" %
                              (scan, self.timeout))
        except Exception as e:
            self.logger.error("[%s] failed to upload due to unknown error: %s" %
                              (scan, e))

        if r is not None and r.status_code == 200:
            prearcdate = r.text.split('/')[5]
            if self.session is None:
                self.session = r.text.split('/')[6]
                self.session = self.session.strip('\n')
                self.session = self.session.strip('\r')
            transtime = (datetime.datetime.now() - bwstarttime).total_seconds()
            self.logger.info('[%s] Uploaded zipfile (runtime %ds)' % (scan, transtime))
            return prearcdate
        else:
            transtime = (datetime.datetime.now() - bwstarttime).total_seconds()
            self.logger.error('[%s] Upload failed for zipfile, (runtime %ds): %s' %
                              (scan, transtime, r.reason))
            return False

    def upload_rawscan(self, targetdir, scan):
        # Upload dcm files individually from directory
        targetfiles = list()
        badfiles = list()
        self.logger.debug('[%s] Analyzing %d mimetypes in %s' % (scan, len(os.listdir(targetdir)), targetdir))
        sumsize = 0
        for thisfile in os.listdir(targetdir):
            if magic.from_file(os.path.join(targetdir, thisfile), mime=True) == 'application/dicom':
                targetfiles.append(thisfile)
                sumsize = sumsize + os.path.getsize(os.path.join(targetdir, thisfile))
            else:
                badfiles.append(thisfile)

        if sumsize == 0:
            self.logger.info('[%s] No files suitable for transfer. Skipping', scan)
            return False

        self.logger.info('[%s] Uploading %d dcm files (%s) to [Proj %s Sub %s Sess %s Scan %s], skipping %d '
                         'unsupported files' % (scan, len(targetfiles), self.bytes_format(sumsize), self.project,
                                                self.subject, self.session, scan, len(badfiles)))

        bwstarttime = datetime.datetime.now()
        prearcdate = None
        failreason = None
        upstat = {'success': 0, 'failure': 0, 'total': 0}

        for thisdcm in targetfiles:
            mypayload = dict()
            mydata = open(os.path.join(targetdir, thisdcm), 'rb')
            mypayload['import-handler'] = 'gradual-DICOM'
            mypayload['inbody'] = 'true'
            mypayload['PROJECT_ID'] = self.project
            mypayload['SUBJECT_ID'] = self.subject
            mypayload['EXPT_LABEL'] = self.session

            r = None

            try:
                r = self.httpsess.post(url=(self.host + "/data/services/import"), params=mypayload, data=mydata,
                                       timeout=(30, self.timeout))
            except requests.exceptions.ReadTimeout:
                self.logger.error("[%s] Failed to upload due to read timeout, increase default from %d" %
                                  (scan, self.timeout))
                return False
            except requests.exceptions.ConnectionError:
                self.logger.error("[%s] Failed to upload due to read timeout, increase default from %d" %
                                  (scan, self.timeout))

            if r is not None and r.status_code == 200:
                upstat['success'] += 1
                prearcdate = r.text.split('/')[5]
            else:
                upstat['failure'] += 1
                failreason = r.reason

            upstat['total'] += 1

        transtime = (datetime.datetime.now() - bwstarttime).total_seconds()

        if prearcdate:
            self.logger.info('[%s] Transferred %d files (%d/%d sucessful) (runtime %ds)' %
                             (scan, len(targetfiles), upstat['success'], upstat['total'], transtime))
            return prearcdate
        else:
            self.logger.error('[%s] Failed to transfer %d files (%d/%d sucessful), (runtime %ds): last failure %s' %
                              (scan, len(targetfiles), upstat['failure'], upstat['total'], transtime, failreason))
            return False

    def upload_datafiles(self, targetdir, scan):
        # Upload generic data files individually from directory
        targetfiles = list()

        self.logger.debug('[%s] Analyzing %d datafile in %s' % (scan, len(os.listdir(targetdir)), targetdir))
        sumsize = 0

        if self.scan:
            if os.path.isdir(os.path.join(targetdir, scan, self.scan)):
                mypath = os.path.join(targetdir, scan, self.scan)
            else:
                self.logger.error('Path %s for scan %s does not exist' %
                                  (os.path.join(targetdir, scan, self.scan), self.scan))
                return False
        else:
            mypath = os.path.join(targetdir, scan)

        for thisfile in os.listdir(mypath):
            if thisfile.startswith('.') is not True:
                targetfiles.append(thisfile)
                sumsize = sumsize + os.path.getsize(os.path.join(mypath, thisfile))

        if sumsize == 0:
            self.logger.info('[%s] No files suitable for transfer. Skipping', scan)
            return False

        self.logger.info('[%s] Uploading %d data files (%s) of type %s to [Proj %s Sub %s Sess %s Folder %s]' %
                         (scan, len(targetfiles), self.bytes_format(sumsize), self.datatype, self.project, self.subject,
                          self.session, self.resource))

        bwstarttime = datetime.datetime.now()
        upstat = {'success': 0, 'failure': 0, 'total': 0}
        myurl = ("%s/data/projects/%s/subjects/%s/experiments/%s" %
                 (self.host, self.project, self.subject, self.session))
        if self.scan:
            myurl = ("%s/scans/%s" % (myurl, self.scan))

        for thisfile in targetfiles:
            mypayload = dict()
            mydata = open(os.path.join(mypath, thisfile), 'rb')
            response = None
            try:
                myurl = ("%s/resources/%s/files/%s?inbody=true&update-stats=false&event_reason=batch-upload"
                         "&event_action=Uploaded-%s" % (myurl, self.resource, thisfile, self.datatype))
                response = self.httpsess.post(url=myurl, params=mypayload, data=mydata,
                                              timeout=(30, self.timeout))
            except requests.exceptions.ReadTimeout:
                self.logger.error("[%s] Failed to upload due to read timeout, increase default from %d" %
                                  (scan, self.timeout))
            except requests.exceptions.ConnectionError:
                self.logger.error("[%s] Failed to upload due to read timeout, increase default from %d" %
                                  (scan, self.timeout))

            if response is not None and response.status_code == 200:
                upstat['success'] += 1
            else:
                upstat['failure'] += 1

            upstat['total'] += 1

        transtime = (datetime.datetime.now() - bwstarttime).total_seconds()

        self.logger.info('[%s] Transferred %d files (%d/%d sucessful) (runtime %ds)' %
                         (scan, len(targetfiles), upstat['success'], upstat['total'], transtime))
        return None

    def upload_singlefile(self, scan):
        # Upload generic data files individually
        self.logger.debug('[%s] Analyzing datafile in %s' % (scan, self.target))
        sumsize = os.path.getsize(self.target)

        if sumsize == 0:
            self.logger.info('[%s] No files suitable for transfer. Skipping', scan)
            return False

        self.logger.info('[%s] Uploading data file (%s) of type %s to [Proj %s Sub %s Sess %s Folder %s]' %
                         (scan, self.bytes_format(sumsize), self.datatype, self.project, self.subject,
                          self.session, self.resource))

        bwstarttime = datetime.datetime.now()
        upstat = {'success': 0, 'failure': 0, 'total': 0}
        myurl = ("%s/data/projects/%s/subjects/%s/experiments/%s" %
                 (self.host, self.project, self.subject, self.session))
        if self.scan:
            myurl = ("%s/scans/%s" % (myurl, scan))
        mypayload = self.scanfields
        mydata = open(self.target, 'rb')

        if len(mypayload) > 0:
            self.logger.debug('[%s] Data file has custom fields %s' % self.scanfields)

        response = None
        try:
            myurl = ("%s/resources/%s/files/%s?inbody=true&update-stats=false&event_reason=batch-upload"
                     "&event_action=Uploaded-%s" %
                     (myurl, self.resource, os.path.basename(self.target), self.datatype))
            response = self.httpsess.post(url=myurl, params=mypayload, data=mydata, timeout=(30, self.timeout))
        except requests.exceptions.ReadTimeout:
            self.logger.error("[%s] Failed to upload due to read timeout, increase default from %d" %
                              (scan, self.timeout))
            return None, None, None, 0
        except requests.exceptions.ConnectionError:
            self.logger.error("[%s] Failed to upload due to read timeout, increase default from %d" %
                              (scan, self.timeout))
            return None, None, None, 0

        if response is not None and response.status_code == 200:
            upstat['success'] += 1
        else:
            upstat['failure'] += 1

        upstat['total'] += 1

        transtime = (datetime.datetime.now() - bwstarttime).total_seconds()

        self.logger.info('[%s] Transferred %d files (%d/%d sucessful) (runtime %ds)' %
                         (self.scan, 1, upstat['success'], upstat['total'], transtime))
        return scan, None, None, 1

    def upload_ingestedfile(self, subject=None, session=None, scan=None, scandata=None, resource=None):
        # Upload generic data files individually
        self.logger.debug('[%s] Analyzing datafile in %s' % (scan, self.target))
        sumsize = os.path.getsize(scandata['path'])

        if sumsize == 0:
            self.logger.info('[%s %s %s %s] %s : no files suitable for transfer. Skipping' %
                             (self.project, subject, session, scan, scandata['path']))
            return 0, 0, 0

        self.logger.info('[%s] Uploading data file %s (%s) to [Proj %s Sub %s Sess %s Resource %s]' %
                         (scan, os.path.basename(scandata['path']), self.bytes_format(sumsize), self.project, subject,
                          session, resource))

        bwstarttime = datetime.datetime.now()
        upstat = {'success': 0, 'total': 0}
        myurl = ("%s/data/projects/%s/subjects/%s/experiments/%s/scans/%s" %
                 (self.host, self.project, subject, session, scan))

        mydata = open(scandata['path'], 'rb')

        self.renew_session()
        try:
            myurl = ("%s/resources/%s/files/%s?inbody=true&update-stats=false&event_reason=batch-upload"
                     "&event_action=ScriptedUpload" %
                     (myurl, resource, os.path.basename(scandata['path'])))
            response = self.httpsess.post(url=myurl, data=mydata, timeout=(30, self.timeout))
        except requests.exceptions.ReadTimeout:
            self.logger.error("[%s] Failed to upload due to read timeout, increase default from %d" %
                              (scan, self.timeout))
            return 0, 0, 0
        except requests.exceptions.ConnectionError:
            self.logger.error("[%s] Failed to upload due to read timeout, increase default from %d" %
                              (scan, self.timeout))
            return 0, 0, 0

        upstat['total'] += 1
        if response.status_code == 200:
            upstat['success'] += 1

        transtime = (datetime.datetime.now() - bwstarttime).total_seconds()

        self.logger.debug('[%s] Transferred %d/%d files (runtime %ds)' %
                          (scan, upstat['success'], upstat['total'], transtime))
        return upstat['success'], upstat['total'], sumsize

    def zipdir(self, targetzip, path, fast=False):
        # Zips a scan directory in uploadable format
        scan = os.path.splitext(os.path.basename(targetzip))[0]

        try:
            if fast:
                zipf = zipfile.ZipFile(targetzip, 'w', zipfile.ZIP_STORED)
            else:
                zipf = zipfile.ZipFile(targetzip, 'w', zipfile.ZIP_DEFLATED)

            # ziph is zipfile handle
            zcount = 0
            for root, dirs, files in os.walk(path + '/'):
                for myfile in files:
                    if magic.from_file(os.path.join(root, myfile), mime=True) == 'application/dicom':
                        zipf.write(os.path.join(root, myfile))
                        zcount += 1

            zipf.close()
            return zcount
        except Exception as e:
            self.logger.error("[%s] Recompression failed for %s into %s: %s" % (scan, path, targetzip, e))
            return False

    def check_project(self):
        # Checks project existence on server
        try:
            response = self.httpsess.get(self.host + '/data/archive/projects/%s?accessible=true' % self.project)
            if response.status_code == 200:
                    self.logger.debug('Project %s found' % self.project)
                    return True
        except Exception as e:
            self.logger.error('Error checking project existence %s', str(e))

        return False

    def check_subject(self, create=False, subject=None, fields=None):
        # Checks subject existence on server, create if requested
        if subject is None:
            self.logger.error('Subject is not set, required for this upload.')
            return False

        try:
            response = self.httpsess.get(self.host + '/data/projects/%s/subjects/%s?format=json' %
                                         (self.project, subject))
            if response.status_code == 200:
                self.logger.debug('Subject %s found' % subject)
                return True
        except Exception as e:
            self.logger.error('Error checking subject existence %s', str(e))

        if create is True:
            # create new subject
            # curl - u $CRED - X PUT "$HOST/REST/projects/$PROJECT/subjects/$SUBJECT?event_reason=test&
            # req_format=form&gender=$GENDERTEXT&dob=02/14/$YEAR" - d xnat:subjectData / group = group$GROUP
            response = self.httpsess.put(self.host + '/data/projects/%s/subjects/%s?format=json'
                                                     '&event_action=ScriptedNewSubject' %
                                         (self.project, subject), data=fields)
            if response.status_code == 201:
                if self.verbose:
                    self.logger.debug('Created new subject %s' % subject)
                return True
            else:
                self.logger.debug('Unable to create subject %s: Response code %s' % (subject, response.status_code))

        return False

    def check_session(self, create=False, subject=None, session=None, xmlnamespace=None, datatype=None, fields=None,
                      custom=None):
        # Checks session existence for project/subject, creates with proper fields if necessary
        if subject is None:
            self.logger.error('Session cannot be checked without subject, required for this upload')
            return False

        if session is None:
            self.logger.error('Session is not set, required for this upload')
            return False

        # TODO: Create logic for deleting and recreating session only first time it is seen

        try:
            response = self.httpsess.get(self.host + '/data/projects/%s/subjects/%s/experiments/%s?format=json' %
                                         (self.project, subject, session))
            if response.status_code == 200:
                self.logger.debug('Session %s found' % session)

                return True
        except Exception as e:
            self.logger.error('Error checking session existence %s', str(e))

        if create is True:
            response = self.httpsess.put(self.host +
                                         '/data/projects/%s/subjects/%s/experiments/%s?xsiType=%s:%sSessionData'
                                         '&event_action=ScriptedSessionCreation' % (
                                             self.project,
                                             subject,
                                             session,
                                             xmlnamespace,
                                             datatype))

            if response.status_code == 201:
                if self.verbose:
                    self.logger.debug('Created new session %s as %s:%sSession' % (session, xmlnamespace, datatype))

                if custom is not None:
                    for fieldname, fieldvalue in custom.items():
                        fields['%s:%sSessionData/%s' % (xmlnamespace, datatype, fieldname)] = fieldvalue

                if len(fields) > 0:
                    response = self.httpsess.put(self.host +
                                                 '/data/projects/%s/subjects/%s/experiments/%s'
                                                 '&event_action=ScriptedSessionCreation' % (
                                                     self.project,
                                                     subject,
                                                     session
                                                 ), params=fields)

                    if response.status_code == 200:
                        if self.verbose:
                            self.logger.debug(
                                'Updated session %s with fields: %s' %
                                (session, fields))
                        return True
                    else:
                        self.logger.debug('Unable to update session %s with fields: Response code %s' %
                                          (session, response.status_code))
                        return False

                return True
            else:
                self.logger.debug('Unable to create session %s: Response code %s' % (session, response.status_code))

        return False

    def delete_session(self, create=False, subject=None, session=None):
        # Checks session existence for project/subject, creates with proper fields if necessary
        if subject is None:
            self.logger.error('Session cannot be deleted without subject, required for this deletion')
            return False

        if session is None:
            self.logger.error('Session is not set, required for this deletion')
            return False

        try:
            response = self.httpsess.get(self.host + '/data/projects/%s/subjects/%s/experiments/%s?format=json' %
                                         (self.project, subject, session))
            if response.status_code == 404:
                self.logger.debug('Session %s does not exist, no need to delete' % session)
                return True
        except Exception as e:
            self.logger.error('Error checking session existence %s', str(e))
            return False

        response = self.httpsess.delete("%s/data/projects/%s/subjects/%s/experiments/%s"
                                        "?removeFiles=true&event_action=ScriptedDeletion" % (
                                             self.host,
                                             self.project,
                                             subject,
                                             session
                                         ))

        if response.status_code == 200:
            if self.verbose:
                self.logger.debug('Deleted existing session %s' % (session))
                return True
        else:
            self.logger.debug('Unable to delete session %s: Response code %s' % (session, response.status_code))
            return False

        return False

    def check_scan(self, create=False, subject=None, session=None, scan=None, xmlnamespace=None, datatype=None,
                   fields=None):
        # Check if scan exists, create if requested
        if scan is None:
            self.logger.error('Scan is not set, required for this upload.')
            return False

        # Checks scan existence for project/subject/session, creates with proper fields if necessary
        try:
            response = self.httpsess.get(self.host + '/data/projects/%s/subjects/%s/experiments/%s/scans/%s'
                                                     '?format=json' %
                                         (self.project, subject, session, scan))
            if response.status_code == 200:
                self.logger.debug('Scan %s found' % scan)
                return True
        except Exception as e:
            self.logger.error('Error checking scan existence %s', str(e))

        proc_fields = {}
        if fields is not None:
            for fieldname, fieldvalue in fields.items():
                proc_fields['%s:%sScanData/%s' % (xmlnamespace, datatype, fieldname)] = fieldvalue

        if create is True:
            response = self.httpsess.put(self.host +
                                         '/data/archive/projects/%s/subjects/%s/experiments/%s/scans/%s'
                                         '?xsiType=%s:%sScanData&event_action=ScriptedScanCreation'
                                         % (
                                             self.project,
                                             subject,
                                             session,
                                             scan,
                                             xmlnamespace,
                                             datatype
                                         ), data=proc_fields)

            if response.status_code == 201 or response.status_code == 200:
                if self.verbose:
                    self.logger.debug('Created new scan %s as %s:%s' % (scan, xmlnamespace, datatype))
                return True
            else:
                self.logger.debug('Unable to create scan %s: Response code %s' % (scan, response.status_code))

        return False

    def load_ingestion_patterns(self):
        # Load ingestion pattern and validate
        try:
            if os.path.isfile(self.ingestconfig):
                with open(self.ingestconfig, 'r') as f:
                    self.ingestpatterns = json.load(f)
            else:
                self.logger.error("Ingestion JSON Config %s not found, required for ingestion" % self.ingestconfig)
                exit(1)
        except ValueError as e:
            self.logger.error("Invalid ingestion pattern json, cannot continue: %s" % e)
            exit(1)

        # Checks that ingestion pattern is valid
        found_fields = dict()

        for thisfield in self.ingestion_required_fields:
            found_fields[thisfield] = False

        for thisdefault in self.ingestpatterns['defaults']:
            if thisdefault in self.ingestion_required_fields:
                found_fields[thisdefault] = True

        for thispattern in self.ingestpatterns['patterns']:
            if thispattern['type'] in self.ingestion_required_fields:
                found_fields[thispattern['type']] = True

        if 'project' in found_fields and found_fields['project'] is False and self.project:
            self.ingestpatterns['defaults']['project'] = self.project
            found_fields['project'] = True

        if 'subject'in found_fields and found_fields['subject'] is False and self.subject:
            self.ingestpatterns['defaults']['subject'] = self.subject
            found_fields['subject'] = True

        if 'session'in found_fields and found_fields['session'] is False and self.session:
            self.ingestpatterns['defaults']['session'] = self.session
            found_fields['session'] = True

        for thisfield in self.ingestion_required_fields:
            if found_fields[thisfield] is False:
                self.logger.error("Ingestion Pattern error: required field %s not found, and no default defined" %
                                  thisfield)
                exit(1)

        return True

    def validate_uploads(self):
        # Validate that uploaded scans match local data
        self.logger.info('Upload Validation:')
        scan_ssum = 0
        scan_lsum = 0
        scansserver = self.get_serverscans()
        scanslocal = self.localval

        for thisscan in scanslocal:
            scan_dcomp = (scanslocal[thisscan]['desc'] == scansserver[thisscan]['desc'])
            scan_ccomp = (scanslocal[thisscan]['count'] == scansserver[thisscan]['count'])

            if scan_dcomp and scan_ccomp:
                self.logger.info('MATCH: Series %d (%s/%s)/%d files: [Series: %s] [Count: %s]' %
                                 (thisscan, scanslocal[thisscan]['localname'], scanslocal[thisscan]['desc'],
                                  scanslocal[thisscan]['count'], str(scan_dcomp), str(scan_ccomp)))
            else:
                if scan_ccomp is False:
                    scan_ccomp = ('%s: %s local vs %s remote' % (scan_ccomp, scanslocal[thisscan]['count'],
                                                                 scansserver[thisscan]['count']))
                if scan_dcomp is False:
                    scan_dcomp = ('%s: %s local vs %s remote' % (scan_dcomp, scanslocal[thisscan]['desc'],
                                                                 scansserver[thisscan]['desc']))

                self.logger.error('ERROR: Series %d (%s/%s)/%d files: [Series: %s] [Count %s]' %
                                  (thisscan, scanslocal[thisscan]['localname'], scanslocal[thisscan]['desc'],
                                   scanslocal[thisscan]['count'], str(scan_dcomp), str(scan_ccomp)))
            scan_ssum += scanslocal[thisscan]['count']
            scan_lsum += scansserver[thisscan]['count']

        if scan_ssum == scan_lsum:
            self.logger.info('MATCH: [Source files %d]/[Server files %d]' % (scan_ssum, scan_lsum))
            return True
        else:
            self.logger.info('ERROR: [Source files %d]/[Server files %d]' % (scan_ssum, scan_lsum))
            return False

    def validate_dicom_session(self, targetpath, scan):
        # Validate dicom session
        dd = dict()
        zcount = 0
        # Creates index of dicom series names from files in dir
        for f in os.listdir(targetpath):
            if magic.from_file(os.path.join(targetpath, f), mime=True) == 'application/dicom':
                td = pydicom.read_file(os.path.join(targetpath, f))
                if td.SeriesNumber not in dd:
                    dd[int(td.SeriesNumber)] = {'desc': td.SeriesDescription, 'count': 1, 'localname': scan}
                    zcount += 1
                else:
                    dd[int(td.SeriesNumber)]['count'] += 1
                    zcount += 1

        if len(dd) > 1:
            self.logger.warning('[%s] More than one series detected in scan: %s' % (scan, str(dd.keys())))

        return zcount, dd

    def server_pull_dicomheaders(self, project, subject, session):
        # Trigger final pull of remote headers via api for all sessions
        # 'http://my.xnat.org/REST/projects/MyProject/subjects/ThisSubject/experiments/ThisSession?pullDataFromHeaders=true'
        self.renew_session()
        self.logger.info(
            "Pulling headers from session %s [%s %s]" % (session, project, subject))
        response = self.httpsess.put(
            self.host + '/REST/projects/%s/subjects/%s/experiments/%s?pullDataFromHeaders=true' %
            (project, subject, session))

        return True

    def get_serverscans(self):
        # Gathers server side upload for validation
        self.renew_session()
        scandata = dict()
        try:
            mypayload = {'format': 'json'}
            scans = self.httpsess.get(("%s/data/archive/projects/%s/subjects/%s/experiments/%s/scans/" %
                                       (self.host, self.project, self.subject, self.session)),
                                      params=mypayload).json()

            for thisscan in scans['ResultSet']['Result']:
                scandata[int(thisscan['ID'])] = {'desc': thisscan['series_description'], 'count': 0}
                filelist = self.httpsess.get("%s/data/archive/projects/%s/subjects/%s/experiments/%s/scans/%s/"
                                             "resources/DICOM/files" %
                                             (self.host, self.project, self.subject, self.session, thisscan['ID']),
                                             params=mypayload).json()

                scandata[int(thisscan['ID'])]['count'] += len(filelist['ResultSet']['Result'])

            return scandata
        except Exception as e:
            self.logger.error(('Error retrieving file validation data from %s: %s' % (self.host, str(e))))

        return False

    def bytes_format(self, number_of_bytes):
        # Formats byte to human readable text
        if number_of_bytes < 0:
            raise ValueError("number_of_bytes can't be smaller than 0 !!!")

        step_to_greater_unit = 1024.

        number_of_bytes = float(number_of_bytes)
        unit = 'bytes'

        if (number_of_bytes / step_to_greater_unit) >= 1:
            number_of_bytes /= step_to_greater_unit
            unit = 'KB'

        if (number_of_bytes / step_to_greater_unit) >= 1:
            number_of_bytes /= step_to_greater_unit
            unit = 'MB'

        if (number_of_bytes / step_to_greater_unit) >= 1:
            number_of_bytes /= step_to_greater_unit
            unit = 'GB'

        if (number_of_bytes / step_to_greater_unit) >= 1:
            number_of_bytes /= step_to_greater_unit
            unit = 'TB'

        precision = 1
        number_of_bytes = round(number_of_bytes, precision)

        return str(number_of_bytes) + ' ' + unit

    def renew_session(self):
        # Set up request session and get cookie
        if self.lastrenew is None or ((self.lastrenew + self.sessiontimeout) < datetime.datetime.now()):
            self.logger.info('[SESSION] Renewing http session as %s from %s with timeout %d' % (self.username,
                                                                                                self.host,
                                                                                                self.timeout))
            # Renew expired session, or set up new session
            self.httpsess = requests.Session()

            # Retry logic
            retry = Retry(connect=5, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            self.httpsess.mount('http://', adapter)
            self.httpsess.mount('https://', adapter)

            # Log in and generate xnat session
            response = self.httpsess.post(self.host + '/data/JSESSION', auth=(self.username, self.password),
                                          timeout=(30, self.timeout))
            if response.status_code != 200:
                self.logger.error("[SESSION] Renewal failed, no session acquired: %d %s" % (response.status_code,
                                                                                          response.reason))
                exit(1)

            self.lastrenew = datetime.datetime.now()
        else:
            self.logger.debug('[SESSION] Reusing existing https session until %s' % (self.lastrenew + self.sessiontimeout))

        return True

    def close_session(self):
        # Logs out of session for cleanup
        self.httpsess.delete(self.host + '/data/JSESSION', timeout=(30, self.timeout))
        self.logger.debug('[SESSION] Deleting https session')
        self.httpsess.close()
        return True
