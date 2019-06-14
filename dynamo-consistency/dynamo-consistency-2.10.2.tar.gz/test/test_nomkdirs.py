#! /usr/bin/env python

# They config.py module has an annoying habit of creating directories
# Let's kill that

import os
for d in ['cache', 'logs']:
    if os.path.exists(d):
        os.rmdir(d)

from dynamo_consistency import datatypes

if __name__ == '__main__':
    if os.path.exists('cache') or os.path.exists('logs'):
        exit(1)
