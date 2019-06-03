#! /usr/bin/env python -u

import csv
import json
import sys
from os import environ

w = csv.writer(sys.stdout)

w.writerow(['row', 'type', 'k', 'v'])

i = 0

for k in sys.argv:
    w.writerow([i, 'arg', k, ''])
    i += 1

for k, v in environ.items():
    w.writerow([i, 'env', k, v])
    i += 1

for k, v in json.loads(environ['PROPERTIES']).items():
    w.writerow([i, 'prop', k, v])
    i += 1
