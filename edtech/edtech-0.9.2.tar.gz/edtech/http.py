'''
This file is part of the EdTech library project at Full Sail University.

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

    Copyright (C) 2014, 2015 Full Sail University.
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Taken from https://gist.github.com/rduplain/1265409 with permission (by Ron DuPlain).
@author: Jeremiah Blanchard
@since: 08/20/2014
@summary: HTTP lib
'''

import cookielib
import urllib
import urllib2
  
class Client(object):
    def __init__(self, cookieFile = None):
        if cookieFile != None:
            self.cookie_jar = cookielib.MozillaCookieJar()
            self.cookie_jar.load(cookieFile)
            for cookie in self.cookie_jar:
                print(cookie)
        else:
            self.cookie_jar = cookielib.CookieJar()
        
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        urllib2.install_opener(self.opener)
 
    def addCookie(self, cookie):
        self.cookie_jar.set_cookie(cookie)        
    
    def get(self, url, headers={}):
        request = urllib2.Request(url, headers=headers)
        return self.execute_request(request)
    
    def post(self, url, data=None, headers={}):
        if data is None:
            postdata = None
        else:
            postdata = urllib.urlencode(data)
        request = urllib2.Request(url, postdata, headers)
        return self.execute_request(request)
    
    def execute_request(self, request):
        response = self.opener.open(request)
        response.status_code = response.getcode()
        response.data = response.read()
        return response
