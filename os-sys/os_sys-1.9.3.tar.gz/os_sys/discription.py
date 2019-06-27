def code(txt):
    b = txt
    d = {}
    for c in (65, 97):
        for i in range(26):
            d[chr(i+c)] = chr((i+13) % 26 + c)

    return "".join([d.get(c, c) for c in b])
def more_input():
    init = input()
    mystr = str()
    while not init == 'None':
        mystr = mystr + (str(init)) + '
'
        init = input()
    return mystr


