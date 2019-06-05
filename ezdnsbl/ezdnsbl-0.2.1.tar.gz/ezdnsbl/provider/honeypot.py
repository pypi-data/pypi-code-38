#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dns.resolver
from ezdnsbl.classes import DNSBLBase, DNSBLAuthException

__all__ = ['HTTPBL']

http_ref = 'http://www.projecthoneypot.org/'


class HTTPBL(DNSBLBase):
    def __init__(self, ip, **kwargs):
        super(HTTPBL, self).__init__(**kwargs)
        self.http_ref = 'http://www.projecthoneypot.org/httpbl_api.php'
        self.ip = ip
        try:
            self.apikey = self.auth_tokens['HTTPBL']
        except KeyError:
            raise DNSBLAuthException('Need API Key for `HTTPBL`')
        reverse_ip = self.reverse_ip(self.ip)
        self.host = 'dnsbl.httpbl.org'
        self.query_type = 'A'
        self.query = '{}.{}.{}.'.format(self.apikey, reverse_ip, self.host)
        self.resolver = dns.resolver.Resolver()
        self.answer = self.do_query(self.query, self.query_type)
        if not self.answer:
            self.match = False
        else:
            self.match = True
            self.answer_octets = self.answer[0].to_text().split('.')
            self.result = ''
            if self.answer_octets[0] != '127':
                self.result = 'Error'
            self.threat_score = int(self.answer_octets[2])
            self.threat_score_max = 255
            self.last_active = int(self.answer_octets[1])
            if int(self.answer_octets[3]) == 0:
                self.match_categories.append('Search Engine')
            if int(self.answer_octets[3]) & 1:
                self.match_categories.append('Suspicious')
            if int(self.answer_octets[3]) & 2:
                self.match_categories.append('Harvester')
            if int(self.answer_octets[3]) & 4:
                self.match_categories.append('Comment Spammer')

    def __str__(self):
        error_text = ''
        if self.match:
            if self.result == 'Error':
                error_text = 'with an error [{}] '.format(self.answer_octets[0])
            match_text = 'Matched {}{} categorie(s): {}\n        Threat score of {}/{}.\n        It was last seen {} ' \
                         'days ago'.format(
                                error_text,
                                len(self.match_categories),
                                ', '.join(self.match_categories),
                                self.threat_score,
                                self.threat_score_max,
                                self.last_active
                            )
        else:
            match_text = 'Did not match'
        return 'IP {}\n    {}.'.format(self.ip, match_text)

