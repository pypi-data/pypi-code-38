#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .spamhaus import Zen, DBL
from .dan import TORExit
from .honeypot import HTTPBL
from .surriel import PSBL
from .gbudb import Truncate
from .lashback import UBL
from .apews import RHSBL, LHSBL
from .cymru import MHR, IPtoASN, IPtoASNPeers, ASNInfo

supports = {
    'ipv4': [
        Zen,
        TORExit,
        HTTPBL,
        PSBL,
        Truncate,
        UBL,
        LHSBL,
        IPtoASN,
        IPtoASNPeers
    ],
    'ipv6': [
        TORExit,
        IPtoASN,
        IPtoASNPeers
    ],
    'ipv4_subnet': [
    ],
    'ipv6_subnet': [
    ],
    'asn': [
        ASNInfo
    ],
    'domain': [
        DBL,
        RHSBL
    ],
    'hash': [
        MHR
    ]
}
