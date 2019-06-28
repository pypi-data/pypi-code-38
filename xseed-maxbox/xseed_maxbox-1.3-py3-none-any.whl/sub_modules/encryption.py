from itertools import cycle
import base64

def encodeDecodeXOR(message, key):
    return ''.join(chr(ord(c)^ord(k)) for c,k in zip(message, cycle(key)))

# for encoding
# message = input("Enter message to be ciphered: ")
# key = input("Enter key: ")
# XORstring = encodeDecodeXOR(message, key)
# print(XORstring)
# base64encoded = base64.b64encode(XORstring.encode()).decode("utf-8")
# print("encrypted text is: %s" %base64encoded)

# # for decoding
def decode(encodedString, key):
    return encodeDecodeXOR(base64.b64decode(encodedString).decode("utf-8"), key)
    print("decrypted text is: %s" %XORstring)
