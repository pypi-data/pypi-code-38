from . import sources


def create_client(source):
    return sources.available[source]()
