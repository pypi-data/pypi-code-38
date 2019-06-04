'''
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
 *
'''
import logging
from abc import ABCMeta
from datetime import datetime

from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC

logger = logging.getLogger(__name__)


class PeekServerConfigLicMixin:
    ### CAPABILITIES SECTION ###
    @property
    def capabilities(self):

        # from peek_server.server.auth import AuthValue
        from peek_server.storage.Setting import globalSetting, SYSTEM_NAME
        from peek_server.storage.Setting import internalSetting, CAPABILITIES_KEY

        if not hasattr(self, '_capabilities'):
            self._capabilities = None

        # if not self._capabilities:
        #     data = internalSetting()[CAPABILITIES_KEY]
        #     AuthValue.loadCapabilities(self, data)

        if not self._capabilities:
            self._capabilities = {'sid': 'SER-VER-ID-01', #AuthValue.authKey(),
                                  'upd': "01-Jan-2014",

                                  'lil': 20,
                                  'lin': "Unlicensed",

                                  'sun': "Not Supported",
                                  'sul': 0,
                                  'aud': False,
                                  'dii': False,

                                  }

        self._capabilities['upd'] = "01-Jan-2018"  # DEBUG

        lic = self._capabilities
        # session = getNovaOrmSession()

        # def limitText(countKey, limitKey):
        #     limit = lic[limitKey]
        #     count = lic[countKey]
        #     return "%s out of %s" % (count, ("Unlimited" if limit == -1 else limit))

        lic['serverName'] = globalSetting()[SYSTEM_NAME]

        # lic['planCount'] = session.query(Plan).count()
        # lic['planCountText'] = limitText('planCount', 'plc')
        # lic['planCountExceeded'] = (lic['plc'] != -1
        #                             and lic['planCount'] > lic['plc'])
        #
        #
        # lic['execHistoryCountText'] = ("Unlimited" if lic['ehc'] == -1 else lic['ehc'])

        upd = datetime.strptime(lic['upd'], '%d-%b-%Y')
        lic['supportExceeded'] = upd < datetime.today()
        lic['demoExceeded'] = lic['lil'] == 20 and lic['supportExceeded']
        lic['countsExceeded'] = False
        # (lic['planCountExceeded']
        #                      or lic['scheduleCountExceeded']
        #                      or lic['placevalueCountExceeded'])

        if lic['supportExceeded']:
            lic['sun'] = "Expired"

        return self._capabilities
