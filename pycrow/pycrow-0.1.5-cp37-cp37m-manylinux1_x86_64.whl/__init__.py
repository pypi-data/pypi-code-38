import pycrow
import pycrow.libcrow

from pycrow.libcrow import *
import time

crowker = None

def spin():
	while 1:
		pycrow.libcrow.onestep()
		time.sleep(0.00001)

def diagnostic(pack=False, live=False):
	if pack:
		pycrow.libcrow.diagnostic()

	if live:
		pycrow.libcrow.live_diagnostic()

def incoming_handler(func):
	pycrow.libcrow.set_incoming_handler(func)

subs = dict()
subs_init = False

def subscribe_handler_impl(packet):
	thm = packet.theme()
	subs[thm](packet)

def subscribe(theme, handler, **kwargs):
	subs[theme] = handler

	if not subs_init:
		pycrow.libcrow.set_subscribe_handler(subscribe_handler_impl)

	return pycrow.libcrow.subscribe(crowker, theme, **kwargs)


def use_environment_crowker():
	crowker = pycrow.libcrow.environment_crowker()

def set_crowker(cker):
	global crowker
	crowker = pycrow.libcrow.compile_address(cker)