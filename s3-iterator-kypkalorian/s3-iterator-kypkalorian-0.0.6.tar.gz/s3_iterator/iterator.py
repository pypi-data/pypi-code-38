from .list_obj import list_obj, list_obj_marker, list_prefix, list_prefix_marker

import json

def get_next_marker(response):
    if 'NextMarker' in response:
        return response['NextMarker']
    else:
        return None

def get_contents(response):
    if 'Contents' in response:
        return response['Contents']
    else:
        return None

def iterator(bucket, nextMarker=None, prefix=None):

    print("\n")
    print(f"bucket: {bucket}")
    print(f"next: {nextMarker}")
    print(f"prefix: {prefix}")


    response = None

    if nextMarker == None:


        if prefix != None:
            response = list_prefix(bucket, prefix)
        else:
            response = list_obj(bucket)

    else:


        if prefix != None:
            response = list_prefix_marker(bucket, nextMarker, prefix)
        else:
            response = list_obj_marker(bucket, nextMarker)

    print("")

    return get_contents(response), get_next_marker(response)
