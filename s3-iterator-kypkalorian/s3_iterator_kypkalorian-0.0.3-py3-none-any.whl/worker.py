from .iterator import iterator

def worker(bucket, prefix, function):

    nextMarker = None

    while True:

        contents, nextMarker = iterator(bucket, nextMarker, prefix)

        if contents != None:
            function(contents)
            pass
        else:
            break

        # Break out of loop
        if nextMarker == None:
            break


if __name__ == '__main__':


    worker("com.vivintsolar.devops", "temp_testing_folder", function )
