import multiprocessing
import ctypes
from pylibpcap3.defs.functions import *
from pylibpcap3.defs.structs import *

class MPPCAPListenSession(multiprocessing.Process):
	def __init__(self, ifname, out_q, filter = None):
		multiprocessing.Process.__init__(self)
		self.ifname = ifname
		self.filter = filter
		
		self.out_q = out_q
	
		self.pcap_handle = None
		self.ifinfo = None
		self.pcap_sendq = None
		self.queue_size = 0
		
		self.pkt_cb = None
		self.filter_handles = {} #id -> filter_handle
		self.current_filter_id = 0
				
	@staticmethod
	def get_all_devices():
		return pcap_findalldevs()
		
	def packet_arrived_cb(self, user, p_pkt_header, pkt_data):
		try:
			pkt_header = p_pkt_header.contents
			data = ctypes.string_at(pkt_data, pkt_header.caplen)
			self.out_q.put(data)
		except Exception as e:
			print('packet_in_handler_cb: %s ' % e)
		finally:
			return 0
		
	def run(self):
		#open device
		self.pcap_handle = pcap_open_live(self.ifname)
		#setting filter
		if self.filter:
			filter_handle = pcap_compile(self.pcap_handle, self.filter)
			pcap_setfilter(self.pcap_handle, filter_handle)
		#register read callback
		self.pkt_cb = PCAP_HANDLER(self.packet_arrived_cb)
		pcap_loop(self.pcap_handle, -1, self.pkt_cb)
		print('loop returned!')
