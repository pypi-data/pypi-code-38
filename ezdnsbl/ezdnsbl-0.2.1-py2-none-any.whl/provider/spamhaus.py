#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dns.resolver
from ezdnsbl.classes import DNSBLBase

__all__ = ['Zen', 'DBL']

http_ref = 'https://www.spamhaus.org/'

return_codes = {
    '127.0.0.2': 'SBL - Spam',
    '127.0.0.3': 'SBL CSS - Snowshoe Spam',
    '127.0.0.4': 'XBL/CBL - Proxies, Trojans, Worms',
    '127.0.0.5': 'XBL/CBL - Proxies, Trojans, Worms',
    '127.0.0.6': 'XBL/CBL - Proxies, Trojans, Worms',
    '127.0.0.7': 'XBL/CBL - Proxies, Trojans, Worms',
    '127.0.0.9': 'SBL - DROP/EDROP',
    '127.0.0.10': 'PBL - ISP Policy Forbidden Mailer',
    '127.0.0.11': 'PBL - Spamhaus Policy Forbidden Mailer',
    '127.0.1.2': 'Spam',
    '127.0.1.4': 'Phishing',
    '127.0.1.5': 'Malware',
    '127.0.1.6': 'Botnet C&C',
    '127.0.1.102': 'Abused Legit Spam',
    '127.0.1.103': 'Abused Spammed Redirector',
    '127.0.1.104': 'Abused Legit Phish',
    '127.0.1.105': 'Abused Legit Malware',
    '127.0.1.106': 'Abused Legit Botnet C&C',
    '127.0.1.255': 'IP Queries Prohibited'
}


class Zen(DNSBLBase):
    def __init__(self, ip, **kwargs):
        super(Zen, self).__init__(**kwargs)
        self.http_ref = 'https://www.spamhaus.org/zen/'
        self.ip = ip
        self.data = self.ip
        self.resolver = dns.resolver.Resolver()
        self.supports = 'IP'
        reverse_ip = self.reverse_ip(self.ip)
        self.host = 'zen.spamhaus.org'
        self.query_type = 'A'
        self.query = '{}.{}.'.format(reverse_ip, self.host)
        self.answer = self.do_query(self.query, self.query_type)
        if not self.answer:
            self.match = False
        else:
            self.match = True
            for answer in self.answer:
                if answer.to_text() in return_codes:
                    self.match_categories.append(return_codes[answer.to_text()])
                else:
                    self.match_categories.append('Unknown')
            self.txt_answer = self.do_query(self.query, 'TXT')
            if not self.txt_answer:
                self.txt_match = False
            else:
                self.txt_match = True
                self.detailed_results = self.txt_answer[0].to_text().replace('"', '')
                if len(self.txt_answer) > 1:
                    self.category_info = self.txt_answer[1].to_text().replace('"', '')

    def __str__(self):
        if self.match:
            match_text = 'Matched {} categorie(s): {}'.format(
                len(self.match_categories),
                '; '.join(self.match_categories)
            )
        else:
            match_text = 'did not match'
        detailed_results_string = ''
        if self.detailed_results:
            detailed_results_string = ' Detailed Results: {}, More Info: {}'.format(
                self.detailed_results,
                self.category_info
            )
        return 'IP {}\n    {}.\n        {}'.format(self.ip, match_text, detailed_results_string)


class DBL(DNSBLBase):
    def __init__(self, domain, **kwargs):
        super(DBL, self).__init__(**kwargs)
        self.http_ref = 'https://www.spamhaus.org/dbl/'
        self.domain = domain
        self.resolver = dns.resolver.Resolver()
        self.host = 'dbl.spamhaus.org'
        self.query_type = 'A'
        self.query = '{}.{}.'.format(self.domain, self.host)
        self.answer = self.do_query(self.query, self.query_type)
        if not self.answer:
            self.match = False
        else:
            self.match = True
            for answer in self.answer:
                if return_codes.has_key(answer.to_text()):
                    self.match_categories.append(return_codes[answer.to_text()])
                else:
                    self.match_categories.append('Unknown')
            self.txt_answer = self.do_query(self.query, 'TXT')
            if not self.txt_answer:
                self.txt_match = False
            else:
                self.txt_match = True
                self.detailed_results = self.txt_answer[0].to_text().replace('"', '')

    def __str__(self):
        if self.match:
            match_text = 'Matched {} categorie(s): {}'.format(
                len(self.match_categories),
                '; '.join(self.match_categories)
            )
        else:
            match_text = 'Did not match'
        detailed_results_string = ''
        if self.detailed_results:
            detailed_results_string = '\n        Detailed Results: {}'.format(self.detailed_results)
        return 'Domain {}\n    {}.{}'.format(self.domain, match_text, detailed_results_string)

