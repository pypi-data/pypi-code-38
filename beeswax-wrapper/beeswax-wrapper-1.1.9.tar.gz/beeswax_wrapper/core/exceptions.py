#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exception classes for the beeswax wrapper
"""
from __future__ import unicode_literals


class BeeswaxRESTException(Exception):
    """
    Raised if we get a response from the Beeswax endpoint with the 'success' attribute is False.
    """
    pass
