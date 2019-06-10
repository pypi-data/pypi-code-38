import numpy as np

def reader(**kwargs):
    assert ('filename' in kwargs.keys()), 'Filename cannot be empty'
    filename = kwargs['filename']

    if not 'allowedChars' in kwargs.keys():
        allowedChars = ['%d' % ii for ii in range(10)]
        allowedChars.extend(['-', '+'])
    else:
        allowedChars = kwargs['allowedChars']

    if not 'datatype' in kwargs.keys():
        datatype = float
    else:
        datatype = kwargs['datatype']

    if not 'delimiter' in kwargs.keys():
        delimiter = ' '
    else:
        delimiter = kwargs['delimiter']

    if not 'skipLines' in kwargs.keys():
        skipLines = 0
    else:
        skipLines = kwargs['skipLines']

    if not 'flatten' in kwargs.keys():
        flatten = 0
    else:
        flatten = kwargs['flatten']

    f = open(filename, 'r')
    data = []
    for kk, l in enumerate(f):
        if kk < skipLines:
            continue
        if l[0] not in allowedChars:
            continue

        tempChars = []
        tempStr = []
        for c in l:
            # Once a newline is reached, saves the vector into the next line of the data Matrix.
            if c == '\n':
                tempStr.append(''.join(tempChars))
                data.append(tempStr)
                break
            # Once a delimiter is hit, the characterArray is changed into a string and the string is put into the vector
            if c == delimiter:
                if tempChars != []:
                    tempStr.append(''.join(tempChars))
                    tempChars = []
                continue
            # reads until hits a delimiter
            elif c != delimiter:
                tempChars.append(c)
                continue

    for ii, d in enumerate(data):
        if d[-1] == '':
            data[ii] = d[:-1]

    if not data[-1]:
        data = data[:-1]

    if not flatten == 0:
        temp = []
        for ii, d in enumerate(data):
            if len(d) == flatten:
                temp.append(d)
        data = temp

    if datatype == complex:
        for ii, l in enumerate(data):
            for kk, d in enumerate(l):
                if '+' in d:
                    realPart = float(d[:d.index('+')])
                    imagPart = float(d[d.index('+'):d.index('i')])
                    l[kk] = realPart + 1j*imagPart
                if '-' in d:
                    realPart = float(d[:d.index('-')])
                    imagPart = float(d[d.index('-')+len('-'):d.index('i')])
                    l[kk] = realPart - 1j*imagPart
            data[ii] = l

    data = np.asarray(data, dtype=datatype)

    return data
