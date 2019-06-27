from .iterator import iterator

def worker(bucket, prefix, function, args=None):

    nextMarker = None

    while True:

        contents, nextMarker = iterator(bucket, nextMarker, prefix)

        if contents != None:
            function(contents, args)
            pass
        else:
            break

        # Break out of loop
        if nextMarker == None:
            break
