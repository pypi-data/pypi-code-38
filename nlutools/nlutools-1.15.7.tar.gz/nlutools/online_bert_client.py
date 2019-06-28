#from typing import List
try:
    from bert_serving.client import BertClient
except Exception:
    print('Please install BertClient using following commands: "pip install bert-serving-client"')


class bert_vector(object):

    def __init__(self, ip='192.168.7.221'):
       # try:
       #     self.bc_char = BertClient(ip=ip, port=1246, port_out=5551,check_version=False)
       #     self.bc_sent = BertClient(ip=ip, port=1247, port_out=5552,check_version=False)
       # except Exception as e:
       #     print(e)
        pass
    
    def buildConnection(self, ip='192.168.7.221'):
        try:
            self.bc_char = BertClient(ip=ip, port=1246, port_out=5551,check_version=False)
        except Exception as e:
            print('Error!','failed to connect bert service with char client,detail info followed as: ',e)
        try:
            self.bc_sent = BertClient(ip=ip, port=1247, port_out=5552,check_version=False)
        except Exception as e:
            print('Error!','failed to connect bert service with sentence client,detail info followed as: ',e)
    
    def parse(self, texts, mode):
        if mode == 'char':
            return self.bc_char.encode(texts)
        elif mode == 'sent':
            return self.bc_sent.encode(texts)
        
    def close(self,mode):
        if mode == 'char':
            self.bc_char.close()
        elif mode == 'sent':
            self.bc_sent.close()

