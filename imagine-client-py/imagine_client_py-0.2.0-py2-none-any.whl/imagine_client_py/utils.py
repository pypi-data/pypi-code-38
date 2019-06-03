
def normalize_metadata_headers(metadata):
    """
    Normaize the Imagine metadata request headers.
    :param metadata: Dictionary object containing the Imagine metadata
    :return: Dict
    """

    metadata_headers = {}
    items = metadata.items()

    for kvp in items:
        key = kvp[0]
        value = kvp[1]
        lower_case_key = key.lower()
        if lower_case_key.startswith('x-imagine-meta-'):
            metadata_headers[lower_case_key] = value
        else:
            new_key = "x-imagine-meta-{0}".format(lower_case_key)
            metadata_headers[new_key] = value
    
    return metadata_headers
