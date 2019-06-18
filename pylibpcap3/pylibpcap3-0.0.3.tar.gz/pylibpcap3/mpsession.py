import multiprocessing
import threading
import ctypes
import json
from pylibpcap3.defs.functions import *
from pylibpcap3.defs.structs import *

class PCAPSessionCommand:
	def __init__(self, dir = None, cmd = None, data = None):
		self.dir = dir
		self.cmd = cmd
		self.data = data
		
	def to_dict(self):
		t = {}
		t['dir'] = self.dir
		t['cmd'] = self.cmd
		t['data'] = self.data
		return t
	
	@staticmethod
	def from_dict(d):
		return PCAPSessionCommand(d['dir'], d['cmd'], d['data'])
	
	@staticmethod
	def from_json(data):
		return PCAPSessionCommand.from_dict(json.loads(data))
		
	def to_json(self):
		return json.dumps(self.to_dict())
		
class PCAPSessionPacketRply(PCAPSessionCommand):
	def __init__(self, packet_bytes):
		PCAPSessionCommand.__init__(self)
		self.dir = 1
		self.cmd = 'packet'
		self.data = packet_bytes.hex()
		
class PCAPSessionCompileFilterCmd(PCAPSessionCommand):
	def __init__(self, filter_str):
		PCAPSessionCommand.__init__(self)
		self.dir = 0
		self.cmd = 'create_filter'
		self.data = filter_str
		
class PCAPSessionCompileFilterReply(PCAPSessionCommand):
	def __init__(self, filter_handle):
		PCAPSessionCommand.__init__(self)
		self.dir = 1
		self.cmd = 'create_filter'
		self.data = str(filter_handle)
		
class PCAPSessionApplyFilterCmd(PCAPSessionCommand):
	def __init__(self, filter_handle):
		PCAPSessionCommand.__init__(self)
		self.dir = 0
		self.cmd = 'apply_filter'
		self.data = str(filter_handle)
		
class PCAPSessionApplyFilterRply(PCAPSessionCommand):
	def __init__(self, status):
		PCAPSessionCommand.__init__(self)
		self.dir = 1
		self.cmd = 'apply_filter'
		self.data = status
		
class PCAPSessionSendPacketCmd(PCAPSessionCommand):
	def __init__(self, packet_bytes):
		PCAPSessionCommand.__init__(self)
		self.dir = 0
		self.cmd = 'send'
		self.data = packet_bytes.hex()
		

class MPPCAPSession(multiprocessing.Process):
	def __init__(self, ifname, in_q, out_q):
		multiprocessing.Process.__init__(self)
		self.ifname = ifname
		
		self.in_q = in_q
		self.out_q = out_q
	
		self.pcap_handle = None
		self.ifinfo = None
		self.pcap_sendq = None
		self.queue_size = 0
		
		self.pkt_cb = None
		self.filter_handles = {} #id -> filter_handle
		self.current_filter_id = 0
		
		for iface_info in pcap_findalldevs():
			if iface_info.name == self.ifname:
				self.ifinfo = iface_info
				break
				
	@staticmethod
	def get_all_devices():
		return pcap_findalldevs()
		
	def packet_arrived_cb(self, user, p_pkt_header, pkt_data):
		try:
			pkt_header = p_pkt_header.contents
			print('Data in! Size: %s' % pkt_header.caplen)
			data = ctypes.string_at(pkt_data, pkt_header.caplen)
			rply = PCAPSessionPacketRply(data)
			self.in_q.put(rply.to_json())
		except Exception as e:
			print('packet_in_handler_cb: %s ' % e)
		finally:
			return 0
		
	def start_listening(self):
		try:
			print('starting loop')
			self.pkt_cb = PCAP_HANDLER(self.packet_arrived_cb)
			pcap_loop(self.pcap_handle, -1, self.pkt_cb)
			print('loop returned!')
		except Exception as e:
			print(e)
		
	def run(self):
		#open device
		self.pcap_handle = pcap_open_live(self.ifname)
		#register read callback
		listener_t = threading.Thread(target=self.start_listening)
		listener_t.start()
		#allocate sending queue
		self.pcap_sendq = pcap_sendqueue_alloc(100*1024*1024)
		#wait for commands
		while True:
			data = self.out_q.get()
			cmd = PCAPSessionCommand.from_json(data)
			if cmd.cmd == 'create_filter':
				try:
					filter_handle = self.compile_filter(cmd.data)
				except Exception as e:
					self.in_q.put(PCAPSessionCompileFilterReply(-1).to_json())
				else:
					self.in_q.put(PCAPSessionCompileFilterReply(filter_handle).to_json())
			
			elif cmd.cmd == 'apply_filter':
				try:
					self.set_filter(int(cmd.data))
				except Exception as e:
					self.in_q.put(PCAPSessionApplyFilterRply('NO').to_json())
				else:
					self.in_q.put(PCAPSessionApplyFilterRply('OK').to_json())

			else:
				print('Unknown command! %s' % cmd.cmd)
				
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
		
	
	#def handle_out_q(self):
	#	while not self.shutdown_evt.is_set():
	#		data = await self.out_q.get()
	#		#pcap_sendpacket(self.pcap_handle, data)
	#		#print('Q1')
	#		pcap_sendqueue_queue(self.pcap_sendq, data)
	#		#print('Q2')
	#		self.queue_size += 1
	#		if self.queue_size >= 10000:
	#			#await self.loop.run_in_executor(self.executor_type, self.flush_queue)
	#			print('Flushing!')
	#			pcap_sendqueue_transmit(self.pcap_handle ,self.pcap_sendq)
	#			pcap_sendqueue_destroy(self.pcap_sendq)
	#			self.pcap_sendq = pcap_sendqueue_alloc(100*1024*1024)
	#			self.queue_size = 0
	#			print('Flushing done!')
			
			