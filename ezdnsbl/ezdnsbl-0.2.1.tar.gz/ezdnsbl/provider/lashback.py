#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dns.resolver
from ezdnsbl.classes import DNSBLBase

__all__ = ['UBL']

http_ref = 'http://www.lashback.com/'

return_codes = {
    '127.0.0.2': 'Email spam from unsubscribe links',
}


class UBL(DNSBLBase):
    def __init__(self, ip, **kwargs):
        super(UBL, self).__init__(**kwargs)
        self.http_ref = 'http://blacklist.lashback.com/'
        self.ip = ip
        self.resolver = dns.resolver.Resolver()
        reverse_ip = self.reverse_ip(self.ip)
        self.host = 'ubl.unsubscore.com'
        self.query_type = 'A'
        self.query = '{}.{}.'.format(reverse_ip, self.host)
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
                if len(self.txt_answer) > 1:
                    self.category_info = self.txt_answer[1].to_text().replace('"', '')

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
            detailed_results_string = '\n        Detailed Results: {}\n        More Info: {}'.format(
                self.detailed_results,
                self.category_info
            )
        return 'IP {}\n    {}.{}'.format(self.ip, match_text, detailed_results_string)
