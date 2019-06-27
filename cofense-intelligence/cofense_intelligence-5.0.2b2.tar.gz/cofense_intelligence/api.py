from __future__ import unicode_literals, absolute_import
'''
 Copyright 2013-2019 Cofense, Inc.  All rights reserved.

 This software is provided by PhishMe, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
 including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
 disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
 consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
 this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.
'''

import logging
import sys
import time
import platform
import json
from datetime import datetime, timedelta

import requests

from . import metadata
from .intelligence import MalwareThreatReport, PhishThreatReport

try:
    from urllib import parse
except ImportError:
    import urlparse as parse


class IntelligenceAPI(object):
    """
    API Manager inteded to wrap Cofense Intelligence common API endpoint and methods. Requires authentication tokens
    """

    def __init__(self, auth, url='https://www.threathq.com/apiv1/', max_retries=3, proxy=None, proxy_auth=None, verify=False, integration=None):
        """

        :param auth: tuple containing Cofense Intelligence API tokens: (user_token, password_token)
        :param url: API url. Defaults to current version of Cofense API
        :param max_retries: Max number of attempts on failed connections. Default 3
        :param proxy: Url of any proxy server being used to connecto Cofense Intelligence API. Use SSL proxy if you use different URLs for plain and SSL
        :param proxy_auth: tuple containing proxy username and proxy password if authentication is required
        :param verify: SSL verification. Default False
        :param integration: Integration name for user agent string. Defaults to SDK
        """
        self.logger = logging.getLogger(__name__)
        self.version = metadata.__version__

        self.url = url
        self.auth = auth
        self.max_retries = max_retries
        self.proxy = (proxy, proxy_auth)
        self.verify = verify
        self.user_agent = integration

    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, proxy_config):
        proxy, proxy_auth = proxy_config

        if proxy:
            if 'http' in proxy:
                proxy = parse.urlparse(proxy).netloc

            if proxy_auth:
                auth = (proxy_auth[0], proxy_auth[1])
                proxy = '{}:{}@'.format(auth, proxy)

            self.logger.info('Setting proxy {}'.format(parse.urlparse(proxy).netloc))
            self._proxy = {'https': 'https://{}'.format(proxy)}
        else:
            self._proxy = None

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, integration):
        user_agent_base = 'Cofense Intel SDK'

        if not integration:
            integration = 'generic-integration'

        op_systems = {'Linux': 'Linux', 'Darwin': 'Mac OSX', 'Windows': 'Windows'}

        if platform.system() not in op_systems:
            os_release = platform.system()
        else:
            os_release = op_systems[platform.system()]

        py_version = '{0}.{1}.{2}'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)

        self._user_agent = "{0}/{1} ({2}; python {3}) {4}".format(user_agent_base, metadata.__version__, os_release, py_version, integration)

    def connect(self, verb, endpoint, data=None, headers=None, params=None, decode=True):
        """
        Primary connection method to directly interact with API endpoints

        :param verb: GET or POST
        :param endpoint: API endpoint intending to connect to
        :param data: HTTP data being submitted
        :param headers: HTTP headers
        :param params: Any params being passed
        :param decode:
        :return: tuple. (Request status code, Request content)
        """

        if not self.verify:
            requests.packages.urllib3.disable_warnings()

        if not headers:
            headers = {}

        headers['User-Agent'] = self.user_agent

        for t in range(self.max_retries):
            try:
                if verb.lower() == 'get':
                    response = requests.get(url=self.url + endpoint,
                                            auth=self.auth,
                                            headers=headers,
                                            proxies=self.proxy,
                                            verify=self.verify)

                elif verb.lower() == 'post':
                    response = requests.post(url=self.url + endpoint,
                                             auth=self.auth,
                                             headers=headers,
                                             proxies=self.proxy,
                                             verify=self.verify,
                                             data=data,
                                             params=params)
                else:
                    self.logger.error('Incorrect request method: {} [must be get or post]'.format(verb))
                    raise RuntimeError('Incorrect request method: {} [must be get or post]'.format(verb))

                if response.status_code == 404:
                    return response.status_code, "404 returned from a call to {} with data {}".format(endpoint, data)

                if response.status_code < 200 or response.status_code > 299:
                    msg = 'API call failed:\n'
                    msg += '\tStatus Code: {}\n'.format(response.status_code)
                    msg += '\tEndpoint: {}\n'.format(endpoint)
                    msg += '\tData: {}\n'.format(data)
                    msg += '\tHeaders: {}\n'.format(headers)
                    msg += '\tProxies: {}\n'.format(self.proxy)
                    msg += '\tVerify: {}\n'.format(self.verify)
                    msg += '\tContent: {}\n'.format(response.content)

                    self.logger.warning(msg)

                    continue

                if decode:
                    return response.status_code, response.content.decode('utf-8')
                else:
                    return response.status_code, response.content

            except requests.exceptions.RequestException as e:
                self.logger.error(e)
                time.sleep(60)

        else:
            self.logger.error('An error occurred. Tried to complete request ' + str(self.max_retries) + ' times and all failed.')
            sys.exit(1)

    def get_feed(self, feed_id=None):
        """
        Call the Cofense Intelligence /feed endpoint. Primarily used to verify access and permissions

        :param feed_id: optional. integer value for the feed ID
        :return: json with feed data
        """
        if feed_id:
            endpoint = 'feed/{}'.format(feed_id)
        else:
            endpoint = 'feed/'

        _, feeds = self.connect('get', endpoint)
        return feeds

    def get_screenshot(self, threat_id):
        _, screenshot = self.connect('get', 'screenshot/{}'.format(threat_id), decode=False)
        return screenshot

    def get_t3(self, threat_id, frmat, i_type):
        if frmat == 'pdf':
            decode = False
        else:
            decode = True

        _, report = self.connect('get', 't3/{0}/{1}/{2}'.format(i_type, threat_id, frmat), decode=decode)
        return report

    def get_t3_malware(self, threat_id, frmat):
        accepted_formats = ['cef', 'html', 'pdf', 'stix']

        if frmat not in accepted_formats:
            raise RuntimeError('Invalid T3 Malware format: {}'.format(frmat))

        return self.get_t3(threat_id, frmat, 'malware')

    def get_t3_phish(self, threat_id, frmat):
        accepted_formats = ['cef', 'stix']

        if frmat not in accepted_formats:
            raise RuntimeError('Invalid T3 Phish format {}'.format(frmat))

        return self.get_t3(threat_id, frmat, 'phish')

    def get_aggregate_t3(self, frmat, begin_time=None, end_time=None):
        accepted_formats = ['cef', 'pdf']

        if frmat not in accepted_formats:
            raise RuntimeError('Invalid aggregate report format: {}'.format(frmat))

        if frmat == 'pdf':
            decode = False
        else:
            decode = True

        if begin_time or end_time:
            params = {}
            if begin_time:
                params['beginTimestamp'] = begin_time
            if end_time:
                params['endTimestamp'] = end_time
        else:
            params = None

        _, reports = self.connect('post', 't3/{}'.format(frmat), params=params, decode=decode)
        return reports

    def submit_phish(self, url, feed_id=None):
        params = {'phishURL': url}

        if feed_id:
            params['feed'] = feed_id

        return self.connect('post', 'threat/phish', params=params)

    def get_threat(self, threat_type, threat_id):
        _, threats = self.connect('get', 'threat/{0}/{1}'.format(threat_type, threat_id))

        if threat_type == 'malware':
            cls = MalwareThreatReport
        elif threat_type == 'phish':
            cls = PhishThreatReport
        else:
            raise RuntimeError('Incorrect threat type {}'.format(threat_type))

        threat_json = json.loads(threats)

        if threat_json.get('success'):
            return cls(threat_json['data'])
        else:
            raise RuntimeError('Failed to return {0} threat: {1}'.format(threat_type, threat_id))

    def get_malware_threat(self, threat_id):
        return self.get_threat('malware', threat_id)

    def get_phish_threat(self, threat_id):
        return self.get_threat('phish', threat_id)

    def threat_search_page(self, params):
        _, response = self.connect('post', 'threat/search', params=params)
        response_json = json.loads(response)
        if response_json.get('success'):
            return response_json.get('data')
        else:
            # TODO: Include params in message
            raise RuntimeError('ThreatReport Search failed')

    def threat_search(self, rpp=100, **kwargs):
        params = {'resultsPerPage': rpp}
        params.update(kwargs)

        page = 0
        total_pages = 1
        while page < total_pages:
            params.update({'page': page})
            response_json = self.threat_search_page(params)
            page_info = response_json.get('page')
            threats = response_json.get('threats')

            for threat in threats:
                threat_type = threat['threatType'].lower()
                if threat_type == 'malware':
                    report_class = MalwareThreatReport
                elif threat_type == 'phish':
                    report_class = PhishThreatReport
                else:
                    raise RuntimeWarning('Unable to determine threat type: {}'.format(threat_type))

                yield report_class(threat)

            page += 1
            total_pages = page_info.get('totalPages')

    def threat_update_log(self, position=None, begin_time=None):
        if not position:
            if not begin_time:
                begin_time = int(datetime.timestamp(datetime.now() + timedelta(-30)))
            params = {'timestamp': begin_time}
        else:
            params = {'position': position}

        _, response = self.connect('post', 'threat/updates', params=params)

        response_json = json.loads(response)

        if response_json.get('success'):
            next_position = response_json.get('data').get('nextPosition')
            changelog = response_json.get('data').get('changelog')
            return next_position, changelog
        else:
            # TODO: put params/more info
            raise RuntimeError('ThreatReport Update Failed')

    def threat_updates(self, threat_type=None, position=None, begin_time=None):

        results = 1

        threat_reports = []

        while results > 0:
            position, updates = self.threat_update_log(position=position, begin_time=begin_time)
            for update in updates:
                if threat_type:
                    if update['threatType'] == threat_type:
                        threat_reports.append(update)
                else:
                    threat_reports.append(update)
            results = len(updates)

        return position, threat_reports
