import ctypes
import socket

UNIX_PATH_MAX = 255

class PCAPSocketAddr:
	def __init__(self):
		self.addr = None
		self.port = None
		self.family = None
	
	@staticmethod
	def from_cstruct(cs):
		addr = PCAPSocketAddr()
		addr.addr = socket.inet_ntop(cs.sa_family, cs.sin_addr)
		addr.port = cs.sin_port
		addr.family = cs.sa_family
		return addr
		
	def __str__(self):
		t = '=PCAPSocketAddr=\r\n'
		for k in self.__dict__:
			if isinstance(self.__dict__[k], list):
				for item in self.__dict__[k]:
					t += '%s: %s\r\n' % (k, item)
			else:
				t += '%s: %s\r\n' % (k, self.__dict__[k])
		return t
		
class PCAPInterfaceAddr:
	def __init__(self):
		self.addr = None
		self.netmask = None
		self.broadaddr = None
		self.dstaddr = None
	
	@staticmethod
	def from_cstruct(cs):
		addr = PCAPInterfaceAddr()
		if cs.addr:
			addr.addr = PCAPSocketAddr.from_cstruct(cs.addr.contents)
		if cs.netmask:
			addr.netmask = PCAPSocketAddr.from_cstruct(cs.netmask.contents)
		if cs.broadaddr:
			addr.broadaddr = PCAPSocketAddr.from_cstruct(cs.broadaddr.contents)
		if cs.dstaddr:
			addr.dstaddr = PCAPSocketAddr.from_cstruct(cs.dstaddr.contents)
		return addr, cs.next
		
	def __str__(self):
		t = '=PCAPInterfaceAddr=\r\n'
		for k in self.__dict__:
			if isinstance(self.__dict__[k], list):
				for item in self.__dict__[k]:
					t += '%s: %s\r\n' % (k, item)
			else:
				t += '%s: %s\r\n' % (k, self.__dict__[k])
		return t
		
class PCAPInterface:
	def __init__(self):
		self.name = None
		self.description = None
		self.addresses = []
	
	@staticmethod
	def from_cstruct(cs):
		addr = PCAPInterface()
		if cs.name:
			addr.name = ctypes.string_at(cs.name).decode()
		
		if cs.description:
			addr.description = ctypes.string_at(cs.description).decode()
		
		if cs.addresses:
			iaddr, next = PCAPInterfaceAddr.from_cstruct(cs.addresses.contents)
			addr.addresses.append(iaddr)
			while True:
				if not next:
					break
				iaddr, next = PCAPInterfaceAddr.from_cstruct(next.contents)
				addr.addresses.append(iaddr)
				
		return addr, cs.next
		
	def __str__(self):
		t = '=PCAPInterface=\r\n'
		for k in self.__dict__:
			if isinstance(self.__dict__[k], list):
				for item in self.__dict__[k]:
					t += '%s: %s\r\n' % (k, item)
			else:
				t += '%s: %s\r\n' % (k, self.__dict__[k])
		return t

class sockaddr_un(ctypes.Structure):
    _fields_ = [("sa_family", ctypes.c_ushort),  # sun_family
                ("sun_path", ctypes.c_char * UNIX_PATH_MAX)]
				
class sockaddr_in(ctypes.Structure):
    _fields_ = [("sa_family", ctypes.c_ushort),  # sin_family
                ("sin_port", ctypes.c_ushort),
                ("sin_addr", ctypes.c_byte * 4),
                ("__pad", ctypes.c_byte * 8)]    # struct sockaddr_in is 16 bytes
				
class PCAP_ADDR(ctypes.Structure):
	pass
PCAP_ADDR._fields_ = [('next',ctypes.POINTER(PCAP_ADDR)),('addr',ctypes.POINTER(sockaddr_in)),('netmask',ctypes.POINTER(sockaddr_in)),('broadaddr',ctypes.POINTER(sockaddr_in)),('dstaddr',ctypes.POINTER(sockaddr_in))]

class PCAP_IF(ctypes.Structure):
	pass
PCAP_IF._fields_ = [('next',ctypes.POINTER(PCAP_IF)),('name',ctypes.POINTER(ctypes.c_char)),('description',ctypes.POINTER(ctypes.c_char)),('addresses',ctypes.POINTER(PCAP_ADDR))]

PPCAP_IF = ctypes.POINTER(PCAP_IF)

# https://stackoverflow.com/questions/10107971/using-struct-timeval-in-python
class timeval(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long), ("tv_usec", ctypes.c_long)]

# https://www.winpcap.org/docs/docs_412/html/structpcap__pkthdr.html
class PCAP_PKTHDR(ctypes.Structure):
	 _fields_ = [("ts", timeval), 
                ("caplen", ctypes.c_uint32),
                ("len", ctypes.c_uint32)
				]
PPCAP_PKTHDR = ctypes.POINTER(PCAP_PKTHDR)

# https://unix.superglobalmegacorp.com/Net2/newsrc/net/bpf.h.html
class bpf_insn(ctypes.Structure):
	 _fields_ = [("code", ctypes.c_ushort), 
                ("jt", ctypes.c_char),
                ("jf", ctypes.c_char),
                ("k", ctypes.c_long),
				]

# https://unix.superglobalmegacorp.com/Net2/newsrc/net/bpf.h.html
class bpf_program(ctypes.Structure):
	 _fields_ = [("bf_len", ctypes.c_uint32), 
                ("bf_insns", bpf_insn),
				]
				
#typedef void(* pcap_handler)(u_char *user, const struct pcap_pkthdr *pkt_header, const u_char *pkt_data)
PCAP_HANDLER = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_char), PPCAP_PKTHDR, ctypes.POINTER(ctypes.c_char))

# https://www.winpcap.org/docs/docs_412/html/structpcap__send__queue.html
class PCAP_SEND_QUEUE(ctypes.Structure):
	 _fields_ = [("maxlen", ctypes.c_uint), 
                ("len", ctypes.c_uint),
                ("buffer", ctypes.c_char_p),
				]
				
PPCAP_SEND_QUEUE = ctypes.POINTER(PCAP_SEND_QUEUE)
