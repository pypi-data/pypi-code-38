import subprocess
from subprocess import Popen
import dotenv 
import requests_unixsocket
import os
from ain.instanceUtil import InstanceUtil 
import ain.constants as constants

KEY_NAME = ['NAME', 'LIMIT_COUNT', 'MNEMONIC' , "PRICE", "DESCRIPTION"]

class Worker():

	def __init__(self):
		self.ENVS = dotenv.dotenv_values(constants.ENV_FILE_PATH)
		self.session = requests_unixsocket.Session()
		self.hostTtydSocket = f'{constants.SHARED_PATH}/ain_worker_ttyd.sock'
		sharedPath = constants.SHARED_PATH.replace("/", '%2F')
		self.workerAddress =  f'http+unix://{sharedPath}%2Fain_worker.sock'

	def run(self):
		for key in KEY_NAME:
			value = input(f">> {key}: ")

			if self.ENVS[key].replace(" ", "") == "" and value  == "":
				print(f'[-] {key} empty')
				return

			if (value != ""):
				self.ENVS[key] = value
				dotenv.set_key(constants.ENV_FILE_PATH, key, self.ENVS[key])
		
			print(f'{key}: {self.ENVS[key]}')

		print("[?] Do you want to start? (y/n)")
		answer = input()
		if (answer.lower() != 'y'):
			return

		# open provider's ttys socket 
		InstanceUtil.createTtyd(self.hostTtydSocket)

		# open docker container for ain worker server
		InstanceUtil.createContainer(constants.IMAGE, self.ENVS)


	def status(self):
		try:
			response = self.session.get(self.workerAddress + "/info")
			
			ids = response.json()['id']

			if(len(ids) == 0):
				print("[+] does not exist")
				return
		except Exception as e:
			print("[-] worker server error")
			print(e)
			exit(1)
		
		try:
			option = " ".join(ids)
			subprocess.run(["docker", "stats" , option])

		except Exception as e:
			print("[-] subprocess(docker) error")
			print(e)

	def terminate(self):
		try:      
			response = self.session.get(self.workerAddress + "/info")
			cnt = response.json()['cnt']
			if (cnt != 0):
				print(f"[+] instance count: {cnt}")
				print("[+] (y/n)")
				answer = input()
				if (answer.lower() != 'y'):
					return
		except Exception as e:
			print("[-] worker server error - info")
			print(e)

		try:
			response = self.session.get(self.workerAddress + "/terminate")
		except Exception as e:
			print("[-] server error - terminate")
			print(e)
	
		try:
			InstanceUtil.removeContainer("ain_worker")
			print('[+] succeded to remove container!')
		
		except Exception as e:
			print("[-] subprocess(docker) error")
			print(e)

		try:
			InstanceUtil.removeTtyd(self.hostTtydSocket)
			print('[+] succeded to remove ttyd socket')
		except Exception as e:
			print("[-] subprocess error(ttyd socker remove)")
			print(e)
			exit(1)

	def log(self):
		basePath = f"{constants.SHARED_PATH}/log/"
		logFileName = os.listdir(basePath)
		times = [i.split("_")[2].split(".")[0] for i in logFileName]
		if (len(times) == 0) :
			print("[+] does not exist")
		times.sort()             
		try:
			path = os.path.join(basePath, "ain_worker_" + times[-1] + ".log")
			subprocess.run(["tail", "-f" , path])
		except Exception as e:
			print("[-] subprocess(log) error")
			print(e)
