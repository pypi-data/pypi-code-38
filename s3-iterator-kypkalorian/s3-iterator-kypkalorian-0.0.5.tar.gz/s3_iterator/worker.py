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


if __name__ == '__main__':


    worker("com.vivintsolar.devops", "temp_testing_folder", function )
