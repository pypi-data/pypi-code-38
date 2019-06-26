#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This file is free software by d0n <d0n@janeiskla.de>
#
# You can redistribute it and/or modify it under the terms of the GNU -
# Lesser General Public License as published by the Free Software Foundation
#
# This is distributed in the hope that it will be useful somehow.
#
# !WITHOUT ANY WARRANTY!
#
# Without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
"""
yubikey challenge-response lib
"""
from binascii import hexlify

from yubico import \
    find_yubikey, yubikey, yubico_exception

def yubikeys(ykser=None, dbg=False):
	"""
	return a list of yubikeys objects
	"""
	keys = {}
	for i in range(0, 255):
		try:
			key = find_yubikey(debug=dbg, skip=i)
		except yubikey.YubiKeyError:
			break
		if ykser and int(ykser) != int(key.serial()):
			continue
		keys[key.serial()] = key
	return keys

def ykslotchalres(yk, chal, slot):
	"""
	challenge-response function using with given
	challenge (chal) for slot on yubikey found by yubikeys()
	"""
	try:
		return hexlify(yk.challenge_response(
            str(chal).ljust(64, '\0').encode(), slot=slot)).decode()
	except (AttributeError, yubico_exception.YubicoError):
		pass
	return False

def ykchalres(chal, slot=None, ykser=None):
	"""
	challenge-response function using specified slot
	or default (2) as wrapping function for yubikeys() and slotchalres()
	"""
	keys = yubikeys(None)
	res = None
	for (ser, key) in keys.items():
		slots = [2, 1] if not slot else [slot]
		for i in slots:
			res = ykslotchalres(key, chal, i)
			if res:
				return res
	return False
