from pylibpcap3.mpsniffing import MPPCAPListenSession
from pylibpcap3.aqueue import AsyncProcessQueue
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import asyncio

class PCAPServer:
	def __init__(self):
		self.a = 'A'
		
	async def test(self):
		loop = asyncio.get_running_loop()
		device = r'\Device\NPF_{A95208F3-2438-44BB-AD8D-1A9F5086D97E}'
		in_q = AsyncProcessQueue()
		out_q = AsyncProcessQueue()
		
		session = MPPCAPListenSession(device, in_q, 'udp')
		session.daemon = True
		session.start()
		
		while True:
			data = await in_q.coro_get()
			print(data)
			
	
	async def run(self):
		await self.test()

		
