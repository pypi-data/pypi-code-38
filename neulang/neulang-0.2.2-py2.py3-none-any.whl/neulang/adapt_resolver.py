"""
A resolver based on the Mycroft Adapt intent parser.
"""


import logging

import re
from time import time
from ast import Str, Expr, parse

from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine

from .base import BaseResolver


class AdaptResolver(BaseResolver):

    def __init__(self):
        self._pifs = {}
        super().__init__()
        self._ad_test = re.compile(r'^add_adapt_handler(\s.+)?')
        self._eng = IntentDeterminationEngine()
        return

    def resolve(self, o_node):
        if not self.is_adapt(o_node): return False
        a_node = None
        head = o_node.get('head')
        h_match = self._ad_test.match(head)

        if h_match:
            a_node = self.add_handler(o_node)
            assert a_node is None, f"None expected but got {type(a_node)}"

        else:
            a_node = self.nl_call(o_node)
        return a_node

    def add_handler(self, data):
        engine = self._eng
        ignores = ['intent_parts', 'body']
        data = self._node_to_list(data, ignore_first=ignores)
        if not len(data) == 2:
            raise ValueError(f"Expected 2")
        matches = data[0].get("intent_parts")
        assert all([isinstance(m, Str) for m in matches]), f"Expected all strings"
        itt_parts = [m.s for m in matches]
        body = data[1].get("body")
        body = [Expr(a_n) if not type(a_n) in self._stmt_types else a_n for a_n in body]
        th = f"ad_{abs(hash(time()))}"
        #self._ad_hashes[match] = ad_h
        ib = IntentBuilder(f'{th}')
        ipn_rx = re.compile(r'P<\w+>.')

        for part in itt_parts:
            [
                ib.optionally(ipn[2:-2].partition('_')[-1])
                if 'opt_' in ipn else
                ib.require(ipn[2:-2].partition('_')[-1])
                if 'req_' in ipn else None
                for ipn in ipn_rx.findall(part)
            ]
            part = part.replace('opt_', '').replace('req_', '')
            engine.register_regex_entity(part)
        itt = ib.build()
        engine.register_intent_parser(itt)
        pif = body
        self._pifs[th] = pif
        return None

    def nl_call(self, data):
        head = data.get("head")
        body = data.get("body", [])
        itt = context = p_body = None
        engine = self._eng

        if body:
            # preprocess body
            p_body = self._node_to_list(data)
        intents = [i for i in engine.determine_intent(head)]
        if not intents: return False
        itt = intents[0]
        bit = itt.get('intent_type')
        pif = self._pifs.get(bit)
        if not pif: return False
        assert isinstance(pif, list), f'Unable to resolve `{head}`'
        del itt['intent_type']
        del itt['confidence']
        itta = parse(f'nl_ctx={itt}').body[0]
        node = [itta] + pif
        return node

    def is_adapt(self, node):
        # Just a stub until a way to detect
        return True
