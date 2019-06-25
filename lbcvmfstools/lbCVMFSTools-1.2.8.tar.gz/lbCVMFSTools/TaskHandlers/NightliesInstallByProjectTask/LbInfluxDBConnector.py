###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''

Module that allows to load all the checker Plugins

:author: Stefan-Gabriel CHITIC
'''

from influxdb import InfluxDBClient
import os
import urllib3


class InFluxDbConnector():

    def __init__(self, database='cvmfs-nightlies',
                 hostname='dbod-lbcvmfsd.cern.ch',
                 port=8088, username='', password=''):
        urllib3.disable_warnings()
        if username == '' and password == '':
            fname = os.path.join(os.environ["HOME"], "private", "influx.txt")
            if os.path.exists(fname):
                with open(fname, "r") as f:
                    data = f.readlines()
                    if len(data) > 0:
                        res = data[0].strip()
                        (username, password) = res.split("/")
        self.client = InfluxDBClient(hostname, port, username, password,
                                     database, ssl=True, verify_ssl=False)
        self.client.create_database(database)

    def getConnector(self):
        return self.client


instance = None


def getConnector(connector=InFluxDbConnector):
    global instance
    if instance is None:
        instance = connector()
    return instance.getConnector()

