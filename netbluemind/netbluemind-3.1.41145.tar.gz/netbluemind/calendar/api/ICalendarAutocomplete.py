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

ICalendarAutocomplete_VERSION = "3.1.41145"

class ICalendarAutocomplete(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/calendar/autocomplete'

    def calendarLookup (self, pattern , verb ):
        postUri = "/_calendarLookup/{pattern}";
        __data__ = None
        postUri = postUri.replace("{pattern}",pattern);
        from netbluemind.core.container.model.acl.Verb import Verb
        from netbluemind.core.container.model.acl.Verb import __VerbSerDer__
        __data__ = __VerbSerDer__().encode(verb)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendarAutocomplete_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.CalendarLookupResponse import CalendarLookupResponse
        from netbluemind.calendar.api.CalendarLookupResponse import __CalendarLookupResponseSerDer__
        return self.handleResult__(serder.ListSerDer(__CalendarLookupResponseSerDer__()), response)
    def calendarGroupLookup (self, groupUid ):
        postUri = "/_calendarsGroupLookup/{groupUid}";
        __data__ = None
        postUri = postUri.replace("{groupUid}",groupUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendarAutocomplete_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.CalendarLookupResponse import CalendarLookupResponse
        from netbluemind.calendar.api.CalendarLookupResponse import __CalendarLookupResponseSerDer__
        return self.handleResult__(serder.ListSerDer(__CalendarLookupResponseSerDer__()), response)
