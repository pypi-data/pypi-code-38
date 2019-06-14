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

IPrint_VERSION = "3.1.41145"

class IPrint(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/calendars/print'

    def print_ (self, options ):
        postUri = "";
        __data__ = None
        from netbluemind.calendar.api.PrintOptions import PrintOptions
        from netbluemind.calendar.api.PrintOptions import __PrintOptionsSerDer__
        __data__ = __PrintOptionsSerDer__().encode(options)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IPrint_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.PrintData import PrintData
        from netbluemind.calendar.api.PrintData import __PrintDataSerDer__
        return self.handleResult__(__PrintDataSerDer__(), response)
