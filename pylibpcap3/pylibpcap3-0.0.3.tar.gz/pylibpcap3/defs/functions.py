import ctypes
import platform

from pylibpcap3.defs.structs import *

if platform.system() == 'Windows':
	pcapdll = ctypes.WinDLL("wpcap.dll")
else:
	pcapdll = ctypes.cdll.LoadLibrary("libpcap.so.0.8")

HANDLE = ctypes.c_void_p

# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga7b128eaeef627b408f6a6e2a2f5eb45d
def pcap_findalldevs():
	def errc(result, func, arguments):
		if result == 0:
			return result
		error_message = ctypes.string_at(arguments[1])
		raise Exception('%s failed with error code %s (%s)' % ('pcap_findalldevs', result, error_message))
		
	_pcap_findalldevs = pcapdll.pcap_findalldevs
	_pcap_findalldevs.argtypes = [ctypes.POINTER(PPCAP_IF), ctypes.POINTER(ctypes.c_char)]
	_pcap_findalldevs.restype  = ctypes.c_int
	_pcap_findalldevs.errcheck  = errc
	
	pinterfaces = PPCAP_IF()
	error = ctypes.create_string_buffer(1024)
	res = _pcap_findalldevs(ctypes.byref(pinterfaces), error)
	
	oi = []
	if pinterfaces:
		interfaces = pinterfaces.contents
		
		iface, next = PCAPInterface.from_cstruct(interfaces)
		oi.append(iface)
		if next:
			while True:
				if not next:
					break
				iface, next = PCAPInterface.from_cstruct(next.contents)
				oi.append(iface)
	
	return oi
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#gaae6abe06e15c87b803f69773822beca8
def pcap_open_live(device_name, snaplen = 65535, promisc = 1, to_ms = 100):
	def errc(result, func, arguments):
		if result:
			#according to docs, there may even be a warning even if the function sucseeds!
			warning_message = ctypes.string_at(arguments[-1]).decode()
			if len(warning_message) > 0:
				print('pcap_open_live sucsess, but warning was set! WARNING: %s' % warning_message)
			
			return result
		error_message = ctypes.string_at(arguments[1])
		raise Exception('%s failed with error code %s (%s)' % ('pcap_open_live', result, error_message))
		
	_pcap_open_live = pcapdll.pcap_open_live
	_pcap_open_live.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_char)]
	_pcap_open_live.restype  = ctypes.POINTER(ctypes.c_int)
	_pcap_open_live.errcheck  = errc
	
	#can be string or None
	if device_name is not None:
		if device_name == '':
			device_name = 'any'
		device_name = ctypes.create_string_buffer(device_name.encode())
	
	error = ctypes.create_string_buffer(1024)
	res = _pcap_open_live(device_name, snaplen, promisc, to_ms, error)
	
	return res
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#gadf60257f650aaf869671e0a163611fc3
def pcap_next(pcap_handle):
	def errc(result, func, arguments):
		if result:
			return result
		raise Exception('%s failed!' % ('pcap_next',))
		
	_pcap_next = pcapdll.pcap_next
	_pcap_next.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(PCAP_PKTHDR)]
	_pcap_next.restype  = ctypes.POINTER(ctypes.c_int)
	_pcap_next.errcheck  = errc
	
	
	hdr = PCAP_PKTHDR()
	res = _pcap_next(pcap_handle, ctypes.byref(hdr))
	data = ctypes.string_at(res, hdr.caplen)
	
	return data
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#gadf60257f650aaf869671e0a163611fc3
def pcap_next_ex(pcap_handle):			
	_pcap_next_ex = pcapdll.pcap_next_ex
	_pcap_next_ex.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(PPCAP_PKTHDR), ctypes.POINTER(ctypes.c_char)]
	_pcap_next_ex.restype  = ctypes.c_int
	
	
	phdr = PPCAP_PKTHDR()
	buff = ctypes.create_string_buffer(0)
	result = _pcap_next_ex(pcap_handle, ctypes.byref(phdr), buff)
	
	if result == 1:
		hdr = phdr.contents
		return ctypes.string_at(buff, hdr.caplen)
	elif result == 0:
		return None
	elif result == -1:
		raise Exception('%s failed with error code %s' % ('pcap_next_ex', result))
	elif result == -1:
		return b''
	else:
		raise Exception('%s unexpected return code! %s' % ('pcap_next_ex', result))
		
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#gadf60257f650aaf869671e0a163611fc3
def pcap_getevent(pcap_handle):		
	_pcap_getevent = pcapdll.pcap_getevent
	_pcap_getevent.argtypes = [ctypes.POINTER(ctypes.c_int)]
	_pcap_getevent.restype  = HANDLE
	
	res = _pcap_getevent(pcap_handle)
		
	return res
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#gadf60257f650aaf869671e0a163611fc3
def pcap_close(pcap_handle):		
	_pcap_close = pcapdll.pcap_close
	_pcap_close.argtypes = [ctypes.POINTER(ctypes.c_int)]
	_pcap_close.restype  = None
	
	res = _pcap_close(pcap_handle)
		
	return res

# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga51dbda0f1ab9da2cfe49d657486d50b2
def pcap_sendpacket(pcap_handle, raw_data):
	def errc(result, func, arguments):
		if result == 0:
			return result
		raise Exception('%s failed with error code %s ' % ('pcap_sendpacket', result))
		
	_pcap_sendpacket = pcapdll.pcap_sendpacket
	_pcap_sendpacket.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_char), ctypes.c_int]
	_pcap_sendpacket.restype  = ctypes.c_int
	
	buff = ctypes.create_string_buffer(raw_data, len(raw_data))
	
	res = _pcap_sendpacket(pcap_handle, buff, len(raw_data))
		
	return res
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga363bdc6f6b39b4979ddcf15ecb830c5c
def pcap_compile(pcap_handle, expr, optimize = 1, netmask = 0):
	def errc(result, func, arguments):
		if result != -1:			
			return result
		raise Exception('%s failed with error code %s' % ('pcap_compile', result))
		
	_pcap_compile = pcapdll.pcap_compile
	_pcap_compile.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(bpf_program), ctypes.POINTER(ctypes.c_char), ctypes.c_int, ctypes.c_uint32]
	_pcap_compile.restype  = ctypes.c_int
	_pcap_compile.errcheck  = errc
	
	filter_handle = bpf_program()
	buff = ctypes.create_string_buffer(expr.encode())
	res = _pcap_compile(pcap_handle, ctypes.byref(filter_handle), buff, optimize, netmask)
	
	return filter_handle
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#gaf5f9cfe85dad0967ff607e5159b1ba61
def pcap_setfilter(pcap_handle, filter_ptr):
	def errc(result, func, arguments):
		if result != -1:			
			return result
		raise Exception('%s failed with error code %s' % ('pcap_setfilter', result))
		
	_pcap_setfilter = pcapdll.pcap_setfilter
	_pcap_setfilter.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(bpf_program)]
	_pcap_setfilter.restype  = ctypes.c_int
	_pcap_setfilter.errcheck  = errc
	
	res = _pcap_setfilter(pcap_handle, ctypes.byref(filter_ptr))
	
	return res
	
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga60ce104cdf28420d3361cd36d15be44c
def pcap_dispatch(pcap_handle, cnt, cb, user = 0):
	"""
	user param is a pointer to a data structure if you need to be passed to the callback
	"""		
	_pcap_dispatch = pcapdll.pcap_dispatch
	_pcap_dispatch.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, PCAP_HANDLER, ctypes.c_void_p]
	_pcap_dispatch.restype  = ctypes.c_int
	
	user = ctypes.c_void_p(user)
	res = _pcap_dispatch(pcap_handle, cnt, cb, user)
	
	if res >= 0:
		return res
	elif res == -1:
		raise Exception('pcap_dispatch error!')
	else:
		return None
	return res
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga60ce104cdf28420d3361cd36d15be44c
def pcap_loop(pcap_handle, cnt, cb, user = 0):
	"""
	user param is a pointer to a data structure if you need to be passed to the callback
	"""		
	_pcap_loop = pcapdll.pcap_loop
	_pcap_loop.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, PCAP_HANDLER, ctypes.c_void_p]
	_pcap_loop.restype  = ctypes.c_int
	
	user = ctypes.c_void_p(user)
	res = _pcap_loop(pcap_handle, cnt, cb, user)
	
	if res >= 0:
		return res
	elif res == -1:
		raise Exception('pcap_loop error!')
	else:
		return None
	return res
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga60ce104cdf28420d3361cd36d15be44c
def pcap_setnonblock(pcap_handle, blocking = 0):
	"""
	user param is a pointer to a data structure if you need to be passed to the callback
	"""
	def errc(result, func, arguments):
		if result != -1:			
			return result
		error_message = ctypes.string_at(arguments[2])
		raise Exception('%s failed with error code %s Reason: %s' % ('pcap_setnonblock', result, error_message))
		
	_pcap_setnonblock = pcapdll.pcap_setnonblock
	_pcap_setnonblock.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.POINTER(ctypes.c_char)]
	_pcap_setnonblock.restype  = ctypes.c_int
	_pcap_setnonblock.errcheck  = errc
	
	error = ctypes.create_string_buffer(1024)
	res = _pcap_setnonblock(pcap_handle, blocking, error)
	
	return res
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga4c57ea320d71dbfe55c5665af9db1297
def pcap_sendqueue_alloc(memsize):
	"""
	memsize speficyes the amount of bytes in the kernel buffer to be allocated
	"""
		
	_pcap_sendqueue_alloc = pcapdll.pcap_sendqueue_alloc
	_pcap_sendqueue_alloc.argtypes = [ctypes.c_int]
	_pcap_sendqueue_alloc.restype  = PPCAP_SEND_QUEUE
	
	res = _pcap_sendqueue_alloc(memsize)
	
	return res
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga4c57ea320d71dbfe55c5665af9db1297
def pcap_sendqueue_destroy(p_sendqueue):
	_pcap_sendqueue_destroy = pcapdll.pcap_sendqueue_destroy
	_pcap_sendqueue_destroy.argtypes = [PPCAP_SEND_QUEUE]
	_pcap_sendqueue_destroy.restype  = ctypes.c_int
	
	res = _pcap_sendqueue_destroy(p_sendqueue)
	
	return res
	
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga4c57ea320d71dbfe55c5665af9db1297
def pcap_sendqueue_transmit(pcap_handle ,p_sendqueue, sync = 0):
	_pcap_sendqueue_transmit = pcapdll.pcap_sendqueue_transmit
	_pcap_sendqueue_transmit.argtypes = [ctypes.POINTER(ctypes.c_int), PPCAP_SEND_QUEUE, ctypes.c_int]
	_pcap_sendqueue_transmit.restype  = ctypes.c_uint
	
	res = _pcap_sendqueue_transmit(pcap_handle, p_sendqueue, sync)
	
	return res
	
# https://www.winpcap.org/docs/docs_412/html/group__wpcapfunc.html#ga4c57ea320d71dbfe55c5665af9db1297
def pcap_sendqueue_queue(p_sendqueue, packet_data):
	_pcap_sendqueue_queue = pcapdll.pcap_sendqueue_queue
	_pcap_sendqueue_queue.argtypes = [PPCAP_SEND_QUEUE, ctypes.POINTER(PCAP_PKTHDR), ctypes.c_char_p]
	_pcap_sendqueue_queue.restype  = ctypes.c_uint
	
	plen = len(packet_data)
	
	tim = timeval()
	tim.tv_sec = 0
	tim.tv_usec = 0
	
	hdr = PCAP_PKTHDR()
	hdr.ts = tim
	hdr.caplen = plen
	hdr.len = plen
	
	buff = ctypes.create_string_buffer(packet_data, plen)
	res = _pcap_sendqueue_queue(p_sendqueue, ctypes.byref(hdr), buff )
	
	return res
	

	
if __name__ == '__main__':
	oi = pcap_findalldevs()
	for iface in oi:
		print(iface)
		
	devicename = '\\Device\\NPF_{A95208F3-2438-44BB-AD8D-1A9F5086D97E}'
	print('Opening device! %s' % devicename)
	pcap_handle = pcap_open_live(devicename)
	print(pcap_handle)
	#while True:
	#	pcap_next(pcap_handle)
	#print(pcap_next_ex(pcap_handle))
	print(pcap_getevent(pcap_handle))
	print(pcap_sendpacket(pcap_handle, b'HELLO WORLD!'))
	print('DONE!')