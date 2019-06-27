from __future__ import unicode_literals, absolute_import
'''
 Copyright 2013-2019 Cofense, Inc.  All rights reserved.

 This software is provided by PhishMe, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
 including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
 disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
 consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
 this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.
'''

import logging
import os
import random
import copy
import sys
import time
from calendar import timegm
from datetime import datetime, timedelta

from .api import IntelligenceAPI
from .output import JsonFileOutput

# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]

LOGGER = logging.getLogger(__name__)

class CFIntelBase(object):

    default_config = {'CF_USER': None,
                      'CF_PASS': None,
                      'INTEL_FORMAT': 'json',
                      'THREAT_TYPE': 'malware',
                      'PROXY_URL': None,
                      'PROXY_AUTH': False,
                      'PROXY_USER': None,
                      'PROXY_PASS': None,
                      'SSL_VERIFY': False,
                      'INTEGRATION': JsonFileOutput}

    def __init__(self, integration_root=None, **kwargs):

        if not integration_root:
            integration_root = os.getcwd()

        self.logger = LOGGER
        self.logger.info('Initialized Cofense Intelligence Sync')

        self.config = copy.deepcopy(self.default_config)
        self.config['BASE_DIR'] = integration_root

        self.config.update(kwargs)

        self.api_mgr = self.api_config()

    def api_config(self):
        auth = (self.config['CF_USER'], self.config['CF_PASS'])
        max_retries = self.config.get('MAX_RETRIES') or 3
        proxy = self.config.get('PROXY_URL') or None
        if self.config['PROXY_AUTH']:
            proxy_auth = (self.config['PROXY_USER'], self.config['PROXY_PASS'])
        else:
            proxy_auth = None
        verify = self.config['SSL_VERIFY']
        integration = self.config['INTEGRATION']

        return IntelligenceAPI(auth=auth,
                               max_retries=max_retries,
                               proxy=proxy,
                               proxy_auth=proxy_auth,
                               verify=verify,
                               integration=integration)


class CFIntelSync(CFIntelBase):

    sync_defaults = {'JITTER': True,
                     'POSITION': None,
                     'USE_LOCK': True}

    def __init__(self, **kwargs):
        super(CFIntelSync, self).__init__(**kwargs)

        self.config.update(self.sync_defaults)
        self.config.update(kwargs)

        self.begin_date = self.config.get('INIT_DATE')

        self.scheduler_offset = self.config.get('JITTER')

        if not self.config.get('LOCK_FILE'):
            self.config['LOCK_FILE'] = self.config['BASE_DIR'] + '/cf_intel.lock'
        if not self.config.get('POSITION_FILE'):
            self.config['POSITION_FILE'] = self.config['BASE_DIR'] + '/cf_intel.pos'

        if os.path.isfile(self.config['POSITION_FILE']):
            with open(self.config['POSITION_FILE'], 'r') as pos_file:
                self.config['POSITION'] = pos_file.read().rstrip()

    @property
    def begin_date(self):
        return self._begin_date

    @begin_date.setter
    def begin_date(self, init_date):
        if not init_date:
            begin_date = datetime.now() + timedelta(days=-30)
            self._begin_date = timegm(begin_date.timetuple())
        else:
            if not isinstance(init_date, int):
                raise ValueError('INIT_DATE must be a integer')

            self._begin_date = init_date

    @property
    def scheduler_offset(self):
        return self._scheduler_offset

    @scheduler_offset.setter
    def scheduler_offset(self, jitter):
        if jitter:
            if not self.config.get('SCHEDULER_OFFSET'):
                offset = random.randint(0, 600) - 1
                self._scheduler_offset = offset
            else:
                self._scheduler_offset = self.config['SCHEDULER_OFFSET']

    def backfill_cef(self, begin_time, end_time):
        threat_type = self.config.get('THREAT_TYPE')
        message_types = {'intelligence': 'malware', 'brand intelligence': 'phish'}

        while begin_time < end_time:
            if (end_time - begin_time) > 86400:
                block_end_time = begin_time + 86400
            else:
                block_end_time = end_time

            cef_messages = self.api_mgr.get_aggregate_t3('cef', begin_time=begin_time, end_time=block_end_time)

            for message in cef_messages.splitlines():
                if threat_type == 'all':
                    yield message
                else:
                    message_type = message.split('|')[2].lower()
                    if message_types[message_type] == threat_type:
                        yield message

            begin_time += 86400

    def backfill_standard(self, begin_time, end_time, fmt):
        threat_type = self.config.get('THREAT_TYPE')

        threat_reports = self.api_mgr.threat_search(threatType=threat_type, beginTimestamp=begin_time, endTimestamp=end_time)

        if fmt == 'stix':
            return self.backfill_stix(threat_reports)
        else:
            return threat_reports

    def backfill_stix(self, threat_reports):

        for report in threat_reports:
            yield self.api_mgr.get_t3(report.threat_id, 'stix', report.threat_type.lower())

    def backfill(self, fmat, begin_time):
        end_time = round(datetime.today().timestamp())
        if fmat == 'cef':
            threat_reports = self.backfill_cef(begin_time, end_time)
        else:
            threat_reports = self.backfill_standard(begin_time, end_time, fmat)

        return threat_reports

    def get_json_update(self, threat_id, threat_type):
        return self.api_mgr.get_threat(threat_type, threat_id)

    def get_cef_update(self, threat_id, threat_type):
        return self.api_mgr.get_t3(threat_id, 'cef', threat_type)

    def get_stix_update(self, threat_id, threat_type):
        return self.api_mgr.get_t3(threat_id, 'stix', threat_type)

    def get_update(self, threat_id, threat_type):
        format_methods = {'json': self.get_json_update, 'cef': self.get_cef_update, 'stix': self.get_stix_update}

        format_method = format_methods[self.config['INTEL_FORMAT']]

        threat_report = format_method(threat_id, threat_type)

        return threat_report

    def update_position(self, position):
        self.config['POSITION'] = position
        with open(self.config['POSITION_FILE'], 'w') as pos_file:
            pos_file.write(position)

    def jitter_pause(self):
        self.logger.info('Jitter set. Delaying sync start by {} seconds'.format(self.scheduler_offset))
        time.sleep(self.scheduler_offset)

    def run(self):

        if self.config['USE_LOCK']:
            if os.path.isfile(self.config['LOCK_FILE']):
                return False
            lock_handler = open(self.config['LOCK_FILE'], 'w')
            lock_handler.close()

        integration_cls = self.config['INTEGRATION']
        integration = integration_cls(self.config)

        if self.config['THREAT_TYPE'] != 'all':
            threat_type = self.config['THREAT_TYPE']
        else:
            threat_type = None

        if self.config.get('JITTER'):
            self.jitter_pause()

        if not self.config['POSITION']:
            self.logger.info('No position marker set. Backfilling from {} date'.format(self.begin_date))
            end_time = round(time.time())
            backfill_reports = self.backfill(self.config['INTEL_FORMAT'], self.begin_date)

            for report in backfill_reports:
                integration.process(report)

            position, updates = self.api_mgr.threat_updates(threat_type=threat_type, begin_time=end_time)

            for update in updates:
                report = self.get_update(update.get('threatId'), update.get('threatType'))
                integration.process(report)

            self.update_position(position)

        position, updates = self.api_mgr.threat_updates(threat_type=threat_type, position=self.config['POSITION'])

        for update in updates:
            report = self.get_update(update.get('threatId'), update.get('threatType'))
            integration.process(report)

        self.update_position(position)

        self.logger.info('Sync Complete. Most recent position: ' + position)

        if self.config['USE_LOCK']:
            os.remove(self.config['LOCK_FILE'])
