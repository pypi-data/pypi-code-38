backend_factory = None

def set_backend(bf):
    global backend_factory
    backend_factory = bf

def get_backend():
    return backend_factory()
