import os
__all__ = ['find_packages', 'setup']
def all_dict(dictory, ex=False, exceptions=None, file_types=None, maps=True, files=False, print_data=False):
    import os
    data = []
    string_data = ''
    e = exceptions
    if 'list' in str(type(e)) or e == None:
        pass
    else:
        raise TypeError('expected a list but got a %s' % type(e))
    e = file_types
    if 'list' in str(type(e)) or e == None:
        pass
    else:
        raise TypeError('expected a list but got a %s' % type(e))
    
    print_ = False
    
    for dirname, dirnames, filenames in os.walk(dictory):
        # print path to all subdirectories first.
        if maps:
            for subdirname in dirnames:
                dat = os.path.join(dirname, subdirname)
                data.append(dat)
                string_data = string_data + '\n' + dat
                if print_:
                    print(dat)

        # print path to all filenames.
        if files:
            for filename in filenames:
                s = False
                fname_path = filename
                file = fname_path.split('.')
                no = int(len(file) - 1)
                file_type = file[no]
                if not e == None:
                    for b in range(0, len(e)):
                        if e[b] == file_type:
                            s = True
                            
                if e == None:
                    s = True
                if s:
                    s = False   
                            
                    dat = os.path.join(dirname, filename)
                    data.append(dat)
                    string_data = string_data + '\n' + dat
                    if print_:
                        
                        print(dat)
        
        

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if not exceptions == None:
            
            for ip in range(0, int(len(exceptions))):
                exception = exceptions[ip]
                
                if exception in dirnames:
                    # don't go into any .git directories.
                    dirnames.remove(exception)
                elif exception in filename and data:
                    data.remove(exception)

    
    return [data, string_data]
import psutil
def process_exists(name):
    i = psutil.pids()
    for a in i:
        try:
            str(psutil.Process().name)
            if str(psutil.Process().name()) == name:
                
                return True
        except:
            pass
    return False
def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode() # uses 'utf-8' for encoding
    else:
        value = bytes_or_str
    return value # Instance of bytes


def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode() # uses 'utf-8' for decoding
    else:
        value = bytes_or_str
    return value # Instance of str
def find_packages(path, *except_paths):
    """auto packages finder, except+paths: the names of the paths you dont want"""
    package = all_dict(path, False, list(except_paths), None, maps=False, files=True)[0]
    return package
def return_file_data(packages, path):
    import tqdm
    print('building...')
    bar = tqdm.tqdm(range(0, len(packages)))

    mystr = ''
    for i in bar:
        try:
            with open(packages[i], mode='rb') as fh:
                try:
                    type(print)
                except Exception:
                    pass
                else:
                    try:
                        e = fh.read()
                        
                    except Exception:
                        pass
                    else:
                        mystr = mystr + '##########' + str(packages[i]).replace(path, '') + '>>>>>>>>>>>>>>>' + str(e).replace('\\n', '\n') + '\n'
        except Exception as ex:
            with open(packages[i], mode='rb') as fh:
                try:
                    print('building file: %s, data: %s' % (packages[i], fh))
                except Exception:
                    pass
                else:
                    try:
                        e = fh.read()
                        
                    except Exception:
                        pass
                    else:
                        mystr = mystr + '##########' + str(packages[i]).replace(path, '') + '>>>>>>>>>>>>>>>' + str(e).replace('\\n', '\n') + '\n'
    bar.close()
    return mystr
def write_info(path, data):
    file = os.path.join(path, str(data['name'] + '.info'))
    w = open(file, 'w+')
    for i in range(0, len(data)):
        w.write(list(data)[i] + '=' + str(data[list(data)[i]]) + '\n')
    w.close()
def write_packages(data, name, path, rpath):
    import random
    lijst = list()
    data = data.replace(rpath, str(name + '\\'))
    for i in range(random.randint(10, 50)):
        lijst.append(str(random.randint(0, 9)))
                     
    file = os.path.join(path, str(name + '.py_install'))
    with open(file, 'wb') as fh:
        fh.write(to_bytes(data))
def write_packages_data(data, name, path, rpath):
    import random
    lijst = list()
    print('writing data...')
    data = data.replace(rpath, str(name + '\\'))
    for i in range(random.randint(10, 50)):
        lijst.append(random.randint(0, 9))
                     
    file = os.path.join(path + str(name + '-' + '.py_data'))
    with open(file, 'wb') as fh:
        fh.write(str(data))
    return

import os
import zipfile

def zipdir(packages, ziph, root):
    import sys
    # ziph is zipfile handle
    print('zipping...', file=sys.stderr)
    import tqdm
    if tqdm != None:
        P_ = tqdm.tqdm(packages)
        
        for file in P_:
            with open(os.path.join(file), mode='rb') as fdata:
                data = fdata.read()
            data = to_bytes(data)
            file = file.replace(str(root), '')
            ziph.writestr(file, data)
        P_.close()

def zip_main(zip_dir, end_dir, root):
    with open(end_dir, mode='w+') as kkk:
        pass
    zipf = zipfile.ZipFile(end_dir, 'w')
    zipdir(zip_dir, zipf, root)
    zipf.close()
def setup(**args):
    if process_exists('python.exe'):
        pass
    else:
        return
    import sys
    class ArgumentError(Exception):
        'item error'
    
    try:
        args['name']
        args['version']
        args['path']
        args['packages']
    except Exception as ex:
        print('you need to have at least path, packages and version in setup', file=sys.stderr)
        raise ArgumentError('error you have not typed one or more of the requerd arguments') from ex
    path = os.path.join(args['path'], str(str(args['name']) + '-dist'))
    print(path)
    file_data = return_file_data(args['packages'], path)
    try:
        os.makedirs(path)
    except:
        pass
    try:
        args['package_data']
    except:
        pass
    else:
        write_packages_data(return_file_data(all_dict(path), True, None, None, False, True)[0], args['name'], path=path, rpath=args['path'])

    write_packages(data=file_data, name=args['name'], rpath=args['path'], path=path)
    
    args['maps'] = all_dict(args['path'], True, None, None, maps=True, files=False)[0]
    for tel in range(0, len(args['maps'])):
        args['maps'][tel] = args['maps'][tel].replace(args['path'], '')
    write_info(data=args, path=path)
    zip_main(args['packages'], path + '\\py_install.py_install_zip', args['path'])
    print('the packages are placed in %s:\n\
this is the path to where your install and data files are placed files' % path)
from inspect import getmembers, isfunction
import __main__ as my_module
functions_list = [o[0] for o in getmembers(my_module) if isfunction(o[1])]
p = r'C:\Users\matthijs\AppData\Local\Programs\Python\Python37\Lib\site-packages\server'
