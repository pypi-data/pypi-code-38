from lbCVMFSReporting.Utils import Utils
from lbCVMFSReporting.APIInfoAgent import APIInfoAgent
from lbCVMFSReporting.Parser import Parser
import json
import urllib2
import urllib
import os
import datetime
from lbCVMFSReporting.LbInfluxDBConnector import getConnector


class LbCVMFSReport:

    def __init__(self, date):
        self.shouldInstall = Utils.getSlotsProjects(date)
        self.logsData = Parser.slotsTuplesFromLogs(date, self.shouldInstall)
        self.dataPrint = self._convertDataLogsToArray()
        self.date = date

    def _convertDataLogsToArray(self):
        dataArray = []
        keys = self.logsData.keys()
        keys = sorted(keys, key=lambda slot: self.logsData[slot]['priority'],
                      reverse=True)
        for slot in keys:
            if len(self.logsData[slot].keys()) == 1:
                dataArray.append([slot, '', '', '', '', ''])
                for p in self.shouldInstall[slot]['projects']:
                    for plat in self.shouldInstall[slot]['platforms']:
                        dataArray.append([slot, '', p, plat, '', ''])
                dataArray.append(['', '', '', '', '', ''])
            for build in self.logsData[slot].keys():
                if build in ['priority']:
                    continue
                dataArray.append(
                    [slot, '', '', '', self.logsData[slot][build]['min'],
                     self.logsData[slot][build]['max']])
                tmp_data = []
                for project in self.logsData[slot][build].keys():
                    if project in ['min', 'max']:
                        continue
                    for platform in self.logsData[slot][build][project].keys():
                        tmp_data.append([slot, build, project, platform,
                                         self.logsData[slot][build][project][
                                             platform]['start_date'],
                                         self.logsData[slot][build][project][
                                             platform]['install_time']])
                tmp_data.sort(key=Utils.cmpList)
                dataArray.extend(tmp_data)
                dataArray.append(['', '', '', '', '', ''])
        return dataArray

    def _getExtraInfo(self):
        total = 0
        installed = 0
        min = None
        slotsProgress = {}
        extra = {
            'usage': {},
            'slots_info': {}
        }
        for line in self.dataPrint:
            if line[0] != '' and line[2] != '' and line[3] != '':
                total += 1
                if line[4] != '' and (min is None or min > line[4]):
                    min = line[4]
                if line[5] != '':
                    installed += 1
                if not slotsProgress.get(line[0], None):
                    slotsProgress[line[0]] = {
                        'total': 0,
                        'priority': self.logsData[line[0]]['priority'],
                        'installed': 0,
                        'started': None,
                        'ended': None}
                if line[4] != '' and (
                        slotsProgress[line[0]]['started'] is None or
                        slotsProgress[line[0]]['started'] > line[4]):
                    slotsProgress[line[0]]['started'] = line[4]
                if line[5] != '' and (
                        slotsProgress[line[0]]['ended'] is None or
                        slotsProgress[line[0]]['ended'] > line[5]):
                    slotsProgress[line[0]]['ended'] = line[5]
                slotsProgress[line[0]]['total'] += 1
                if line[5] != '':
                    slotsProgress[line[0]]['installed'] += 1
        extra['slots_info'] = slotsProgress
        return extra

    def convertDataLogsToJson(self):
        agent = APIInfoAgent()
        extra = self._getExtraInfo()
        extra['usage'] = agent.getInfoForReport()
        extra['completed_builds'] = {}
        for slot in self.shouldInstall.keys():
            completed_builds_counter = 0
            for p in self.shouldInstall[slot]['completed']:
                if p['is_build'] is True:
                    completed_builds_counter += 1
            extra['completed_builds'][slot] = completed_builds_counter
        to_return = {
            'summary': extra,
            'slots': self.logsData,
        }
        return json.dumps(to_return)

    def sendToNightlies(self):
        try:
            # url = 'http://pclhcb13.cern.ch:8000/'
            url = 'https://lhcb-nightlies.cern.ch/'
            url += 'ajax/cvmfsReport/' + str(self.date) + '/'
            payload = urllib.urlencode(
                {'payload': self.convertDataLogsToJson()})
            r = urllib2.urlopen(url=url, data=payload)
            r.read()
        except urllib2.HTTPError as e:
            print(e)
        self.sendDataToInflux()

    def saveToDisk(self):
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        json_file_path = os.path.join(os.environ.get("HOME"), "reports",
                                      "report%s.json" % now)
        with open(json_file_path, 'w') as f:
            f.write(self.convertDataLogsToJson())

    def sendDataToInflux(self):
        now = datetime.datetime.now()
        current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        db_entries = []

        for slot in self.logsData.keys():
            for build in self.logsData[slot]:
                if build in ['priority']:
                    continue
                for project in self.logsData[slot][build]:
                    if project in ['min', 'max']:
                        continue
                    for platform in self.logsData[slot][build][project]:
                        start = self.logsData[slot][build][project][platform].get(
                            'start_date', 'None')
                        end = self.logsData[slot][build][project][platform].get(
                            'install_time', 'None')
                        if start == '':
                            start = 'None'
                        if end == '':
                            end = 'None'
                        db_entry = {
                            'measurement': "nightlies_installation",
                            'tags': {
                                'slot': str(slot),
                                'build': str(build),
                                'platform': str(platform),
                                'project': str(project)
                            },
                            "time": current_time,
                            'fields': {
                                'start_date': start,
                                'install_time': end
                            }
                        }
                        db_entries.append(db_entry)
        getConnector().write_points(db_entries)
