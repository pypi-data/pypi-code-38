#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sesame import build_shared

def get_builder(**kwargs):
    builder = build_shared.get_builder(**kwargs)
    builder.add()
    return builder
