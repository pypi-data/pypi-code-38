from .iterator import iterator

def smart_worker(bucket, prefix, worker_function, args=None):

    nextMarker = None

    results_list = []

    while True:

        results = None

        contents, nextMarker = iterator(bucket, nextMarker, prefix)

        print(f"NextMarker: {nextMarker}")

        if contents != None:
            results = worker_function(contents, args)
            results_list.append(results)
        else:
            break

        # Break out of loop
        if nextMarker == None:
            break

    return results_list
