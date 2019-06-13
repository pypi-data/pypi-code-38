# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

class ServiceNotFoundError(Exception):
    def __init__(self, *resolve_chain):
        self.resolve_chain = resolve_chain
        msg = f'unknown service: {repr(resolve_chain[-1])}'
        if len(resolve_chain) > 1:
            resolve_chain_msg = '->'.join([repr(i) for i in resolve_chain])
            msg += f'; resolve chain: {resolve_chain_msg}'
        super().__init__(msg)
