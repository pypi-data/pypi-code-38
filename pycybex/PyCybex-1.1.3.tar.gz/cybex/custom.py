MAGIC_NUM = 'ca1be4'
def convert_to_hex(data):
    to_hex = '0123456789abcdef'
    ret = [MAGIC_NUM]
    for c in data:
        ret.append(to_hex[ord(c) >> 4])
        ret.append(to_hex[ord(c) & 0xf])
    return str(''.join(ret))

def convert_from_hex(data):
    if len(data) < len(MAGIC_NUM) or data[:len(MAGIC_NUM)] != MAGIC_NUM:
        raise ValueError('This str is not converted by this tool')
    
    if len(data) % 2 != 0:
        raise ValueError('String length can not be odd')

    return ''.join([
        chr((int(data[i], 16) << 4) | (int(data[i + 1], 16)))
        for i in range(len(MAGIC_NUM),len(data),2)])

def run_test():
    s = 'this is a sentence which is verrrrrrrrrrrry long'
    h = convert_to_hex(s)
    print(h)
    ss = convert_from_hex(h)
    print(ss)

if __name__ == '__main__':
    run_test()
