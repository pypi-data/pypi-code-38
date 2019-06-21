from pkg_resources import resource_listdir, resource_filename

def list_notebooks():
    x = resource_listdir("jrpyml","notebooks/")
    return x

def get_path(name):
    path = resource_filename("jrpyml","notebooks/")
    return(path + name)
