from os.path import join, curdir

project_path = curdir

def set_project_path(name):
    global project_path
    project_path = join(curdir, name)

def get_project_path():
    return project_path

def get_mekpy_path():
    return join(get_project_path(), 'mek.py')

def get_gitignore_path():
    return join(get_project_path(), '.gitignore')

def get_src_path():
    return join(get_project_path(), 'src')

def get_test_path():
    return join(get_project_path(), 'tests')

def get_includes_path():
    return join(get_project_path(), 'includes')

def get_target_path():
    return join(get_project_path(), 'target')

def get_cache_path():
    return join(get_target_path(), 'cache')

def get_target_debug_path():
    return join(get_target_path(), 'debug')

def get_target_release_path():
    return join(get_target_path(), 'release')

def get_main_path(main):
    return join(get_src_path(), main)
    