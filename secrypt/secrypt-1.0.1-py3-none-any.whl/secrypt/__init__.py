#-*-coding:utf8;-*-
class Crypt(object):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890., @#$_&-+()/*\"':;!?~`|={}\\%[]"
    def __init__(self, key="0.0"):
        # props
        self.key = key
        self.char = list(Crypt.chars)
        self.enc1 = list(Crypt.chars)
        self.enc2 = list(Crypt.chars)
        self.reset()
        
    def setKey(self, key):
        self.key = key
        self.reset()
        
    def reset(self):
        self.enc1 = list(Crypt.chars)
        self.enc2 = list(Crypt.chars)
        # work on enc 1
        k1 = int(self.key.split(".")[0])
        self.enc1.extend(self.enc1[:k1])
        del self.enc1[:k1]
        # work on enc 2
        k2 = int(self.key.split(".")[1])
        self.enc2.extend(self.enc2[:k2])
        del self.enc2[:k2]
        
    def flip(self):
        self.enc2.insert(0, self.enc2[-1])
        del self.enc2[-1]
        
    def encrypt(self, value):
        value = list(str(value))
        res = ''
        for char in value:
            if char in self.char:
                key = self.enc1.index(char)
                res_ = self.enc2[key]
                res = res + res_
            else:
                res = res+char
            self.flip()
        self.reset()
        return res
        
    def decrypt(self, value):
        value = list(str(value))
        res = ''
        for char in value:              
            if char in self.char:
                key = self.enc2.index(char)
                res_ = self.enc1[key]
                res = res + res_
            else:
                res = res+char
            self.flip()
        self.reset()
        return res
