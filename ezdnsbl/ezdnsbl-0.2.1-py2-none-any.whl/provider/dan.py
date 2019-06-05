#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import dns.resolver
from ezdnsbl.classes import DNSBLBase

__all__ = ['TORExit']

http_ref = 'https://www.dan.me.uk/'

types = {
    'E': 'Exit',
    'X': 'Hidden Exit',
    'A': 'Authority',
    'B': 'Bad Exit',
    'D': 'V2 Directory',
    'F': 'Fast',
    'G': 'Guard',
    'H': 'Hidden Service Directory',
    'N': 'Named',
    'R': 'Running',
    'S': 'Stable',
    'U': 'Unnamed',
    'V': 'Valid'
}


class TORExit(DNSBLBase):
    def __init__(self, ip, **kwargs):
        super(TORExit, self).__init__(**kwargs)
        self.http_ref = 'https://www.dan.me.uk/dnsbl'
        self.ip = ip
        self.resolver = dns.resolver.Resolver()
        reverse_ip = self.reverse_ip(self.ip)
        self.host = 'torexit.dan.me.uk'
        self.query_type = 'A'
        self.return_categories = []
        self.query = '{}.{}.'.format(reverse_ip, self.host)
        self.answer = self.do_query(self.query, self.query_type)
        if not self.answer:
            self.match = False
        else:
            self.match = True
            self.detailed_results = 'https://www.dan.me.uk/torcheck?ip={}'.format(self.ip)
            self.answer_octets = self.answer[0].to_text().split('.')
            self.error = None
            if self.answer_octets[0] != '127':
                self.error = self.answer_octets[0]
            if self.answer[0].to_text() == '127.0.0.100':
                self.return_categories.append('TOR Exit Node')
                self.match_categories.append('TOR Exit Node')
            else:
                self.return_categories.append('Other TOR Node')
                self.match_categories.append('TOR Exit Node')
            self.txt_answer = self.do_query(self.query, 'TXT')
            if not self.txt_answer:
                self.txt_match = False
            else:
                self.txt_match = True
                self.node_types = []
                self.txt_fields = re.match(r'"N:([^/]*)/P:([0-9,]*)/F:([A-Z]*)"', self.txt_answer[0].to_text())
                if not self.txt_fields:
                    self.error = 'Unknown TXT return: {}'.format(self.txt_answer[0].to_text())
                else:
                    self.node_name = str(self.txt_fields.group(1))
                    self.ports = str(self.txt_fields.group(2)).split(',')
                    self.flags = str(self.txt_fields.group(3))
                    for flag in self.flags:
                        self.node_types.append(types[flag])
                        self.match_categories.append(types[flag])

    def __str__(self):
        error_text = ''
        if self.match:
            if self.error:
                error_text = 'with an error [{}] '.format(self.error)
            if self.txt_match and self.node_types:
                txt_text = 'node types: {}'.format(', '.join(self.node_types))
            else:
                txt_text = 'no node types'
            match_text = 'Matched {}{} categorie(s): {}\n        Flagged with {}'.format(
                error_text,
                len(self.return_categories),
                ', '.join(self.return_categories),
                txt_text
            )
        else:
            match_text = 'Did not match'
        return 'IP {}\n    {}.'.format(self.ip, match_text)
