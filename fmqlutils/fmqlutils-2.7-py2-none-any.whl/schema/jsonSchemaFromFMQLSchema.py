#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import os
import re
import json
from datetime import datetime
from collections import defaultdict, OrderedDict
import copy
import logging
import shutil

"""
From type data summary from walking data, generate MongoDB supported JSON Schema definition

Outside package that checks schema: https://pypi.org/project/jsonschema/

Some Links:
- https://docs.mongodb.com/manual/core/schema-validation/
- https://docs.mongodb.com/manual/reference/operator/query/jsonSchema/#op._S_jsonSchema
- https://tools.ietf.org/html/draft-zyp-json-schema-04
- https://tools.ietf.org/html/draft-fge-json-schema-validation-00
- https://docs.mongodb.com/manual/reference/operator/query/type/#document-type-available-types
- https://docs.mongodb.com/manual/reference/operator/query/jsonSchema/
"""
def toJSONSchemaMongo(typeData):

