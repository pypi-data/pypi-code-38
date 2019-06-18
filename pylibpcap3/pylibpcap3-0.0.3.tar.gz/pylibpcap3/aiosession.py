import asyncio
import ctypes
from pylibpcap3.defs.functions import *
from pylibpcap3.defs.structs import *

class AIOPCAPSession:
	def __init__(self, ifname, executor_type = None):
		self.ifname = ifname
		self.executor_type = executor_type
		self.shutdown_evt = asyncio.Event()
		self.loop = None
		
		self.in_q = asyncio.Queue()
		self.out_q = asyncio.Queue()
	
		self.pcap_handle = None
		self.ifinfo = None
		self.pcap_sendq = None
		self.queue_size = 0
		self.flushing_evt = asyncio.Event()
		
		self.pkt_cb = None
		self.filter_handles = {} #id -> filter_handle
		self.current_filter_id = 0
		
		for iface_info in pcap_findalldevs():
			if iface_info.name == self.ifname:
				self.ifinfo = iface_info
				break
				
	
	def packet_in_handler_cb(self, user, p_pkt_header, pkt_data):
		#print(user)
		#print(pkt_header)
		#print(pkt_data)
		try:
			pkt_header = p_pkt_header.contents
			print('Data in! Size: %s' % pkt_header.caplen)
			data = ctypes.string_at(pkt_data, pkt_header.caplen)
			self.in_q.put_nowait(data)
		except Exception as e:
			print('packet_in_handler_cb: %s ' % e)
		finally:
			return 0
		
	@staticmethod
	def get_all_devices():
		return pcap_findalldevs()
		
	def compile_filter(self, expr, optimize = 1, netmask = 0):
		"""
		expr is a string!
		"""
		filter_handle = pcap_compile(self.pcap_handle, expr, optimize = optimize, netmask = netmask)
		filter_id = self.current_filter_id
		self.current_filter_id += 1
		self.filter_handles[filter_id] = filter_handle
		
		return filter_id
		
	def set_filter(self, filter_id):
		filter_handle = self.filter_handles[filter_id]
		pcap_setfilter(self.pcap_handle, filter_handle)
		
	def get_packet(self):
		try:
			print('starting loop')
			self.pkt_cb = PCAP_HANDLER(self.packet_in_handler_cb)
			pcap_loop(self.pcap_handle, -1, self.pkt_cb)
			print('loop returned!')
		except Exception as e:
			print(e)
			
	
	def setup(self):
		if not self.loop:
			self.loop = asyncio.get_running_loop()
		if not self.pcap_handle:
			self.pcap_handle = pcap_open_live(self.ifname)
		if not self.pcap_sendq:
			self.pcap_sendq = pcap_sendqueue_alloc(100*1024*1024)
			
	#def flush_queue(self):
		

		
	async def handle_out_q(self):
		while not self.shutdown_evt.is_set():
			data = await self.out_q.get()
			#pcap_sendpacket(self.pcap_handle, data)
			#print('Q1')
			pcap_sendqueue_queue(self.pcap_sendq, data)
			#print('Q2')
			self.queue_size += 1
			if self.queue_size >= 10000:
				#await self.loop.run_in_executor(self.executor_type, self.flush_queue)
				print('Flushing!')
				pcap_sendqueue_transmit(self.pcap_handle ,self.pcap_sendq)
				pcap_sendqueue_destroy(self.pcap_sendq)
				self.pcap_sendq = pcap_sendqueue_alloc(100*1024*1024)
				self.queue_size = 0
				print('Flushing done!')
			

				

	async def run(self):
		self.setup()
		asyncio.ensure_future(self.handle_out_q())
		await self.loop.run_in_executor(self.executor_type, self.get_packet)
		print('end!!!!')
			