# -*- coding:UTF-8 -*-

'''
Created on 2014年11月12日

@author: caifh
'''

import hashlib

def get_file_md5(filepath):
    inst = hashlib.md5()
    with open(filepath, 'rb') as fp:
        while True:
            blk = fp.read(4096) # 4KB per block
            if not blk: 
                break
            
            inst.update(blk)
            
#     print(inst.hexdigest(), filepath)

    return inst.hexdigest()
    

def get_data_md5(data):    
    inst = hashlib.md5(data.encode(encoding='utf-8'))
#     print(inst.hexdigest())  

    return inst.hexdigest()

def get_file_sha1(filepath):
    inst = hashlib.sha1()
    with open(filepath, 'rb') as fp:
        while True:
            blk = fp.read(4096) # 4KB per block
            if not blk: 
                break
            
            inst.update(blk)
            
    return inst.hexdigest()

def get_data_sha1(data):    
    inst = hashlib.sha1(data.encode(encoding='utf-8'))
#     print(inst.hexdigest())  

    return inst.hexdigest()