def guaranteed_list( d, *keys ):
    def transform( x ):
        if not x:
            result = []
        elif isinstance( x, list ):
            result = x
        else:
            result = [x]
        return result

    if isinstance( d, dict ):
        for k, v in d.items():
            if k in keys:
                d[ k ] = transform( v )
            guaranteed_list( v, *keys )
    elif isinstance( d, list ):
        for i in d:
            guaranteed_list( i, *keys )
    return d
