#!/usr/bin/env python

#
# LICENSE:
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License version 3 (AGPL)
# as published by the Free Software Foundation.
# (c) 2015-2016 caregraf
#

import urllib
import urllib2
import ssl
import json
import re
from StringIO import StringIO
from collections import OrderedDict
import logging

from brokerRPC import VistARPCConnection, RPCLogger

"""
FMQL Endpoint Indirection - broker or REST and REST can be CSP (which has quirky errors)

TODO: merge in CacheInterface (may distinguish 3 - CSP/REST/BrokerIF
"""
                                
class FMQLRESTIF:
    """
    Indirection between endpoint for query so can go to CSPs etc.
        
    TODO: catch 503 etc in here and return clean ERROR codes
    """
    def __init__(self, fmqlEP, epWord="query"):
        self.fmqlEP = fmqlEP
        self.epWord = epWord
        
    def __str__(self):
        return "ENDPOINT: " + self.fmqlEP
        
    def invokeQuery(self, query):
        queryURL = self.fmqlEP + "?" + urllib.urlencode({self.epWord: query}) 
        try:
            if re.match("https", queryURL):
                # ignore bad cert - happens on test systems.
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                sreply = StringIO(urllib2.urlopen(queryURL, context=ctx).read())
            else:
                sreply = StringIO(urllib2.urlopen(queryURL).read()) # be compatible with cacheObjectInterface
            # Want to preserve order of keys (as FMQL does) 
            jreply = json.load(sreply, object_pairs_hook=OrderedDict) 
            return jreply
        except:
            try:
                sreply.seek(0)
            except:
                logging.error("Problem Response for query {} - can't even examine".format(query))
                raise
            text = sreply.read()
            if re.search(r'FMQL\.CSP', self.fmqlEP): # CSP endpoint
                #
                # Error: <b>Cannot allocate a license</b><br>
                # ErrorNo: <b>5915</b><br>
                # CSP Page: <b>/csp/fmquery/FMQL.CSP</b><br>
                # Namespace: <b>CHCS</b><br>
                #
                if re.search(r'ErrorNo', text):
                    error = re.search(r'Error: \<b\>([^\<]+)', text).group(1)
                    errorNo = re.search(r'ErrorNo: \<b\>([^\<]+)', text).group(1)
                    logging.error("CSP Error Response for query {} - {} - {}".format(query, errorNo, error))
            last500 = text[-500:]
            if len(text) > 500:
                last500 = "[LAST 500] {}".format(last500)
            logging.error("Problem Response for query {} - {}".format(query, last500))
            raise
            
class FMQLBrokerIF:

    def __init__(self, hostname, port, access, verify, osehraVISTA=False):
        conn = VistARPCConnection(hostname, int(port), access, verify, "CG FMQL QP USER", RPCLogger(), useOSEHRACipher=osehraVISTA)
        conn.connect()
        self.__connection = conn
        self.__epDescr = hostname + ":" + str(port)
        
    def __str__(self):
        return "BROKER ENDPOINT: " + self.__epDescr
        
    def invokeQuery(self, query):
    
        reply = self.__connection.invokeRPC("CG FMQL QP", [query])

        try: 
            # preserve order as FMQL does
            jreply = json.loads(reply, object_pairs_hook=OrderedDict)
        except:
            logging.error("Can't make JSON for response to query {} - {}".format(query, reply))
            raise
        
        return jreply
