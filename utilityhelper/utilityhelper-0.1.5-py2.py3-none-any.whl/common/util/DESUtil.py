#coding:utf-8
from __future__ import (print_function, unicode_literals)
from Crypto.Cipher import DES3, DES

DEBUG_DES = 1

class MyDES(object):
    
    skey = ''
    mkey = ''
       
    @classmethod 
    def encrypt(self, data):
        '''3DES ECB mode.
            
        '''
        D = data   

        '''在明文M后附加0x80，然后在右端填充最少的0x00，使得填充后消息M = (M||80||00||00||…||00)的长度为8的整数倍'''
        D += b'\x80'
        if len(D)%8:
            D += b'\x00' * (8 - len(D)%8)

        cipher = DES3.new(self.skey, DES3.MODE_ECB)
        EData = cipher.encrypt(D)
        return EData
    
    @classmethod
    def decrypt(self, EData):

        cipher = DES3.new(self.skey, DES3.MODE_ECB)
        D = cipher.decrypt(EData)
        return D
    
    @classmethod
    def CalcMAC(self, data):
        D = data + b'\x80'
        if len(D)%8:
            D += b'\x00' * (8 - len(D)%8)
        
        #CBC模式加密
        Ecipher = DES.new(self.mkey[:8], DES.MODE_CBC, IV=b'\x00'*8)
        C = Ecipher.encrypt(D)
        
        #使用最后一块数据计算消息认证码
        Cn = C[-8:]
        Dcipher = DES.new(self.mkey[8:], DES.MODE_ECB)
        Dn = Dcipher.decrypt(Cn)
        
        Ecipher = DES.new(self.mkey[:8], DES.MODE_ECB)
        Mac = Ecipher.encrypt(Dn)

        return Mac