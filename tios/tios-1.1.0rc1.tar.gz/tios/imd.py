# Python module suppprting the Interactive Molecular Dynamics protocol
import socket
import struct

IMD_DISCONNECT = 0
IMD_ENERGIES = 1
IMD_FCOORDS = 2
IMD_GO = 3
IMD_HANDSHAKE = 4
IMD_KILL = 5
IMD_MDCOMM = 6
IMD_PAUSE = 7
IMD_TRATE = 8
IMD_IOERROR = 9
IMD_ETERMS = ['tstep', 'T', 'Etot', 'Epot', 
              'Evdw', 'Eelec', 'Ebond', 
              'Eangle', 'Edihe', 'Eimpr']

HEADERSIZE = 8
IMDVERSION = 2


def imd_connect(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
    except socket.error:
        #print('Error: host: {}, port: {}'.format(host, port))
        raise
    return s

def imd_readn(s, n):
    buff = b''
    bytes_recd = 0
    while bytes_recd < n:
        chunk = s.recv(min(n - bytes_recd, 2048))
        if len(chunk) == 0:
            raise RuntimeError("socket connection broken")
        buff += chunk
        bytes_recd += len(chunk)
    return buff

def imd_send_header(s, typ, length):
    msg = struct.pack('II', socket.htonl(typ), socket.htonl(length))
    s.sendall(msg)

def imd_disconnect(s):
    imd_send_header(s, IMD_DISCONNECT, 0)
    
def imd_pause(s):
    imd_send_header(s, IMD_PAUSE, 0)

def imd_kill(s):
    try:
        imd_send_header(s, IMD_KILL, 0)
    except socket.error:
        pass

def imd_go(s):
    imd_send_header(s, IMD_GO, 0)

def imd_handshake(s):
    msg = struct.pack('II', socket.htonl(IMD_HANDSHAKE), IMDVERSION)
    s.sendall(msg)

def imd_trate(s, rate):
    imd_send_header(s, IMD_TRATE, int(rate))

def imd_send_mdcomm(s, n_forces, indices, forces):
    imd_send_header(IMD_MDCOMM, n_forces)
    msg = struct.pack('I' * n_forces + 'f' * n_forces * 3, *(indices, forces))
    s.sendall(msg)

def imd_send_energies(s, energies):
    imd_send_header(IMD_ENERGIES, 1)
    msg = struct.pack('Ifffffffff', *[energies[eterm] for eterm in IMD_ETERMS])
    s.sendall(msg)

def imd_send_fcoords(s, n_atoms, coords):
    imd_send_header(IMD_FCOORDS, n_atoms)
    msg = struct.pack('f' * 3 * n_atoms, *coords)
    s.sendall(msg)

def imd_recv_header(s):
    buff = imd_readn(s, HEADERSIZE)
    typ, length = struct.unpack('II', buff)
    typ = socket.ntohl(typ)
    if typ != IMD_HANDSHAKE:
        length = socket.ntohl(length)
    return typ, length

def imd_recv_handshake(s):
    typ, length = imd_recv_header(s)
    if typ != IMD_HANDSHAKE:
        return -1
    if length == IMDVERSION:
        imd_go(s)
        return 0
    length = struct.unpack("<I", struct.pack(">I", length))[0]
    if length == IMDVERSION:
        imd_go(s)
        return 1
    return -1

def imd_recv_mdcomm(s, n_forces):
    imd_readn(s, buff, n_forces * 4 * 4)
    indfor = struct.unpack('I' * n_forces + 'fff' * n_forces, buff)
    indices = indfor[:n_forces]
    forces = indfor[n_forces:]
    return indices, forces

def imd_recv_energies(s):
    buff = imd_readn(s, 40)
    eners = struct.unpack('Ifffffffff', buff)
    energies = {}
    for i in range(len(IMD_ETERMS)): 
        energies[IMD_ETERMS[i]] = eners[i]
    return energies

def imd_recv_fcoords(s, n_atoms):
    buff = imd_readn(s, 12 * n_atoms)
    coords = struct.unpack('fff' * n_atoms, buff)
    return coords

