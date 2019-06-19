# encoding: utf-8


class NoForwardersConfigured(Exception):
    pass


class MultipleForwardersForInterface(Exception):
    pass


class NoActiveRecordForHost(Exception):
    pass


class DNSQueryFailed(Exception):
    pass
