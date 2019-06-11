#! /usr/bin/env python
"""Unpack a signed .tar.gz.asc or .tar.gz.gpg archive into a temporary directory
"""
import datetime

def ts_name( ):
    """Produce a human-readable timestamp (UTC ISO formatted date)"""
    d = datetime.datetime.utcnow()
    return d.isoformat().replace(':','.')
