'''
Created on 25 apr 2019

@author: Matteo
'''
import asyncio
from . import _LOGGER
from .const import (CD_ADD_AND_CONTINUE_WAITING,CD_RETURN_IMMEDIATELY,CD_CONTINUE_WAITING,CD_ABORT_AND_RETRY)
from .asyncio_udp import open_remote_endpoint
import binascii
from Crypto.Cipher import AES
import random
import time
from _datetime import datetime
from functools import partial
from pybroadlink.asyncio_udp import open_local_endpoint
PORT = 80

def _type2class(devtype):
    if devtype == 0: # SP1
        return None
    elif devtype == 0x2711: # SP2
        return None
    elif devtype == 0x2719 or devtype == 0x7919 or devtype == 0x271a or devtype == 0x791a: # Honeywell SP2
        return None
    elif devtype == 0x2720: # SPMini
        return None
    elif devtype == 0x753e: # SP3
        return None
    elif devtype == 0x7D00: # OEM branded SP3
        return None
    elif devtype == 0x947a or devtype == 0x9479: # SP3S
        return None
    elif devtype == 0x2728: # SPMini2
        return None
    elif devtype == 0x2733 or devtype == 0x273e: # OEM branded SPMini
        return None
    elif devtype >= 0x7530 and devtype <= 0x7918: # OEM branded SPMini2
        return None
    elif devtype == 0x2736: # SPMiniPlus
        return None
    elif devtype == 0x2712: # RM2
        return BroadlinkRM3
    elif devtype == 0x2737: # RM Mini
        return BroadlinkRM3
    elif devtype == 0x273d: # RM Pro Phicomm
        return BroadlinkRM3
    elif devtype == 0x2783: # RM2 Home Plus
        return BroadlinkRM3
    elif devtype == 0x277c: # RM2 Home Plus GDT
        return BroadlinkRM3
    elif devtype == 0x272a: # RM2 Pro Plus
        return BroadlinkRM3
    elif devtype == 0x2787: # RM2 Pro Plus2
        return BroadlinkRM3
    elif devtype == 0x279d: # RM2 Pro Plus3
        return BroadlinkRM3
    elif devtype == 0x27a9: # RM2 Pro Plus_300
        return BroadlinkRM3
    elif devtype == 0x278b: # RM2 Pro Plus BL
        return BroadlinkRM3
    elif devtype == 0x2797: # RM2 Pro Plus HYC
        return BroadlinkRM3
    elif devtype == 0x27a1: # RM2 Pro Plus R1
        return BroadlinkRM3
    elif devtype == 0x27a6: # RM2 Pro PP
        return BroadlinkRM3
    elif devtype == 0x278f: # RM Mini Shate
        return BroadlinkRM3
    elif devtype == 0x2714: # A1
        return None
    elif devtype == 0x4EB5 or devtype == 0x4EF7: # MP1: 0x4eb5, honyar oem mp1: 0x4ef7
        return None
    elif devtype == 0x4EAD: # Hysen controller
        return None
    elif devtype == 0x2722: # S1 (SmartOne Alarm Kit)
        return None
    elif devtype == 0x4E4D: # Dooya DT360E (DOOYA_CURTAIN_V2)
        return None
    else:
        return None

class BroadlinkUDP:
    _local = None
    KEY = b'\x09\x76\x28\x34\x3f\xe9\x9e\x23\x76\x5c\x15\x13\xac\xcf\x8b\x02'
    IV = b'\x56\x2e\x17\x99\x6d\x09\x3d\x28\xdd\xb3\xba\x69\x5a\x2e\x6f\x58'
    ID =  b'\x00\x00\x00\x00'
    def __repr__(self):
        return "%s[%s:%d] %s" % (self.__class__.__name__,*self._hp,BroadlinkUDP.print_mac(self._mac))

    def __init__(self,hp,mac,devtype,timeout=3,**kwargs):
        self._hp = hp
        if isinstance(mac, bytes):
            self._mac = mac
        else:
            mac = mac.replace(':','').replace('-','').replace(' ','')
            self._mac = binascii.unhexlify(mac)
        self._devtype = devtype
        self._timeout = timeout
        self._remote = None
        self._force_auth = False
        self._key = BroadlinkUDP.KEY
        self._iv = BroadlinkUDP.IV
        self._id = BroadlinkUDP.ID
        self._count = random.randrange(0xffff)
        self._local_addr = ''



    async def _protocol(self,generate_packet_fn,check_data_fun,timeout,retry=3,ensure_auth=False,is_broadcast=False,**kwargs):
        out_data = None
        timeout = self._timeout if timeout<=0 else timeout
        rem = None
        newrem = None
        for _ in range(retry):
            try:
                newrem =  await self._init_remote(ensure_auth,**kwargs)
                if newrem:
                    if isinstance(generate_packet_fn, (bytes,bytearray)):
                        data = generate_packet_fn
                    elif rem!=newrem:
                        data = generate_packet_fn()
                        rem = newrem
                    for _ in range(retry):
                        out_data = await self._remote.protocol(data,self._hp,check_data_fun,timeout,1,is_broadcast)
                        if out_data:
                            break
                    break
            except BaseException as ex:
                self.destroy_remote()
                _LOGGER.error("Protocol[%s:%d] error: %s",*self._hp,str(ex))
            except:
                self.destroy_remote()
                _LOGGER.error("Protocol[%s:%d] error",*self._hp)
        #=======================================================================
        # if not out_data:
        #     self.destroy_remote()
        #=======================================================================
        return out_data

    async def _init_remote(self,ensure_auth,**kwargs):
        if not self._remote:
            try:
                self._force_auth = True
                if 'local_addr' not in kwargs:
                    if not len(self._local_addr):
                        remtmp = await open_remote_endpoint(*self._hp)
                        self._local_addr = remtmp.address[0]
                        remtmp.abort()
                    kwargs['local_addr'] = (self._local_addr,0)
                    self._remote = await open_remote_endpoint(*self._hp,**kwargs)
                else:
                    self._remote = await open_local_endpoint(*kwargs['local_addr'],**kwargs)
            except BaseException as ex:
                _LOGGER.error("Open endpoint error %s",str(ex))
                self._remote = None
            except:
                _LOGGER.error("Open endpoint error")
                self._remote = None
        if self._remote and ensure_auth and self._force_auth:
            if not await self.auth():
                _LOGGER.warning("%s:%d auth FAIL",*self._hp)
            else:
                _LOGGER.info("%s:%d auth OK",*self._hp)
                self._force_auth = False
        return self._remote

    def destroy_remote(self):
        if self._remote:
            try:
                self._remote.abort()
            except:
                pass
            self._remote = None
        self._key = BroadlinkUDP.KEY
        self._id = BroadlinkUDP.ID

    @staticmethod
    def print_mac(mac_bytes):
        return binascii.hexlify(mac_bytes).decode('utf-8')

    def _encrypt(self, payload):
        aes = AES.new(self._key, AES.MODE_CBC, self._iv)
        return aes.encrypt(bytes(payload))

    def _decrypt(self, payload):
        aes = AES.new(self._key, AES.MODE_CBC, self._iv)
        return aes.decrypt(bytes(payload))

    def _check_auth_packet(self,data,addr):
        if len(data)>0x38:
            payload = self._decrypt(data[0x38:])
            if payload and len(payload)>=0x14:
                key = payload[0x04:0x14]
                if len(key) % 16 == 0:
                    self._id = payload[0x00:0x04]
                    self._key = key
                    #print("New key",binascii.hexlify(key)," ",self._id)
                    return CD_RETURN_IMMEDIATELY
        return CD_CONTINUE_WAITING

    def _check_generic_packet(self,data,addr):
        #print("CHECK ",data," ",len(data)>0x23," ",(data[0x22] | (data[0x23] << 8)))
        if len(data)>0x23 and (data[0x22] | (data[0x23] << 8))==0:
            return CD_RETURN_IMMEDIATELY
        else:
            self._force_auth = True
            return CD_ABORT_AND_RETRY

    @staticmethod
    def _check_discovery_packet(data,addr):
        if len(data)>=0x40:
            mac = data[0x3a:0x40]
            devtype = data[0x34] | data[0x35] << 8
            return (CD_ADD_AND_CONTINUE_WAITING,{'hp':addr,'mac':mac,'devtype':devtype})
        else:
            return CD_CONTINUE_WAITING

    def _decorate_packet(self,command,payload):
        self._count = (self._count + 1) & 0xffff
        packet = bytearray(0x38)
        packet[0x00] = 0x5a
        packet[0x01] = 0xa5
        packet[0x02] = 0xaa
        packet[0x03] = 0x55
        packet[0x04] = 0x5a
        packet[0x05] = 0xa5
        packet[0x06] = 0xaa
        packet[0x07] = 0x55
        packet[0x24] = 0x2a
        packet[0x25] = 0x27
        packet[0x26] = command
        packet[0x28] = self._count & 0xff
        packet[0x29] = self._count >> 8
        packet[0x2a] = self._mac[0]
        packet[0x2b] = self._mac[1]
        packet[0x2c] = self._mac[2]
        packet[0x2d] = self._mac[3]
        packet[0x2e] = self._mac[4]
        packet[0x2f] = self._mac[5]
        packet[0x30] = self._id[0]
        packet[0x31] = self._id[1]
        packet[0x32] = self._id[2]
        packet[0x33] = self._id[3]

        # pad the payload for AES encryption
        if len(payload)>0:
            numpad=(len(payload)//16+1)*16
            payload=payload.ljust(numpad, b"\x00")

        checksum = 0xbeaf
        for i in range(len(payload)):
            checksum += payload[i]
            checksum = checksum & 0xffff

        payload = self._encrypt(payload)

        packet[0x34] = checksum & 0xff
        packet[0x35] = checksum >> 8

        for i in range(len(payload)):
            packet.append(payload[i])

        checksum = 0xbeaf
        for i in range(len(packet)):
            checksum += packet[i]
            checksum = checksum & 0xffff
        packet[0x20] = checksum & 0xff
        packet[0x21] = checksum >> 8
        return packet

    async def auth(self,timeout = -1,retry = 3):
        if not await self._inner_auth():
            self.destroy_remote()
            return False
        else:
            return True

    async def _inner_auth(self,timeout = -1,retry = 3):
        payload = bytearray(0x50)
        payload[0x04] = 0x31
        payload[0x05] = 0x31
        payload[0x06] = 0x31
        payload[0x07] = 0x31
        payload[0x08] = 0x31
        payload[0x09] = 0x31
        payload[0x0a] = 0x31
        payload[0x0b] = 0x31
        payload[0x0c] = 0x31
        payload[0x0d] = 0x31
        payload[0x0e] = 0x31
        payload[0x0f] = 0x31
        payload[0x10] = 0x31
        payload[0x11] = 0x31
        payload[0x12] = 0x31
        payload[0x1e] = 0x01
        payload[0x2d] = 0x01
        payload[0x30] = ord('T')
        payload[0x31] = ord('e')
        payload[0x32] = ord('s')
        payload[0x33] = ord('t')
        payload[0x34] = ord(' ')
        payload[0x35] = ord(' ')
        payload[0x36] = ord('1')

        return await self._protocol(partial(self._decorate_packet, 0x65, payload),self._check_auth_packet,timeout,retry)

    @staticmethod
    async def discovery(local_ip_address,broadcast_address='255.255.255.255',timeout=5,retry=3):
        fake = BroadlinkUDP((broadcast_address,PORT),b'\x00\x01\x02\x03\x04\x05',0x00,timeout)
        if await fake._init_remote(False,local_addr=(local_ip_address,0),allow_broadcast=True):
            port = fake._remote.address[1]
            address = local_ip_address.split('.')
            timezone = int(time.timezone/-3600)
            packet = bytearray(0x30)
            year = datetime.now().year
            if timezone < 0:
                packet[0x08] = 0xff + timezone - 1
                packet[0x09] = 0xff
                packet[0x0a] = 0xff
                packet[0x0b] = 0xff
            else:
                packet[0x08] = timezone
                packet[0x09] = 0
                packet[0x0a] = 0
                packet[0x0b] = 0
            packet[0x0c] = year & 0xff
            packet[0x0d] = year >> 8
            packet[0x0e] = datetime.now().minute
            packet[0x0f] = datetime.now().hour
            subyear = str(year)[2:]
            packet[0x10] = int(subyear)
            packet[0x11] = datetime.now().isoweekday()
            packet[0x12] = datetime.now().day
            packet[0x13] = datetime.now().month
            packet[0x18] = int(address[0])
            packet[0x19] = int(address[1])
            packet[0x1a] = int(address[2])
            packet[0x1b] = int(address[3])
            packet[0x1c] = port & 0xff
            packet[0x1d] = port >> 8
            packet[0x26] = 6
            checksum = 0xbeaf

            for i in range(len(packet)):
                checksum += packet[i]
            checksum = checksum & 0xffff
            packet[0x20] = checksum & 0xff
            packet[0x21] = checksum >> 8

            out_data = await fake._protocol(packet,
                                  BroadlinkUDP._check_discovery_packet, timeout, retry,ensure_auth=False,is_broadcast=True)
            fake.destroy_remote()
            if out_data:
                hosts = dict()
                for d_a in out_data:
                    dev = d_a[0]
                    keyv = '%s:%d' %  d_a[1]
                    if keyv not in hosts:
                        _LOGGER.info("Discovered device %s", dev)
                        cl = _type2class(dev['devtype'])
                        if cl:
                            hosts[keyv] = cl(**dev)
                return hosts
        return dict()

class BroadlinkRM3(BroadlinkUDP):

    def __init__(self, hp, mac, devtype = 0x2737, timeout=3, **kwargs):
        BroadlinkUDP.__init__(self, hp, mac, devtype, timeout=timeout, **kwargs)

    async def emit_ir(self,databytes,timeout=-1,retry=3):
        payload = bytearray([0x02, 0x00, 0x00, 0x00])
        payload += databytes
        rv = await self._protocol(partial(self._decorate_packet, 0x6a, payload),self._check_generic_packet,timeout,retry,True)
        if rv:
            return rv[0]
        else:
            return None

    async def enter_learning_mode(self,timeout=-1,retry=3):
        payload = bytearray(16)
        payload[0] = 3
        return await self._protocol(partial(self._decorate_packet, 0x6a, payload),self._check_generic_packet,timeout,retry,True)

    def _check_learn_ir_get_packet(self,data,addr):
        if len(data)>0x38:
            err = data[0x22] | (data[0x23] << 8)
            if err == 0:
                payload = self._decrypt(data[0x38:])
                return CD_RETURN_IMMEDIATELY,payload[0x04:]
            else:
                self._force_auth = True
        return CD_CONTINUE_WAITING

    async def get_learned_key(self,timeout=30):
        tim = max([5,timeout])
        payload = bytearray(16)
        payload[0] = 4
        packet = self._decorate_packet(0x6a, payload)
        timeout = time.time()
        while time.time()-timeout<tim:
            await asyncio.sleep(5)
            rv = await self._protocol(packet,self._check_learn_ir_get_packet,self._timeout,1,True)
            if rv:
                return rv[0]
        return None

if __name__ == '__main__': # pragma: no cover
    import sys
    import logging
    import traceback
    from base64 import b64decode
    async def testFake(n):
        for i in range(n):
            _LOGGER.debug("Counter is %d",i)
            await asyncio.sleep(1)
    async def discovery_test(*args):
        rv = await BroadlinkUDP.discovery(local_ip_address=args[2],timeout=int(args[3]))
        if rv:
            _LOGGER.info("Discovery OK %s",rv)
        else:
            _LOGGER.warning("Discovery failed")

    async def emit_test(*args):
        import re
        mo = re.search('^[a-fA-F0-9]+$', args[4])
        if mo:
            payload = binascii.unhexlify(args[4])
        else:
            payload = b64decode(args[4])
        a = BroadlinkRM3((args[2],PORT),args[3])
        rv = await a.emit_ir(payload,retry=1)
        if rv:
            _LOGGER.info("Emit OK %s",binascii.hexlify(rv).decode('utf-8'))
        else:
            _LOGGER.warning("Emit failed")
        a.destroy_remote()
    async def learn_test(*args):
        a = BroadlinkRM3((args[2],PORT),args[3])
        rv = await a.enter_learning_mode()
        if rv:
            _LOGGER.info("Entered learning mode (%s): please press key",rv)
            rv = await a.get_learned_key(30)
            if rv:
                _LOGGER.info("Obtained %s",binascii.hexlify(rv).decode('utf-8'))
            else:
                _LOGGER.warning("No key pressed")
        else:
            _LOGGER.warning("Enter learning failed")
        a.destroy_remote()
    _LOGGER.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(testFake(150))
        if sys.argv[1]=="learn":
            loop.run_until_complete(learn_test(*sys.argv))
        elif sys.argv[1]=="discovery":
            loop.run_until_complete(discovery_test(*sys.argv))
        else:
        #loop.run_until_complete(emit_test('00000000a801000000000000000098018e11951127029b0625029906270299062702380227023a0225023802270238022d023202270299062702990627029806270238022702380227023802270238022802370227023802270238022702980627023802240245021c02380227023802270238022702980627029c0623023802270298062702990627029b062502990627029906270220b7a1119d11270299062702990628029b06250238022702380227023802270238022702380227029906270299062702990627023802270238022a0234022702380227023802260238022702380226029a06260238022602380226023802260241021e02380227029b0624029906270238022702980627029b0625029906270299062702990629021db79f11a2112502990627029b0625029906270238022702380227023802270238022a02350227029906270299062702990628023702260238022702380227023802270238022702380226023b02240299062702380226023802270238022602380227023c0223029906270299062702380226029b062402990627029906270299062802980627020000'))
            loop.run_until_complete(emit_test(*sys.argv))
        #loop.run_until_complete(learn_test())
    except BaseException as ex:
        _LOGGER.error("Test error %s",str(ex))
        traceback.print_exc()
    except:
        _LOGGER.error("Test error")
        traceback.print_exc()
    finally:
        loop.close()
