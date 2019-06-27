import socket
import fcntl
import struct

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname.encode('utf-8')[:15])
        )[20:24])
    except IOError as e:
        raise e
    finally:
        s.close()
    return None


def get_hostname_ip():
    ip = socket.gethostbyname(socket.gethostname())
    return ip


def get_ip_address_udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ret = s.getsockname()[0]
    s.close()
    return ret


def is_open(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        return True
    except:
        pass
    finally:
        s.close()
    return False
