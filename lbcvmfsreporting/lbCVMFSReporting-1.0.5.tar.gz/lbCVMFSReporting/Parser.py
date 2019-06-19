import os
import re
from lbCVMFSReporting.Utils import Utils
import lbmessaging


class Parser:

    @staticmethod
    def slotsTuplesFromLogs(date, shouldInstall):
        slotsPrriority = Utils.getSlots()
        logsData = {}
        skip = True
        log_path = os.path.join(os.environ.get("HOME"), "logs", "manager.log")
        for slot in shouldInstall.keys():
            if not logsData.get(slot, None):
                try:
                    priority = slotsPrriority.index(slot)
                except:
                    priority = len(slotsPrriority)
                len_positions = len(slotsPrriority)
                slot_priority = (len_positions - priority) * 1.0 / len_positions
                raw_priority = slot_priority / 2.0
                priority = lbmessaging.priority(lbmessaging.LOW, raw_priority)
                logsData[slot] = {'priority': priority}
        with open(log_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if date not in line:
                    continue
                if 'Starting execute /home/cvlhcbdev/' \
                   'bin/installNightlies' in line:
                    skip = False
                if 'Finished command from client with id: ' \
                   'installNightlies' in line:
                    skip = True
                if not skip:
                    if 'Starting executing: (' in line:
                        matchObj = re.match(
                            r'(.*)\[RUNNING-installNightlies'
                            r'(.*)Starting executing: \((.*)\)',
                            line,
                            re.M | re.I)
                        if matchObj:
                            date_start = matchObj.group(1).replace(
                                '[', '').replace(']', '')
                            tmp = matchObj.group(3).split(',')
                            slot = tmp[0].replace('\'', '').replace(' ', '')
                            platform = tmp[2].replace(' u\'', '').replace(
                                '\'', '').replace(' ', '')
                            build_id = tmp[1].replace(' ', '').replace(
                                '\'', '').replace(' ', '')
                            project = tmp[3].replace(' u\'', '').replace(
                                '\'', '').replace(' ', '')
                            if not logsData.get(slot, None):
                                if not shouldInstall.get(slot, None):
                                    skip = True
                                    continue
                                try:
                                    priority = slotsPrriority.index(slot)
                                except:
                                    priority = 0
                                logsData[slot] = {'priority': priority}
                            if not logsData[slot].get(build_id, None):
                                logsData[slot][build_id] = {}
                                for p in shouldInstall[slot]['projects']:
                                    logsData[slot][build_id][p] = {}
                                    plats = shouldInstall[slot]['platforms']
                                    for plat in plats:
                                        logsData[slot][build_id][p][plat] = {
                                            'start_date': '',
                                            'install_time': ''}
                            if not logsData[slot][build_id].get(project, None):
                                skip = True
                                continue
                            if not logsData[slot][build_id][project].get(
                                    platform, None):
                                skip = True
                                continue
                            logsData[slot][build_id][project][platform][
                                'start_date'] = date_start
                    if 'Successfully executed: (' in line:
                        matchObj = re.match(
                            r'(.*)\[RUNNING-installNightlies'
                            r'(.*)Successfully executed: \((.*)\)',
                            line,
                            re.M | re.I)
                        if matchObj:
                            date_end = matchObj.group(1).replace('[',
                                                                 '').replace(
                                ']', '')
                            tmp = matchObj.group(3).split(',')
                            slot = tmp[0].replace('\'', '').replace(' ', '')
                            platform = tmp[2].replace(' u\'', '').replace(
                                '\'', '').replace(' ', '')
                            build_id = tmp[1].replace(' ', '').replace(
                                '\'', '').replace(' ', '')
                            project = tmp[3].replace(' u\'', '').replace(
                                '\'', '').replace(' ', '')
                            if not logsData.get(slot, None):
                                continue
                            if not logsData[slot].get(build_id, None):
                                continue
                            if not logsData[slot][build_id].get(project, None):
                                continue
                            if not logsData[slot][build_id][project].get(
                                    platform, None):
                                continue
                            logsData[slot][build_id][project][platform][
                                'install_time'] = date_end
        for slot in logsData.keys():
            for build in logsData[slot].keys():
                min = None
                max = None
                if build in ['priority']:
                    continue
                for project in logsData[slot][build].keys():
                    for platform in logsData[slot][build][project].keys():
                        sDate = logsData[slot][build][project][
                            platform]['start_date']
                        iDate = logsData[slot][build][project][
                            platform]['install_time']
                        if min is None or min > sDate:
                            if sDate != '':
                                min = sDate
                        if iDate == '':
                            max = ''
                        if max != '' and (max is None or max < iDate):
                            max = iDate
                logsData[slot][build]['max'] = max
                logsData[slot][build]['min'] = min
        return logsData
