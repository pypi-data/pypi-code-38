def resize( w, h, dw, dh ):
    if w > dw:
        h = int( max( h * dw / w, 1 ) )
        w = int( dw )
    if h > dh:
        w = int( max( w * dh / h, 1 ) )
        h = int( dh )
    return w, h
