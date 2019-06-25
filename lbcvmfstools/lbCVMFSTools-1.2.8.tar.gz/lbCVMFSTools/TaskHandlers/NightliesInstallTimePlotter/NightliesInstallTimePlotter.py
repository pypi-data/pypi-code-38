###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
CVMFS nightlies installer
@author: Stefan-Gabriel CHITIC, Ben Couturier
'''
import logging
import datetime
import re
import json
import urllib2
import urllib

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface

FREQ = 10 * 60

class NightliesInstallTimePlotter(TaskHandlerInterface, object):

    MODE_PARSE_DATE = 'ParsingRowData'
    MODE_AGGREGATE_DATA = 'AggregateData'
    MODE_PLOT_DATA = 'PlotData'
    MODES = [MODE_PARSE_DATE, MODE_AGGREGATE_DATA, MODE_PLOT_DATA]

    def __init__(self, logsName, date=None, *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(NightliesInstallTimePlotter, self).__init__(FREQ, *args, **kwargs)
        self.logsName = logsName
        self.date = None
        if date:
            self.date = date
        logging.getLogger().setLevel(logging.INFO)

    def get_list_of_tasks(self):
        return self.MODES

    def perform_task(self, tasks):
        if tasks == self.MODE_PARSE_DATE:
            self._parseData()
        if tasks == self.MODE_AGGREGATE_DATA:
            self._aggregateData()
        if tasks == self.MODE_PLOT_DATA:
            self._plotData()

    def _parseData(self):
        if self.date:
            today_str = self.date
        else:
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        self.date = today_str
        self.data = {}
        with open(self.logsName, 'r') as f:
            lines = f.readlines()
            start_platform = False
            for line in lines:
                if today_str not in line:
                    continue
                if start_platform is False:
                    if "Starting executing: (u'" in line:
                        matchObj = re.match(
                            r'(.*) Starting executing: (.*)',
                            line,
                            re.M | re.I)
                        install_identification_row = matchObj.group(2).replace(
                            '(', '').replace(')', '').split(',')
                        slot_name = install_identification_row[0].replace('u\'','').replace('\'','')
                        build_name = int(install_identification_row[1])
                        platform = install_identification_row[2].replace(' u\'','').replace('\'','')
                        start_date = datetime.datetime.strptime(line[1:20], "%Y-%m-%d %H:%M:%S")
                        start_platform = True
                else:
                    if 'Successfully executed: (u\'' in line:
                        matchObj = re.match(
                            r'(.*) Successfully executed: (.*)',
                            line,
                            re.M | re.I)
                        install_identification_row = matchObj.group(2).replace(
                            '(', '').replace(')', '').split(',')
                        slot_name_end = install_identification_row[0].replace('u\'','').replace('\'','')
                        build_name_end = int(install_identification_row[1])
                        platform_end = install_identification_row[2].replace(' u\'','').replace('\'','')
                        finish_date = datetime.datetime.strptime(line[1:20], "%Y-%m-%d %H:%M:%S")
                        start_platform = False
                        if slot_name != slot_name_end or build_name != build_name_end or platform != platform_end:
                            print "Error with %s-%s-%s" % (slot_name, build_name, platform)
                        else:
                            id = '%s-%s-%s' % (slot_name, build_name, platform)
                            if not self.data.get(id, None):
                                self.data[id] = {
                                    'slot': slot_name,
                                    'build': build_name,
                                    'platform': platform,
                                    'total_time': [],
                                    'lbninstall_time': [],
                                    'transaction_time': []
                                }
                            total_time = (finish_date - start_date)
                            total_time = (total_time.seconds + total_time.days * 24 * 3600)
                            lbninstall_time = (lbninstall_end - lbninstall_start)
                            lbninstall_time = (lbninstall_time.seconds + lbninstall_time.days * 24 * 3600)
                            transaction_time = (finish_date - cvmfs_transaction_start)
                            transaction_time = (transaction_time.seconds + transaction_time.days * 24 * 3600)

                            self.data[id]['total_time'].append(total_time)
                            self.data[id]['lbninstall_time'].append(lbninstall_time)
                            self.data[id]['transaction_time'].append(transaction_time)
                    if 'Invoking: lbn-install' in line:
                        lbninstall_start = datetime.datetime.strptime(line[1:20], "%Y-%m-%d %H:%M:%S")
                    if 'Sending transaction' in line:
                        lbninstall_end = datetime.datetime.strptime(line[1:20], "%Y-%m-%d %H:%M:%S")
                    if 'Processing changes' in line:
                        cvmfs_transaction_start = datetime.datetime.strptime(line[1:20], "%Y-%m-%d %H:%M:%S") 

    def _aggregateData(self):
        self.agrgatedData={}
        for key in self.data.keys():
            self.agrgatedData[key] = {
                'slot': self.data[key]['slot'],
                'build': self.data[key]['build'],
                'platform': self.data[key]['platform'],
                'total_time': 0,
                'lbninstall_time': 0,
                'transaction_time': 0
            }
            for t in self.data[key]['total_time']:
                self.agrgatedData[key]['total_time'] += t
            for t in self.data[key]['transaction_time']:
                self.agrgatedData[key]['transaction_time'] += t
            for t in self.data[key]['lbninstall_time']:
                self.agrgatedData[key]['lbninstall_time'] += t                

    def _plotData(self):
        try:
            url = "https://lhcb-nightlies.cern.ch/updateCVMFSstats/?"
            url += 'date=%s' % self.date
            data =  urllib.urlencode({'json': json.dumps(self.agrgatedData)})
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            result = response.read()
        except urllib2.HTTPError as e:
            print e.code
