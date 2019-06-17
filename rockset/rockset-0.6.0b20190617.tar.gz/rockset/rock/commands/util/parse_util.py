def parse_collection_path(path):
    components = path.split(".")
    name = components[-1]
    if len(components) == 1:
        workspace = 'commons'
    else:
        workspace = '.'.join(components[:-1])
    return workspace, name

