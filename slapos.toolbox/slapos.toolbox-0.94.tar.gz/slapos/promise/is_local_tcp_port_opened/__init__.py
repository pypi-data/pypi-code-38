#!/usr/bin/env python

"""
Check if a specific ip address and port is listening.

No connection establishment is done during the check.

Uses:
- /proc/net/tcp
- /proc/net/tcp6
"""

import sys
import socket
import struct
assert struct.calcsize('I') == 4

def isLocalTcpPortOpened(ip_address, port):
  family = socket.getaddrinfo(ip_address, 0)[0][0]
  conf = {
    socket.AF_INET6: (4, "/proc/net/tcp6"),
    socket.AF_INET: (1, "/proc/net/tcp"),
  }

  int_count = conf[family][0]
  tcp_path = conf[family][1]

  ip_addr_hex = ('%08X' * int_count) % struct.unpack('I' * int_count, socket.inet_pton(family, ip_address))
  full_addr_hex = ip_addr_hex + ":%04X" % port

  return any(full_addr_hex == line.split()[1] for line in open(tcp_path).readlines())

def main():
  if isLocalTcpPortOpened(sys.argv[1], int(sys.argv[2])):
    return 0
  return 1

if __name__ == "__main__":
  sys.exit(main())
