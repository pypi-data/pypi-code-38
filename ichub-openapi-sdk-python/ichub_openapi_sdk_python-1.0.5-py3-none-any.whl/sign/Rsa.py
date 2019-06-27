# -*-coding:utf-8-*-
import rsa
import base64


class Verify:

    def __init__(self, public_key='', private_key=''):
        self.public_key = public_key
        self.private_key = private_key
        return

    # 私钥验签
    def privateRsaVerify(self, prestr, sign):
        private_key = open(self.private_key, 'r').read()
        result = self.rsa_decrypt(sign, private_key)

        if result and result == prestr:
            return True
        else:
            return False

    # 公钥获取签名
    def publicSign(self, content):
        public_key = open(self.public_key, 'r').read()
        return self.rsa_encrypt(content, public_key)

    # 根据签名获取签名字符串
    def signStr(self, sign):
        private_key = open(self.private_key, 'r').read()
        result = self.rsa_decrypt(sign, private_key)
        return result

    # 根据签名获取签名字典
    def signArr(self, sign):
        private_key = open(self.private_key, 'r').read()
        result = self.rsa_decrypt(sign, private_key)
        res = {}
        if result:
            arr = result.split('&')
            for index, value in enumerate(arr):
                tmp = value.split('=')
                if len(tmp) == 2:
                    res[tmp[0]] = tmp[1]
        return res

    # 公钥加密
    def rsa_encrypt(self, prestr, public_key):
        _p = rsa.PublicKey.load_pkcs1_openssl_pem(public_key)
        prestr = prestr.encode('utf-8', 'ignore')
        # 1024bit key
        default_encrypt_length = 117  # 能够加密的最大字符串长度
        len_content = len(prestr)  # 当前需要加密字符串的长度
        if len_content < default_encrypt_length:
            return base64.encodebytes(rsa.encrypt(prestr, _p)).decode().replace('\n', '')
        offset = 0
        params = []  # 最后拼接的签名串
        while len_content - offset > 0:
            if len_content - offset > default_encrypt_length:
                params.append(rsa.encrypt(prestr[offset:offset + default_encrypt_length], _p))
            else:
                params.append(rsa.encrypt(prestr[offset:], _p))
            offset += default_encrypt_length
        params = b''.join(params)
        return base64.b64encode(params).decode()

    # 私钥解密
    def rsa_decrypt(self, sign_str, private_key):
        _pri = rsa.PrivateKey.load_pkcs1(private_key)
        sign_str = base64.decodebytes(sign_str.encode())
        # 1024bit key
        default_length = 128
        len_content = len(sign_str)
        if len_content < default_length:
            return rsa.decrypt(sign_str, _pri)
        offset = 0
        params = ''
        while len_content - offset > 0:
            if len_content - offset > default_length:
                params += rsa.decrypt(sign_str[offset: offset + default_length], _pri).decode()
            else:
                params += rsa.decrypt(sign_str[offset:], _pri).decode()
            offset += default_length
        return params
