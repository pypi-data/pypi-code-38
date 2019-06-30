import subprocess
from subprocess import Popen
import socket
import docker
import os
import ain.constants as constants


class InstanceUtil():

  @staticmethod
  def createTtyd(socketName):
    try:
      print("[+] open ttyd socket.")
      Popen(["ttyd" ,"-i" ,socketName ,"/bin/bash"],
                shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
      print(f"[-] failed to create ttyd socket. - {socketName}")
      print(e)
      exit(1)

  @staticmethod
  def removeTtyd(socketName):
    try:
      if (os.path.exists(socketName)):
        os.remove(socketName)
    except Exception as e:
      print(f"[-] failed to remove ttyd socket. - {socketName}")
      print(e)
      exit(1)

  @staticmethod
  def createContainer(image, envs):
    try:
      client = docker.from_env()
      client.containers.run(image=image, command="yarn start",
                            detach=True,
                            name="ain_worker",
                            volumes={
                              f'/var/run/docker.sock': {'bind': f'/var/run/docker.sock', 'mode': 'ro'},
                              constants.SHARED_PATH:{'bind': "/share", 'mode': "rw"}
                              }
                            )
      
      print("[+] started ain worker server!")
    except Exception as e:
      print("[-] failed to create container.")
      print(e)
      exit(1)

  @staticmethod
  def removeContainer(name):
    try:
      client = docker.from_env()
      constainer = client.containers.get(name)
      constainer.remove(force=True)
      
    except Exception as e:
      print("failed to remove container.")
      print(e)