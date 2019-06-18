#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
from netbluemind.python import serder

class UpgradeReportUpgraderReport :
    def __init__( self):
        self.major = None
        self.build = None
        self.status = None
        pass

class __UpgradeReportUpgraderReportSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = UpgradeReportUpgraderReport()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        majorValue = value['major']
        instance.major = serder.INT.parse(majorValue)
        buildValue = value['build']
        instance.build = serder.INT.parse(buildValue)
        from netbluemind.system.api.UpgradeReportStatus import UpgradeReportStatus
        from netbluemind.system.api.UpgradeReportStatus import __UpgradeReportStatusSerDer__
        statusValue = value['status']
        instance.status = __UpgradeReportStatusSerDer__().parse(statusValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        majorValue = value.major
        instance["major"] = serder.INT.encode(majorValue)
        buildValue = value.build
        instance["build"] = serder.INT.encode(buildValue)
        from netbluemind.system.api.UpgradeReportStatus import UpgradeReportStatus
        from netbluemind.system.api.UpgradeReportStatus import __UpgradeReportStatusSerDer__
        statusValue = value.status
        instance["status"] = __UpgradeReportStatusSerDer__().encode(statusValue)
        return instance

