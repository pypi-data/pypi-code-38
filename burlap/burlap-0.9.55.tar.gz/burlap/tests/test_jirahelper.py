from __future__ import print_function

from burlap.tests.base import TestCase
from burlap.jirahelper import jirahelper

class JiraHelperTests(TestCase):

    def test_jirahelper(self):
        test_log = """
38fc750991db7df363322e77e4ce56d81d0f7eee Fixed migration conflict
5bf53f847bd29eb796f15715a1cbe8a8437d6847 TICKET-3378 - Batch Edit Disassociation
6c9feb0b550c4b96150b4524d6fbd1ded294bb0f Merged in TICKET-3346 (pull request #932)
d7715a04ee829ac16f61a406bbd0d84e3b80eef2 Merged in TICKET-3469 (pull request #933)
b0dd4fe1ab041472f0d83a421dc8be7c9e9bc604 Fixed django settings.
3f34da3173cc4f07ba14ae5786a5f88023592dd7 Regenerate field migration to fix migration conflict
88867aa2209869106dcb35dc7b1db62dee0f543f Fix EmptyResultSet error raised by empty queries in Django admin
5b5a63b69004fbe11ffda310faee5ff069267c50 Merged in TICKET-3481 (pull request #931)
46ef7818aed657b9bc99c181e6c73a7c6a47a487 TICKET-3481 fixed error creating model
1d4c2dbeab0e04d18f75e11f26ddf41aa3a3f00b Merged in TICKET-3473 (pull request #914)
        """
        jirahelper.env.ticket_pattern = 'TICKET-[0-9]+'
        tickets = sorted(jirahelper.get_tickets_from_str(test_log))
        print('tickets:', tickets)
        assert tickets == ['TICKET-3346', 'TICKET-3378', 'TICKET-3469', 'TICKET-3473', 'TICKET-3481']
