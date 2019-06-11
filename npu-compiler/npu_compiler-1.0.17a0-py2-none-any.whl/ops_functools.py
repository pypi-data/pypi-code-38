#coding: utf-8

from six import byte2int

def xxd(binary_data):
    output = ""
    for i, _ in enumerate(binary_data):
        if i % 10 == 0:
            output += "\n\t"
        output += "0x%02x, " % byte2int(binary_data[i:i+1])
    return output

