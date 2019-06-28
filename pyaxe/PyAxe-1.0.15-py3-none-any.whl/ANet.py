import socket
import re
import platform
import subprocess

def getLocalIP():
    """
    Returns the actual ip of the local machine.
    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet.
    In this case, a Google DNS server is used, but the specific address does not matter much.
    No traffic is actually sent.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        (addr, port) = sock.getsockname()
        sock.close()
        return addr
    except socket.error:
        return '127.0.0.1'

def _get1stNetworkAdapterIP_Unix():
    try:
        s = subprocess.check_output("ifconfig")
    except:
        return "0.0.0.0"
    pattern = re.compile(r'((25[0-5]|2[0-4]\d|1\d{2}|[1-9]\d|\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]\d|\d)')
    match = pattern.search(s)
    if match:
        return match.group()
    return "0.0.0.0"
    
def get1stNetworkAdapterIP():
    if platform.system() == "Windows":
        return socket.gethostbyname(socket.getfqdn(socket.gethostname()))   
    else:
        return _get1stNetworkAdapterIP_Unix()
        