#!/usr/bin/env python

#
# LICENSE:
# This program is free software; you can redistribute it and/or modify it 
# under the terms of the GNU Affero General Public License version 3 (AGPL) 
# as published by the Free Software Foundation.
# (c) 2010-2014 caregraf
#

import urllib, urllib2

class CacheObjectInterface:
    """
    Utility for talking to FMQL through a Cache Object Interface. Key feature is managing sessions. Cache uses cookies for session identification. Cache limits the number of sessions on a server so it is important to use and reuse the same session.
    
    If Cache runs out of sessions, it will issue Service Unavailable 503 errors.
    
    Follows FMQLInterface
    """
    def __init__(self, ep):
        # ex/ http://...../FMQL.csp
        self.ep = ep
        self.cookie = ""
        
    def invokeRPC(self, name, params):
        # to match broker if for now
        return self.invokeQuery(params[0]).read()
        
    def invokeQuery(self, query):
        queryDict = {"query": query}
        queryurl = self.ep + "?" + urllib.urlencode(queryDict)
        request = urllib2.Request(queryurl)
        if self.cookie:
            request.add_header('cookie', self.cookie)
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            # 503 "Service Unavailable": The server cannot process the request due to a high load
            raise
        # Always reset the cookie - may be a new one if session idle for > 15 minutes.
        # SET-COOKIE: CSPSESSIONID-SP-57772-UP-csp-fmquery-=0010000100002g3gWldo9l0000fAj6SQgextDm2AmskX7GxQ--; path=/csp/fmquery/;  httpOnly;
        self.cookie = response.info().getheader('Set-Cookie')
        return response      
        
