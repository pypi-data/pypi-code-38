import sys

def get_site_packages_path():
    """"Returns the first sys.path 'site-packages' or 'dist-packages' match."""
    for path in sys.path: 
        if 'site-packages' in path or 'dist-packages' in path: 
            new_path = path + os_sep + 'mediabyte'
            return(new_path) 

def get_os_file_separator():
    """Returns OS-dependent file separator character (Windows or other)."""
    if platform == 'win32':
        os_sep = '\\'
    else:
        os_sep = '/'
    return(os_sep)


# hard-coded canonical package version number

version_number = 'v0.8.6.8'


# constants for use in modules

platform = sys.platform
os_sep = get_os_file_separator()
package_path = get_site_packages_path()
srt_folder_path = package_path + os_sep + 'srt'
hash_dict_path = package_path + os_sep + 'files' + os_sep + 'hash_dict.json'



