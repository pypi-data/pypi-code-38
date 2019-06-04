# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 19:26:46 2018

@author: Frank
"""
 
import socket, threading


def TCP_connect(ip, port_number, delay, output):
    TCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPsock.settimeout(delay)
    try:
        TCPsock.connect((ip, port_number))
        output[port_number] = 'Listening'
    except:
        output[port_number] = ''

def scan_ports(host_ip, delay=10000):

    threads = []        # To run TCP_connect concurrently
    output = {}         # For printing purposes

    # Spawning threads to scan ports
    for i in range(10000):
        t = threading.Thread(target=TCP_connect, args=(host_ip, i, delay, output))
        threads.append(t)

    # Starting threads
    for i in range(10000):
        threads[i].start()

    # Locking the script until all threads complete
    for i in range(10000):
        threads[i].join()

    # Printing listening ports from small to large
    for i in range(10000):
        if output[i] == 'Listening':
            print(str(i) + ': ' + output[i])

'''
netstat –an ¦find /i “listening”
netstat –ano ¦find /i “listening”
nslookup baidu.com
ping baidu.com
'''
import os
def scan_ports_oneself(port=80):
    os.system('netstat')
    os.system('netstat -na | find "%s"'%port)
    
def main():
    host_ip = input("Enter host IP: ")
    delay = int(input("How many seconds the socket is going to wait until timeout: "))   
    scan_ports(host_ip, delay)
    
if __name__ == '__main__':
	main()