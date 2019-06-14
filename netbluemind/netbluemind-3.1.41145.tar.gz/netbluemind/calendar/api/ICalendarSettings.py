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
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

ICalendarSettings_VERSION = "3.1.41145"

class ICalendarSettings(BaseEndpoint):
    def __init__(self, apiKey, url ,calendarUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/calendars/{calendarUid}/_config'
        self.calendarUid_ = calendarUid
        self.base = self.base.replace('{calendarUid}',calendarUid)

    def set (self, settings ):
        postUri = "";
        __data__ = None
        from netbluemind.calendar.api.CalendarSettingsData import CalendarSettingsData
        from netbluemind.calendar.api.CalendarSettingsData import __CalendarSettingsDataSerDer__
        __data__ = __CalendarSettingsDataSerDer__().encode(settings)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendarSettings_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def get (self):
        postUri = "";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendarSettings_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.CalendarSettingsData import CalendarSettingsData
        from netbluemind.calendar.api.CalendarSettingsData import __CalendarSettingsDataSerDer__
        return self.handleResult__(__CalendarSettingsDataSerDer__(), response)
