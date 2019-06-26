import time
import concurrent.futures
from multiprocessing import Pool

s = [1, 2, 3]

with Pool(2) as p:
	result = p.map(time.sleep, s)
	print(type(result))
	print(result[0])

with concurrent.futures.ThreadPoolExecutor(4):
	result = e.map(time.sleep, s)
	print(type(result))
	print(result[0])