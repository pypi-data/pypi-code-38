# -*-coding:utf-8-*-
import hashlib


class Verify:

    # md5签名
    def md5Sign(self, prestr):
        prestr = prestr
        md5 = hashlib.md5()
        md5.update(prestr.encode())
        sign = md5.hexdigest()
        return sign

    # md5校验
    def md5Verify(self, prestr, sign):
        md5 = hashlib.md5()
        md5.update(prestr.encode())
        mysign = md5.hexdigest()
        if mysign == sign:
            return True
        else:
            return False
