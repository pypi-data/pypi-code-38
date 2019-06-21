
text = r'''# Where data will be stored?
DataDirectory {0}\TorData\data\{1}

# Countdown time before exit
ShutdownWaitLength 5

# Where to write PID
PidFile {0}\TorData\data\{1}\pid

# Communication ports
SocksPort {3}:{1}
ControlPort {3}:{2}

# Authentication of Tor
CookieAuthentication 1

# GeoIP file paths?
GeoIPFile {0}\Data\Tor\geoip
GeoIPv6File {0}\Data\Tor\geoip6

SocksListenAddress {3}
SocksPolicy accept {3}/24
'''

def make_torrc(tor_dir, socket_port, control_port,ipv4):
    """example how torrc file should be constructed"""
    return text.format(tor_dir, socket_port, control_port, ipv4).replace('        ', "")