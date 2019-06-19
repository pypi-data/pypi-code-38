#!/usr/bin/python
"""
Created on Mon Jun 13 13:18:08 2016

@author: me
"""

import requests
import time

#input a list of smiles and query envipath for possible suspect transformation products. Output suspects.csv is formatted for input into Envipy and function also returns a list of suspects.
def import_json_package(jsonfile='/home/pps/benchmark/envirest/package.json', host='localhost:8080'):

    headers={"Accept":"application/json"}
    url="http://{0}/package".format(host)

    data={"hiddenMethod":"importFromJson"}
    files={"file":(jsonfile, open(jsonfile,'rb'))}
    r=requests.post(url, data=data, files=files, headers=headers, allow_redirects=True, verify=False)

    return r.json()

if __name__ == '__main__':
    from sys import argv
    print(import_json_package(*argv[1:]))

