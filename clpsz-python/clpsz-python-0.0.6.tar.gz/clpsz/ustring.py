import re
import binascii


def string_to_hex(s):
	return binascii.hexlify(s)


def hex_to_string(h):
	return binascii.unhexlify(h)


# a.k.a levenshteins distance, see https://en.wikipedia.org/wiki/Edit_distance
def get_edit_distance(str_a, str_b):
	if len(str_a) > len(str_b):
		str_a, str_b = str_b, str_a

	distances = range(len(str_a) + 1)
	for i2, c2 in enumerate(str_b):
		distances_ = [i2 + 1]
		for i1, c1 in enumerate(str_a):
			if c1 == c2:
				distances_.append(distances[i1])
			else:
				distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
		distances = distances_
	return distances[-1]


def get_re_group_n(pattern, line, n):
	p = re.compile(pattern)
	m = p.match(line)
	return m.group(n)