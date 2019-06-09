'''
version: 0.1.2
date: 19:51 09.06.2019
'''
import os
import sys

def script_path():
    '''change current path to script one'''
    path = os.path.realpath(os.path.dirname(sys.argv[0]))
    os.chdir(path)
    return path
    
    
def simple_read(file_name):
    '''simple_read data from specified file_name'''
    with open(file_name, "r", encoding="utf-8") as file:
        file_content = file.read().splitlines()
    return file_content
    
    
def justify(content, grid=True, frame=False, enumerator=False, header=False, topbar='', newline='\n', delimiter=';', justsize=4):
    '''
    convert text to justified
    parameters:
        content - text with newlines and delimiters, to be converted
                  from version 0.1.2 it also can be list(tuple) of lists(tuples)
        grid - True/False value, grid inside; default is True
        frame - True/False value, frame around; default is False
        enumerator - True/False value, will add enumerator column on the left
        header - True/False value, will extract first row from content as header
        topbar - str value. Topbar will be added on the top
        newline - newline symbol; default is '\\n'
        delimiter - delimiter symbol; default is ';'
        justsize - justify size; default is 4
        
    justify(content, grid=True, frame=False, newline='\\n', delimiter=';', justsize=4)    
    '''
    
    
    # ****************** define type of content ******************
    listType = False
    if (type(content) is str):
        if not content.strip():
            return ''
        else:
            pass
    elif type(content) in (list, tuple):
        listType = all([True if type(item) in (list, tuple) else False for item in content])
        if listType:
            pass
        else:
            return ''
    else:
        return ''
        
        
    # ****************** create list content ******************
    if not listType:
        content = content.split(newline)
        content = [item.strip().split(delimiter) for item in content if item.strip()]
    else:
        content = [[str(item).strip() for item in row] for row in content]
    maxRow = len(max(content, key=len))
    content = [item + [""]*(maxRow-len(item)) for item in content]
    
    
    # ****************** extract header from content ******************
    if header:
        if enumerator:
            headerValue = ['No.'] + content[0]
        else:
            headerValue = content[0]
        content = content[1:]
        
        
    # ****************** add enumerator ******************
    if enumerator:
        rowsNumber = len(str(len(content)))
        content = [[str(key+1).zfill(rowsNumber)] + row for key, row in enumerate(content)]
        
        
    # ****************** append header after enumeration ******************
    if header:
        content.insert(0, headerValue)
        
        
    # ****************** create transposed ******************
    transposed = list(map(list, zip(*content)))
    
    
    # ****************** down from here need to be cleaned, if its possible :) ******************
    #signs
    if grid:
        horSign = '|'
    else:
        horSign = ' '
    vertSign = ' '
    lineLen = [max([len(part) for part in item]) for item in transposed]
    
    # 1st column to the left
    # justifiedParts = [[(' '*1 + part).ljust(lineLen[key]+justsize, vertSign) if not key else part.center(lineLen[key]+justsize, vertSign) for key, part in enumerate(item)] for item in content]
    
    # justify all columns in the same way
    justifiedParts = [[part.center(lineLen[key]+justsize, vertSign) for key, part in enumerate(item)] for item in content]
    content = [horSign.join(item) for item in justifiedParts]
    
    line = '+'.join(["-"*len(item) for item in justifiedParts[0]])      # with '+' in the cross
    # line = "-"*len(content[0])                                          # without '+'
    if frame:
        # edgeLine = line.join(['+']*2)                                                       # with crosses
        edgeLine = '-'.join(["-"*len(item) for item in justifiedParts[0]]).join(['+']*2)    # without crosses
        line = line.join(['|']*2)
        content = [item.join(['|']*2) for item in content]
        
    line = line.join(['\n']*2)
    
    if grid:
        out = line.join(content)
    else:
        out = "\n".join(content)
        
    if frame:
        out = '\n'.join([edgeLine, out, edgeLine])
        
        
    # ****************** add topbar ******************
    if topbar:
        contentWidth = out.find('\n')
        if contentWidth > 2:
            line = '+' + "-"*(contentWidth-2) + '+'
            sentence = '|' + topbar[:contentWidth-2].upper().center(contentWidth-2, ' ') + '|'
            if frame:
                strTopbar= '\n'.join([line, sentence])
            else:
                strTopbar = '\n'.join([line, sentence, line])
            out = strTopbar + '\n' + out
    return out
    
    
def example():
    data = 'SOME;THING;HERE;AND;THERE;NOW\nthis;is;very;line;there\nthis;is;not now;is;line;the end\nthis;is;;line\nthis;;here;line;thing;end\nthis;is;not now;is;line;the end\nthis;is;;line\nthis;;here;line;thing;end\nthsdis;is;not now;is;line;the end\nthis;is;;line\nthis;;here;line;thing;end\nthis;is;not now;is;line;the end\nthis;is;;line\nthis;;here;line;thing;end'
    # data =  'THIS;IS;ME\nsome;thing;there'
    # data =  [(1, 2, 'sdsd', {'ds':42}), [], [1,23,4], (1,), (2,2)]
    someSize = 10
    clear = justify(data, grid=False, frame=False, justsize=someSize)
    withFrame = justify(data, grid=False, frame=True, justsize=someSize)
    withGrid = justify(data, grid=True, frame=False, justsize=someSize)
    full = justify(data, grid=True, frame=True, justsize=someSize)
    topbar = justify(data, grid=True, frame=True, enumerator=True, header=True, topbar='something', justsize=someSize)
    
    print("String data:\n\n{}\n\n".format(data))
    print("Justified clear:\n\n{}\n\n".format(clear))
    print("Justified with frame:\n\n{}\n\n".format(withFrame))
    print("Justified with grid:\n\n{}\n\n".format(withGrid))
    print("Justified full:\n\n{}\n\n".format(full))
    print("Justified full, with topbar, header, and enumerator:\n\n{}\n\n".format(topbar))
    return True
    
    
if __name__ == "__main__":
    pass
    # path = script_path()
    # args = sys.argv[1:]
    example()
    
''' 
todo:
    -add delimiter option, for now: ';' +
    -add newline sign, for now: '\n'    +
    -add grid as option                 +
    -think of justify to center or left
    -clean up?
    
from 0.1.2:
    -justfying list of lists(tuples)    (+)
    -topbar as parameters               (+)
    -enumerator as parameter            (+)
    -header as parameter                (+)
    
'''
