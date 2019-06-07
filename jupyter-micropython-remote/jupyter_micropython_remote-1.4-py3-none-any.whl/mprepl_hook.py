try:
    import uos, uio as io, gc, select, ustruct as struct, micropython
    gc.collect()
except ImportError:
    import io, os as uos
    gc = None


class RemoteCommand:
    CMD_EXIT = 0
    CMD_STAT = 1
    CMD_ILISTDIR_START = 2
    CMD_ILISTDIR_NEXT = 3
    CMD_OPEN = 4
    CMD_CLOSE = 5
    CMD_READ = 6
    CMD_READLINE = 7
    CMD_WRITE = 8
    CMD_SEEK = 9
    CMD_HASH = 10
    CMD_IOCTL = 11

    use_second_port = False

    def __init__(self):
        try:
            import pyb
            self.write = pyb.USB_VCP().send

            if self.use_second_port:
                self.fin = pyb.USB_VCP(1)
            else:
                self.fin = pyb.USB_VCP()
            self.can_poll = True
        except:
            import sys
            self.write = sys.stdout.buffer.write
            self.fin = sys.stdin.buffer
            # TODO sys.stdio doesn't support polling
            self.can_poll = False

    def poll_in(self):
        if self.can_poll:
            res = select.select([self.fin], [], [], 1000)
            if not res[0]:
                raise Exception('timeout waiting for remote response')

    def rd(self, n):
        # implement reading with a timeout in case other side disappears
        self.poll_in()
        return self.fin.read(n)

    def rdinto(self, buf):
        # implement reading with a timeout in case other side disappears
        self.poll_in()
        return self.fin.readinto(buf)

    def begin(self, type):
        micropython.kbd_intr(-1)
        try:
            while self.fin.any():
                self.fin.read()
        except AttributeError:
            pass
        self.write(bytearray([0x18, type]))

    def end(self):
        micropython.kbd_intr(3)

    def rd_uint32(self):
        return struct.unpack('<I', self.rd(4))[0]

    def wr_uint32(self, i):
        self.write(struct.pack('<I', i))

    def rd_uint64(self):
        return struct.unpack('<Q', self.rd(8))[0]

    def wr_uint64(self, i):
        self.write(struct.pack('<Q', i))

    def rd_int32(self):
        return struct.unpack('<i', self.rd(4))[0]

    def wr_int32(self, i):
        self.write(struct.pack('<i', i))

    def rd_bytes(self):
        n = struct.unpack('<I', self.rd(4))[0]
        buf = bytearray(n)
        mv = memoryview(buf)
        r = 0
        while r < n:
            rd = self.rdinto(mv[r:])
            if not rd: break
            r += rd
        return buf

    def rd_bytes_into(self, buf):
        n = struct.unpack('<I', self.rd(4))[0]
        mv = memoryview(buf)
        r = 0
        while r < n:
            rd = self.rdinto(mv[r:])
            if not rd: break
            r += rd
        return r

    def wr_bytes(self, b):
        self.write(struct.pack('<I', len(b)))
        written = 0
        mv = memoryview(b)
        while written < len(b):
            w = self.write(mv[written:])
            if not w:
                break
            written += w
        return written

    def rd_str(self):
        n = self.rd(1)[0]
        if n == 0:
            return ''
        else:
            return str(self.rd(n), 'utf8')

    def wr_str(self, s):
        b = bytes(s, 'utf8')
        l = len(b)
        assert l <= 255
        self.write(bytearray([l]) + b)


class RemoteFile(io.IOBase):
    def __init__(self, cmd, fd, is_text):
        self.cmd = cmd
        self.fd = fd
        self.is_text = is_text

    def ioctl(self, request, arg):
        self.cmd.begin(RemoteCommand.CMD_IOCTL)
        self.cmd.wr_int32(self.fd)
        self.cmd.wr_int32(request)
        self.cmd.wr_int32(arg)
        n = self.cmd.rd_int32()
        self.cmd.end()
        return n

    def close(self):
        if self.fd is None:
            return
        self.cmd.begin(RemoteCommand.CMD_CLOSE)
        self.cmd.wr_int32(self.fd)
        self.cmd.end()
        self.fd = None

    def read(self, n):
        self.cmd.begin(RemoteCommand.CMD_READ)
        self.cmd.wr_int32(self.fd)
        self.cmd.wr_int32(n)
        data = self.cmd.rd_bytes()
        if self.is_text:
            data = str(data, 'utf8')
        self.cmd.end()
        return data

    def readinto(self, buf):
        self.cmd.begin(RemoteCommand.CMD_READ)
        self.cmd.wr_int32(self.fd)
        self.cmd.wr_int32(len(buf))
        n = self.cmd.rd_bytes_into(buf)
        self.cmd.end()
        return n

    def readline(self):
        self.cmd.begin(RemoteCommand.CMD_READLINE)
        self.cmd.wr_int32(self.fd)
        data = self.cmd.rd_bytes()
        if self.is_text:
            data = str(data, 'utf8')
        self.cmd.end()
        return data

    def write(self, buf):
        self.cmd.begin(RemoteCommand.CMD_WRITE)
        self.cmd.wr_int32(self.fd)
        self.cmd.wr_bytes(buf)
        n = self.cmd.rd_int32()
        self.cmd.end()
        return n

    def seek(self, n):
        self.cmd.begin(RemoteCommand.CMD_SEEK)
        self.cmd.wr_int32(self.fd)
        self.cmd.wr_int32(n)
        n = self.cmd.rd_int32()
        self.cmd.end()
        return n

    def sha256(self):
        self.cmd.begin(RemoteCommand.CMD_HASH)
        self.cmd.wr_int32(self.fd)
        data = self.cmd.rd_bytes()
        self.cmd.end()
        return data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class RemoteFS:
    def __init__(self, use_second_port):
        RemoteCommand.use_second_port = use_second_port
        uos.mount(self, '/remote')
        self.path = '/'

    def umount(self):
        pass

    def mount(self, readonly, mkfs):
        self.cmd = RemoteCommand()
        self.readonly = readonly

    def chdir(self, path):
        if path.startswith('/'):
            self.path = path
        else:
            self.path += path
        if not self.path.endswith('/'):
            self.path += '/'

    def getcwd(self):
        return self.path

    def stat(self, path):
        self.cmd.begin(RemoteCommand.CMD_STAT)
        self.cmd.wr_str(self.path + path)
        res = self.cmd.rd_int32()
        if res < 0:
            raise OSError(-res)
        return tuple(self.cmd.rd_uint64() for _ in range(10))

    def ilistdir(self, path):
        self.cmd.begin(RemoteCommand.CMD_ILISTDIR_START)
        self.cmd.wr_str(self.path + path)
        self.cmd.end()

        def ilistdir_next():
            while True:
                self.cmd.begin(RemoteCommand.CMD_ILISTDIR_NEXT)
                name = self.cmd.rd_str()
                if name:
                    type = self.cmd.rd_uint32()
                    inode = self.cmd.rd_uint64()
                    self.cmd.end()
                    yield (name, type, inode)
                else:
                    self.cmd.end()
                    break

        return ilistdir_next()

    def open(self, path, mode):
        self.cmd.begin(RemoteCommand.CMD_OPEN)
        self.cmd.wr_str(self.path + path)
        self.cmd.wr_str(mode)
        fd = self.cmd.rd_int32()
        self.cmd.end()
        if fd < 0:
            raise OSError(-fd)
        return RemoteFile(self.cmd, fd, mode.find('b') == -1)


def exit(code=0):
    cmd = RemoteCommand()
    cmd.begin(RemoteCommand.CMD_EXIT)
    cmd.wr_int32(code)
    cmd.end()


def _reset(delay):
    import utime
    import machine
    print("restarting...")
    utime.sleep(delay)
    uos.umount('/remote')
    uos.sync()
    machine.reset()


def reset(code=0):
    exit(code)
    micropython.schedule(_reset, 1)

if gc:
    gc.collect()
