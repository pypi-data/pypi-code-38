# encoding: utf-8

import sys
from pydnserver import DNSQuery

if sys.version_info.major == 2:
    data = "\xb4`\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06images\x08metadata\x03sky\x03com\x00\x00\x01\x00\x01"
else:
    data = b"\xb4`\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06images\x08metadata\x03sky\x03com\x00\x00\x01\x00\x01"

q = DNSQuery(data=data)

d = q._decode_query()
print(d)

r = q.resolve()

print(r)




