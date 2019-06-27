import os

def same_paths(*paths):
    resolved_paths = [os.path.abspath(path) for path in paths]
    first_path, *rest_paths = resolved_paths
    return all(path == first_path for path in rest_paths)
