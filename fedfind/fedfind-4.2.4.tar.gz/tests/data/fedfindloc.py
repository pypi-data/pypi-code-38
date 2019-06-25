#!/bin/python3

"""This script generates the compose-urls-YYYYMMDD.json list of compose
URLs that is used for the test_compose_urls test. You need to have a
checkout of fedora_nightlies symlinked to wherever you run the script
from for it to work.
"""

import datetime
import logging
import fedora_nightlies
import json

logging.basicConfig(level=logging.DEBUG)

msgs = fedora_nightlies.datagrepper_query(['org.fedoraproject.prod.pungi.compose.status.change'], 180)
urls = [msg.get('location') for msg in msgs]
urls = set([url for url in urls if url])

fn = 'compose-urls-{0}.json'.format(datetime.date.today().strftime('%Y%m%d'))
fh = open(fn, 'w')
json.dump(list(urls), fh, indent=4, separators=(',', ': '))
fh.close()
