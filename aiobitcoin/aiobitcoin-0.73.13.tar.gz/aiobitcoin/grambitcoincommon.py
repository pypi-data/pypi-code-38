# -*- coding: utf-8 -*-
from .grambitcoin import GramBitcoin


class GramBitcoinCommon(GramBitcoin):
    def __init__(self, url, gram, read_timeout):
        super().__init__(read_timeout=read_timeout)
        self.url = self.check_url(url, gram)
        self._gram = gram
        self.session = self.check_gram(gram)
