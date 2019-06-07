def load_data():    
    letters = [['  A    ', ' A A   ', 'AAAAA  ', 'A   A  ', 'A   A  ', ''],
 ['BBBBB  ', 'B   B  ', 'BBBBB  ', 'B   B  ', 'BBBBB  ', ''],
 ['CCCCC  ', 'C      ', 'C      ', 'C      ', 'CCCCC  ', ''],
 ['DDDD   ', 'D   D  ', 'D   D  ', 'D   D  ', 'DDDD   ', ''],
 ['EEEEE  ', 'E      ', 'EEEEE  ', 'E      ', 'EEEEE  ', ''],
 ['FFFFF  ', 'F      ', 'FFFFF  ', 'F      ', 'F      ', ''],
 ['GGGGG  ', 'G      ', 'G  GG  ', 'G   G  ', 'GGGGG  ', ''],
 ['H   H  ', 'H   H  ', 'HHHHH  ', 'H   H  ', 'H   H  ', ''],
 ['IIIII  ', '  I    ', '  I    ', '  I    ', 'IIIII  ', ''],
 ['JJJJJ  ', '  J    ', '  J    ', 'J J    ', 'JJJ    ', ''],
 ['K   K  ', 'K  K   ', 'K K    ', 'K  K   ', 'K   K  ', ''],
 ['L      ', 'L      ', 'L      ', 'L      ', 'LLLLL  ', ''],
 ['M   M  ', 'MM MM  ', 'M M M  ', 'M   M  ', 'M   M  ', ''],
 ['N   N  ', 'NN  N  ', 'N N N  ', 'N  NN  ', 'N   N  ', ''],
 ['OOOOO  ', 'O   O  ', 'O   O  ', 'O   O  ', 'OOOOO  ', ''],
 ['PPPPP  ', 'P   P  ', 'PPPPP  ', 'P      ', 'P      ', ''],
 ['QQQQQ  ', 'Q   Q  ', 'Q   Q  ', 'QQQQQ  ', '    Q  ', ''],
 ['RRRRR  ', 'R   R  ', 'RRRRR  ', 'R R    ', 'R   R  ', ''],
 ['SSSSS  ', 'S      ', 'SSSSS  ', '    S  ', 'SSSSS  ', ''],
 ['TTTTT  ', '  T    ', '  T    ', '  T    ', '  T    ', ''],
 ['U   U  ', 'U   U  ', 'U   U  ', 'U   U  ', 'UUUUU  ', ''],
 ['V   V  ', 'V   V  ', 'V   V  ', ' V V   ', '  V    ', ''],
 ['W   W ', 'W   W ', 'W W W ', 'W W W ', 'WW WW ', ''],
 ['X   X  ', ' X X   ', '  X    ', ' x x   ', 'X   X  ', ''],
 ['Y   Y  ', ' Y Y   ', '  Y    ', '  Y    ', '  Y    ', ''],
 ['ZZZZZ  ', '   Z   ', '  Z    ', ' Z     ', 'ZZZZZ  ', '']]
    d = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25}
    return letters,d
def printbig(st):
    w,d = load_data()
    inp=st
    res=""
    for i in range(5):
        for char in list(inp):
            if (char == " "):
                res+= "\t"
            else:
                res += w[d.get(char)][i]
        res+="\n"
    print(res)
    