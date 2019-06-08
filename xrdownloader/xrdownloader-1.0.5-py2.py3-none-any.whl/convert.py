from __future__ import division
try:
 import sys
except (ImportError,Exception) as e:
 print(e)
 quit()

def convert_byte(byte):
    if byte < 0:
        print("[!] Cant download an empty file->Exiting...")
        quit()

    block_size = 1000
    byte = float(byte)
    unit = 'B'

    if (byte / block_size) >= 1:
        byte /= block_size
        unit = 'KB'

    if (byte / block_size) >= 1:
        byte /= block_size
        unit = 'MB'

    if (byte / block_size) >= 1:
        byte /= block_size
        unit = 'GB'

    if (byte / block_size) >= 1:
        byte /= block_size
        unit = 'TB'

    byte = round(byte, 1)
    return [str(byte) + '' + unit,unit]

if __name__ == '__main__':
   sys.exit()
