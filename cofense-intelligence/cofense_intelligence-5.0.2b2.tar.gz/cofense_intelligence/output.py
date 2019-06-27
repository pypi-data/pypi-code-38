from __future__ import unicode_literals, absolute_import
'''
 Copyright 2013-2019 Cofense, Inc.  All rights reserved.

 This software is provided by PhishMe, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
 including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
 disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
 consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
 this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.
'''

from datetime import datetime
import sys
import os
import json
import re
import csv
import logging
import defusedxml.ElementTree as etree


class CofenseIntegration(object):
    """
    Base Class of all PhishMe Integration classes
    """

    def __init__(self, config, **kwargs):

        self.config = config

        self.config.update(kwargs)

        self.logger = logging.getLogger('{}'.format(config['INTEGRATION']))

        self.logger.debug('Integration logging setup')
        if 'ARGS' in config:
            self.args = config['ARGS']

    def process(self, mrti):
        """
        Method stub for process; this will be overridden by child integration classes

        :param str mrti: PhishMe Intelligence ThreatReport ID data
        :param int threat_id: PhishMe Intelligence threat id
        :return: None
        """

        pass

    def post_run(self):
        """
        Method stub for post_run; this will be overridden by child integration classes as needed

        :param str config_file_location: Path to configuration file
        :return: None
        """

        pass

    def sync(self):
        pass


class FileOutput(CofenseIntegration):
    """
    Parent class for "generic" PhishMe Intelligence integrations; extends :class:`phishme_intelligence.output.base_integration.CofenseIntegration`
    """

    def __init__(self, config, **kwargs):
        super(FileOutput, self).__init__(config, **kwargs)

        if not self.config.get('BASE_DIR'):
            self.config['BASE_DIR'] = os.path.abspath(os.path.dirname(__file__))

    def prep(self):
        pass

    def process(self, mrti):

        output_file = self.get_file_path(mrti)

        self.write_file(mrti, output_file)

    def verify_dirs(self, year_month_day):

        output_path = os.path.join(self.config['BASE_DIR'], 'output/' + year_month_day)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        return output_path

    def verify_append_dirs(self):
        output_path = os.path.join(self.config['BASE_DIR'], 'output')

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        return output_path

    def get_file_path(self, mrti):
        pass

    def write_file(self, mrti, output_file):
        pass


class JsonFileOutput(FileOutput):

    def get_file_path(self, mrti):
        year_month_date = datetime.fromtimestamp(mrti.first_published / 1e3).strftime('%Y-%m-%d')

        output_path = self.verify_dirs(year_month_date)

        output_file = os.path.join(output_path, str(mrti.threat_id) + '.json')

        return output_file

    def write_file(self, mrti, output_file):
        with open(output_file, 'w') as outfile:
            outfile.write(json.dumps(mrti.json))


class CefFileOutput(FileOutput):

    def get_file_path(self, mrti):
        first_published = re.search('deviceCustomDate1=(\d+)', mrti).group(1)
        year_month_day = datetime.fromtimestamp(int(first_published) / 1e3).strftime('%Y-%m-%d')

        output_path = self.verify_append_dirs()
        output_file = os.path.join(output_path, year_month_day + '.cef')

        return output_file

    def write_file(self, mrti, output_file):
        with open(output_file, 'ab') as outfile:
            outfile.write(mrti.encode('utf-8') + b'\n')


class StixFileOutput(FileOutput):

    def get_file_path(self, mrti):
        threat_id = re.search('<campaign:Title>(\d+)</campaign:Title>', mrti).group(1)
        year_month_day = re.search('<indicator:Start_Time precision=\"second\">(\d{4}-\d{2}-\d{2})T', mrti).group(1)

        output_path = self.verify_dirs(year_month_day)
        output_file = os.path.join(output_path, threat_id + '.stix')

        return output_file

    def write_file(self, mrti, output_file):
        threat_id = re.search('<campaign:Title>(\d+)</campaign:Title>', mrti).group(1)

        try:
            stix_xml = etree.fromstring(mrti.encode('utf-8'))
        except etree.XMLSyntaxError:
            raise RuntimeError('XML parsing error of STIX package for threat report: ' + threat_id)

        with open(output_file, 'wb') as outfile:
            outfile.write(mrti.encode('utf-8'))


class CsvFileOutput(FileOutput):

    def get_file_path(self, mrti):
        year_month_date = datetime.fromtimestamp(mrti.first_published / 1e3).strftime('%Y-%m-%d')

        output_path = self.verify_dirs(year_month_date)

        return output_path

    @staticmethod
    def get_summary(mrti):
        return {'id': mrti.threat_id,
                'first_published': mrti.first_published,
                'last_published': mrti.last_published,
                'report_url': mrti.human_readable_url}

    @staticmethod
    def need_headers(output_file):
        if os.path.isfile(output_file):
            return False
        else:
            return True

    def write_csv(self, output_file, data):
        need_headers = self.need_headers(output_file)

        write_mods = {2: 'ab', 3: 'a'}
        py_version = sys.version_info[0]

        with open(output_file, write_mods[py_version]) as outfile:
            csv_writer = csv.DictWriter(outfile, data.keys())

            if need_headers:
                csv_writer.writeheader()
            try:
                csv_writer.writerow(data)
            except UnicodeEncodeError:
                encoded_data = {}
                for key, value in data.items():
                    if isinstance(value, unicode):
                        encoded_data[key] = value.encode('utf-8')
                    else:
                        encoded_data[key] = value
                csv_writer.writerow(encoded_data)

    def write_malware_summary(self, mrti, output_dir):

        report_summary = self.get_summary(mrti)
        malware_summary = {'malware_families': mrti.malware_families, 'label': mrti.label}
        report_summary.update(malware_summary)

        output_file = os.path.join(output_dir, "malware_threat_reports.csv")

        self.write_csv(output_file, report_summary)

    def write_block_set(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "block_set.csv")

        for item in mrti.block_set:
            ip_details = {'latitude': '',
                          'longitude': '',
                          'time_zone': '',
                          'continent': '',
                          'cont_code': '',
                          'country': '',
                          'country_code': '',
                          'asn': '',
                          'asn_org': '',
                          'isp': '',
                          'organizatoin': ''}

            url_details = {'host': '', 'path': ''}

            if item.block_type == 'URL':
                url_details = {'host': item.watchlist_ioc_host, 'path': item.watchlist_ioc_path}

            if item.block_type == 'IPv4 Address':
                ip_detailed = item.json.get('ipDetail')
                if ip_detailed:
                    ip_details = {'latitude': ip_detailed.get('latitude'),
                                  'longitude': ip_detailed.get('longitude'),
                                  'time_zone': ip_detailed.get('timeZone'),
                                  'continent': ip_detailed.get('continentName'),
                                  'cont_code': ip_detailed.get('continentCode'),
                                  'country': ip_detailed.get('countryName'),
                                  'country_code': ip_detailed.get('countryIsoCode'),
                                  'asn': ip_detailed.get('asn'),
                                  'asn_org': ip_detailed.get('asnOrganization'),
                                  'isp': ip_detailed.get('isp'),
                                  'organization': ip_detailed.get('organization')}

            block_set = {'id': mrti.threat_id,
                         'indicator': item.watchlist_ioc,
                         'impact': item.impact,
                         'type': item.block_type,
                         'role': item.role,
                         'role_desc': item.role_description,
                         'malware_family': item.malware_family}

            block_set.update(url_details)
            block_set.update(ip_details)

            self.write_csv(output_file, block_set)

    def write_exec_set(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "executable_set.csv")

        for item in mrti.executable_set:
            exec_set = {'id': mrti.threat_id,
                        'file_name': item.file_name,
                        'type': item.type,
                        'md5': item.md5,
                        'sha1': item.sha1,
                        'sha224': item.sha224,
                        'sha256': item.sha256,
                        'sha384': item.sha384,
                        'sha512': item.sha512,
                        'ssdeep': item.ssdeep,
                        'malware_family': item.malware_family,
                        'subtype': item.subtype}

            self.write_csv(output_file, exec_set)

    def write_subjects(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "subjects.csv")

        for subject in mrti.subject_set:
            subject_data = {'id': mrti.threat_id,
                            'subject': subject.subject,
                            'count': subject.total_count}

            self.write_csv(output_file, subject_data)

    def write_sender_ips(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "sender_ips.csv")

        for ip in mrti.sender_ip_set:
            ip_data = {'id': mrti.threat_id,
                       'ip': ip.ip,
                       'count': ip.total_count}

            self.write_csv(output_file, ip_data)

    def write_sender_emails(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "sender_emails.csv")

        for email in mrti.sender_email_set:
            email_data = {'id': mrti.threat_id,
                          'email': email.sender_email,
                          'count': email.total_count}

            self.write_csv(output_file, email_data)

    def write_spam_urls(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "spam_urls.csv")

        for url in mrti.spam_url_set:
            spam_url = {'id': mrti.threat_id,
                        'url': url.url,
                        'count': url.total_count}

            self.write_csv(output_file, spam_url)

    def write_malware(self, mrti, output_dir):
        self.write_malware_summary(mrti, output_dir)
        self.write_block_set(mrti, output_dir)
        self.write_exec_set(mrti, output_dir)
        self.write_subjects(mrti, output_dir)
        self.write_sender_ips(mrti, output_dir)
        self.write_sender_emails(mrti, output_dir)
        self.write_spam_urls(mrti, output_dir)

    def write_phish_summary(self, mrti, output_dir):
        # TODO: Include phish URLs and IPs

        report_summary = self.get_summary(mrti)
        phish_summary = {'confirmed_date': mrti.confirmed_date,
                         'title': mrti.title,
                         'language': mrti.language}

        report_summary.update(phish_summary)

        output_file = os.path.join(output_dir, 'phish_threat_reports.csv')
        self.write_csv(output_file, report_summary)

    def write_phish_kits(self, mrti, output_dir):
        output_file = os.path.join(output_dir, 'phish_kits.csv')

        for kit in mrti.kits:
            phish_kit = {'id': mrti.threat_id,
                         'name': kit.kit_name,
                         'size': kit.size,
                         'md5': kit.md5,
                         'sha1': kit.sha1,
                         'sha224': kit.sha224,
                         'sha256': kit.sha256,
                         'sha384': kit.sha384,
                         'sha512': kit.sha512,
                         'ssdeep': kit.ssdeep}

            self.write_csv(output_file, phish_kit)

    def write_reported_urls(self, mrti, output_dir):
        output_file = os.path.join(output_dir, 'phish_reported_urls.csv')

        for url in mrti.reported_url_list:
            reported_url = {'id': mrti.threat_id,
                            'url': url.url,
                            'domain': url.domain,
                            'host': url.host,
                            'path': url.path,
                            'protocol': url.protocol,
                            'query': url.query}

            self.write_csv(output_file, reported_url)

    def write_action_urls(self, mrti, output_dir):
        output_file = os.path.join(output_dir, 'phish_action_urls.csv')

        for url in mrti.action_url_list:
            action_url = {'id': mrti.threat_id,
                          'url': url.url,
                          'domain': url.domain,
                          'host': url.host,
                          'path': url.path,
                          'protocol': url.protocol,
                          'query': url.query}

            self.write_csv(output_file, action_url)

    def write_phish(self, mrti, output_dir):

        self.write_phish_summary(mrti, output_dir)
        self.write_phish_kits(mrti, output_dir)
        self.write_reported_urls(mrti, output_dir)
        self.write_action_urls(mrti, output_dir)

    def write_file(self, mrti, output_dir):

        if mrti.threat_type == 'MALWARE':
            self.write_malware(mrti, output_dir)
        elif mrti.threat_type == 'PHISH':
            self.write_phish(mrti, output_dir)


class TextFileOutput(FileOutput):
    def get_file_path(self, mrti):
        self.logger.debug('Calling get_file_path')
        return self.verify_append_dirs()

    def write_file(self, mrti, output_dir):
        self.logger.debug('Calling write_file')
        if mrti.threat_type == 'MALWARE' and (self.args.intel_type == 'malware' or self.args.intel_type == 'all'):
            self._write_malware(mrti, output_dir)
        elif mrti.threat_type == 'PHISH' and (self.args.intel_type == 'phish' or self.args.intel_type == 'all'):
            self._write_phish(mrti, output_dir)

    def _write(self, data, file_name):
        self.logger.debug('Calling _write')
        write_mods = {2: 'ab', 3: 'a'}
        py_version = sys.version_info[0]

        if isinstance(data, list):
            output = "\n".join(data)
        elif isinstance(data, str):
            output = data
        else:
            raise TypeError("data coming into _write must be a string or a list")

        with open(file_name, write_mods[py_version]) as outfile:
            try:
                if not output.endswith("\n"):
                    output += "\n"
                outfile.write(output.lstrip())

            except Exception as e:
                self.logger.error(e)
                raise e

    def _get_list(self, mrti, block_type, impact):
        self.logger.debug('Calling _get_list')
        return [item.watchlist_ioc for item in mrti.block_set if item.block_type == block_type and item.impact == impact]

    def _write_malware(self, mrti, output_dir):
        self.logger.debug('Calling _write_malware')
        # URLs
        if self.args.txt_url_major:
            major_urls = self._get_list(mrti, 'URL', 'Major')
            self._write(major_urls, os.path.join(output_dir, self.args.txt_url_major_file))

        if self.args.txt_url_moderate:
            moderate_urls = self._get_list(mrti, 'URL', 'Moderate')
            self._write(moderate_urls, os.path.join(output_dir, self.args.txt_url_moderate_file))

        if self.args.txt_url_minor:
            minor_urls = self._get_list(mrti, 'URL', 'Minor')
            self._write(minor_urls, os.path.join(output_dir, self.args.txt_url_minor_file))

        # IP Addresses
        if self.args.txt_ip_major:
            major_ips = self._get_list(mrti, 'IPv4 Address', 'Major')
            self._write(major_ips, os.path.join(output_dir, self.args.txt_ip_major_file))

        if self.args.txt_ip_moderate:
            moderate_ips = self._get_list(mrti, 'IPv4 Address', 'Moderate')
            self._write(moderate_ips, os.path.join(output_dir, self.args.txt_ip_moderate_file))

        if self.args.txt_ip_minor:
            minor_ips = self._get_list(mrti, 'IPv4 Address', 'Minor')
            self._write(minor_ips, os.path.join(output_dir, self.args.txt_ip_minor_file))

        # Domain names
        if self.args.txt_domain_major:
            major_domain = self._get_list(mrti, 'Domain Name', 'Major')
            self._write(major_domain, os.path.join(output_dir, self.args.txt_domain_major_file))

        if self.args.txt_domain_moderate:
            moderate_domain = self._get_list(mrti, 'Domain Name', 'Moderate')
            self._write(moderate_domain, os.path.join(output_dir, self.args.txt_domain_moderate_file))

        if self.args.txt_domain_minor:
            minor_domain = self._get_list(mrti, 'Domain Name', 'Minor')
            self._write(minor_domain, os.path.join(output_dir, self.args.txt_domain_minor_file))

        # Files
        if self.args.txt_malicious_md5:
            files = [item.md5 for item in mrti.executable_set]
            self._write(files, os.path.join(output_dir, self.args.txt_malicious_md5_file))

    def _write_phish(self, mrti, output_dir):
        self.logger.debug('Calling _write_phish')

        for url in mrti.action_url_list:
            self._write_phish_action_url(url.url, output_dir)
        for url in mrti.reported_url_list:
            self._write_phish_reported_url(url.url, output_dir)

    def _write_phish_action_url(self, action_url, output_dir):
        self.logger.debug('Calling _write_phish_action_url')
        self._write(action_url, os.path.join(output_dir, "phish_action_url.txt"))

    def _write_phish_reported_url(self, reported_url, output_dir):
        self.logger.debug('Calling _write_phish_reported_url')
        self._write(reported_url, os.path.join(output_dir, "phish_reported_url.txt"))
