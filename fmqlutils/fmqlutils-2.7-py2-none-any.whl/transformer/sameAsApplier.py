#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import json
from datetime import datetime
import re
from collections import defaultdict, OrderedDict
from shutil import copy2
import random

"""
Note: FMQL v1.1 used to embed some of this logic. As it is very particular and subject to change, it was moved out to the client side/fmaf
in FMQL v2
"""

"""
Follows FMQL sameAs (see comment in utils)
- 80, 81 for codes
- if vuid field for others

Note: for vuid etc, may embed meta about active since etc

Note: may flatten out all concept info like this and have
clinical and meta records use the icd10cm: etc etc directly
and nix own copies of these things beyond simple concept
lookups.

- NOTE: GOAL -- a service ala Parameter Service for VUID-backed national concepts with
a normalized status (nix the multiple) and minimum mandatory fields.
  ie/ want HDI indicated VUID files to be treated uniformly ... do transform below
  ex/ last of effectiveDateTime multiple yields isInactive: ...
"""
class PromoteSameAs:

    def __init__(self):
        pass

    def refine(self, record):
        if "vuid" in record:
            record["sameAs"] = "urn:vuid:" + record["vuid"]
            del record["vuid"]
            return record
        idProp = "id" if "id" in record else "_id"
        if re.match(r'81\-', record[idProp]):
            record["sameAs"] = "urn:cpt:" + record["cpt_code"]
            # no delete for now
            return record
        return record
