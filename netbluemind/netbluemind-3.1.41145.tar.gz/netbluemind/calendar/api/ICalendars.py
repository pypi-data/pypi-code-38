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

ICalendars_VERSION = "3.1.41145"

class ICalendars(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/calendars'

    def search (self, query ):
        postUri = "/_search";
        __data__ = None
        from netbluemind.calendar.api.CalendarsVEventQuery import CalendarsVEventQuery
        from netbluemind.calendar.api.CalendarsVEventQuery import __CalendarsVEventQuerySerDer__
        __data__ = __CalendarsVEventQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendars_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        from netbluemind.core.container.model.ItemContainerValue import ItemContainerValue
        from netbluemind.core.container.model.ItemContainerValue import __ItemContainerValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemContainerValueSerDer__(__VEventSeriesSerDer__())), response)
    def getReminder (self, dtalarm ):
        postUri = "/_reminder";
        __data__ = None
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        __data__ = __BmDateTimeSerDer__().encode(dtalarm)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendars_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.Reminder import Reminder
        from netbluemind.calendar.api.Reminder import __ReminderSerDer__
        return self.handleResult__(serder.ListSerDer(__ReminderSerDer__()), response)
