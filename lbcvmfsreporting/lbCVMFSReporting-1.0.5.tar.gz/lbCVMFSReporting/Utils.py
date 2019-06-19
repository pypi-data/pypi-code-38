import os
import re
import urllib2
import json
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


class Utils:

    @staticmethod
    def cmpList(x):
        if x[4] == '':
            return '9999-99-99 99:99:99'
        return x[4]

    @staticmethod
    def getSlots():
        """ Util function to get slots of interest from conf file """
        url = "https://lhcb-nightlies.cern.ch/ajax/cvmfsReport/priorites/"
        response = urlopen(url)
        raw_data = json.loads(response.read().decode('utf-8'))
        slots = []
        if raw_data:
            for l in raw_data['data'].split('\n'):
                if re.match("^\s*#", l):
                    continue
                else:
                    slots.append(l.rstrip())
        return slots

    @staticmethod
    def getSlotsProjects(date):
        shouldInstall = {}
        url = "https://lhcb-couchdb.cern.ch/nightlies-nightly/_design/" \
              "deployment/_view/ready?key=[\"%s\",\"cvmfs\"]" \
              "&include_docs=true" % date
        response = urllib2.urlopen(url)
        slots = json.loads(response.read())
        for slot in slots['rows']:
            completed = []
            for platform_name in slot['doc']['builds'].keys():
                platform = slot['doc']['builds'][platform_name]
                for project_name in platform.keys():
                    if project_name == 'info':
                        continue
                    p = platform[project_name]
                    completed.append({
                        'project': project_name,
                        'is_build': p.get('completed', None) is not None})
            shouldInstall[slot['doc']['slot']] = {
                'platforms': [str(p['platform']) for p in slot['value']],
                'projects': [str(p['name'])
                             for p in slot['doc']['config']['projects']
                             if not p['disabled']],
                'completed': completed
            }
        return shouldInstall


