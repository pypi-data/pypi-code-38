try:
    unicode
except NameError:
    unicode = str 
else:
    unicode = unicode
try:
    bytes 
except NameError:
    bytes = str
else:
    bytes = bytes
try:
    next
except NameError:
    def next( it ):
        return it.next()
else:
    next = next
try:
    file 
except NameError:
    import io
    file_base = io.IOBase
else:
    file_base = file
try:
    long
except NameError:
    long = int 
else:
    long = long 
