# -*- coding: utf-8 -*-
# Copyright 2017 - 2019 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

from __future__ import print_function

import sys
import json
import struct
import marshal

if sys.version_info[0] == 3:
	from urllib.parse import quote
	from urllib.request import Request, urlopen
else:
	from urllib import quote
	from urllib2 import Request, urlopen


def serialize(stats):
	nameset = set()
	for (f, l, n), (pc, rc, it, ct, callers) in stats.items():
		nameset.add(f)
		nameset.add(n)
		for (f, l, n), (pc, rc, it, ct) in callers.items():
			nameset.add(f)
			nameset.add(n)

	data = struct.pack('I', len(nameset))
	names = {}
	for name in nameset:
		s = name if isinstance(name, type(b'')) else name.encode('utf-8', 'replace')
		data += struct.pack('H', len(s)) + s
		names[name] = len(names)

	for (f, l, n), (pc, rc, it, ct, callers) in stats.items():
		data += struct.pack('!IIIIIddI', names[f], l, names[n], pc, rc, it, ct, len(callers))
		for (f, l, n), (pc, rc, it, ct) in callers.items():
			data += struct.pack('!IIIIIdd', names[f], l, names[n], pc, rc, it, ct)

	return data


def deserialize(data):
	offset = 4
	name_count, = struct.unpack('I', data[:offset])
	names = []
	for _ in range(name_count):
		size, = struct.unpack('H', data[offset : offset + 2])
		offset += 2
		name = data[offset : offset + size]
		name = name if isinstance(name, str) else name.decode('utf-8')
		names.append(name)
		offset += size

	stats = {}
	while offset < len(data):
		f, l, n, pc, rc, it, ct, caller_count = struct.unpack('!IIIIIddI', data[offset : offset + 40])
		offset += 40
		callers = {}
		stats[(names[f], l, names[n])] = (pc, rc, it, ct, callers)
		for _ in range(caller_count):
			f, l, n, pc, rc, it, ct = struct.unpack('!IIIIIdd', data[offset : offset + 36])
			callers[(names[f], l, names[n])] = (pc, rc, it, ct)
			offset += 36

	return stats


def Push(url, token, project, commit, filename, tag = 'default'):
	stats = marshal.load(open(filename, 'rb'))

	if not url.startswith('http'):
		url = 'http://' + url
	request = Request('%(url)s?token=%(token)s&project=%(project)s&commit=%(commit)s&tag=%(tag)s' % {
		'url': url,
		'token': token,
		'project': project,
		'commit': commit,
		'tag': quote(tag),
	}, serialize(stats))
	response = json.loads(urlopen(request).read())
	if not response['error']:
		print('[Properform] Push Success!')
	else:
		print('[Properform] Push Error: %(error)s!' % response)


def Convert(dst, src):
	with open(src, 'rb') as s:
		stats = deserialize(s.read())
		with open(dst, 'wb') as d:
			marshal.dump(stats, d)
