def generateKey(string, key):
    key = list(key)
    if len(string) == len(key):
        return (key)
    else:
        for i in range(len(string) -
                       len(key)):
            key.append(key[i % len(key)])
    return ("".join(key))


# def cipherText(string, key):
    # cipher_text = []
    # for i in range(len(string)):
        # x = (ord(string[i]) +
             # ord(key[i])) % 26
        # x += ord('A')
        # cipher_text.append(chr(x))
    # return ("".join(cipher_text))


# def originalText(cipher_text, key):
    # orig_text = []
    # for i in range(len(cipher_text)):
        # x = (ord(cipher_text[i]) -
             # ord(key[i]) + 26) % 26
        # x += ord('A')
        # orig_text.append(chr(x))
    # return ("".join(orig_text))

	
def cipherText(txt='', key=''):
    if not txt:
        print 'Needs text'
        return
    if not key:
        print 'Needs key'
        return

    k_len = len(key)
    k_ints = [ord(i) for i in key]
    txt_ints = [ord(i) for i in txt]
    ret_txt = ''
    for i in range(len(txt_ints)):
        adder = k_ints[i % k_len]

        v = (txt_ints[i] - 32 + adder) % 95

        ret_txt += chr(v + 32)

    print ret_txt
    return ret_txt
	
def originalText(txt='', key=''):
    if not txt:
        print 'Needs text'
        return
    if not key:
        print 'Needs key'
        return
    if typ not in ('d', 'e'):
        print 'Type must be "d" or "e"'
        return

    k_len = len(key)
    k_ints = [ord(i) for i in key]
    txt_ints = [ord(i) for i in txt]
    ret_txt = ''
    for i in range(len(txt_ints)):
        adder = k_ints[i % k_len]
        adder *= -1

        v = (txt_ints[i] - 32 + adder) % 95

        ret_txt += chr(v + 32)

    print ret_txt
    return ret_txt
