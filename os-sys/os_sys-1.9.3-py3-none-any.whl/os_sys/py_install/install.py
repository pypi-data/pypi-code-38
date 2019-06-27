#installer
#python3.7
#devlopment
import os, sys
import os_sys
__all__ = ['install']
import requests
def download_file(url):
    from tqdm import tqdm
    import requests
    import math

    local_filename = url.split('/')[-1]
    # Streaming, so we can iterate over the response.
    r = requests.get(url, stream=True)

    # Total size in bytes.
    total_size = int(r.headers.get('content-length'))
    block_size = 1024
    wrote = 0 
    with open(local_filename, 'wb') as f:
        b = tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size) , unit='KB', unit_scale=True)
        for data in b:
            wrote = wrote  + len(data)
            f.write(data)
    if total_size != 0 and wrote != total_size:
        print("ERROR, something went wrong")  


import tqdm
import psutil
def process_exists(name):
    i = psutil.pids()
    for a in i:
        try:
            if str(psutil.Process(a).name) == name:
                return True
        except:
            pass
    return False
import shutil
def copytree(src, dst, symlinks=False, ignore=None):
    import tqdm
    items = tqdm.tqdm(os.listdir(src))
    fi = False
    for item in items:
        if fi == False:
            fi == item
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        s = s.replace('/', '\\')
        d = d.replace('/', '\\')
        if os.path.isdir(s):
            try:
                shutil.rmtree(d)
            except:
                pass
            try:
                shutil.copytree(s, d, symlinks, ignore)
            except Exception as ex:
                print('ERROR:', ex.__class__, str(ex))
        else:
            try:
                shutil.copy2(s, d)
            except Exception as ex:
                print('ERROR:', ex.__class__, str(ex))
    items.close()
    return fi

def all_dict(dictory, ex=False, exceptions=None, file_types=['py_install'], maps=False, files=True, print_data=False):
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
    
    print_ = print_data
    
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
def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode() # uses 'utf-8' for encoding
    else:
        value = bytes_or_str
    return value # Instance of bytes
from time import time
def install_zip(zip_file, end_dir, rpath):
    print('unzipping...', file=sys.stderr)
    print('installing...')
    import tqdm 
    from zipfile import ZipFile
    with ZipFile(zip_file, 'r') as zipObj:
        # Get a list of all archived file names from the zip
        files = zipObj.namelist()
        import tqdm
        Bar = tqdm.tqdm(files)
        # Iterate over the file names
        first = None
        for fileName in Bar:
            # Extract a single file from zip
            if first == None:
                first = fileName
            try:
                zipObj.extract(fileName, end_dir)
            except:
                pass
        Bar.close()

        
        

import tempfile
def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode() # uses 'utf-8' for encoding
    else:
        value = bytes_or_str
    return value # Instance of str
def stl(s):
    # string naar lijst
    l = []
    for i in range(0,len(s)): l += s[i]
    return l
def install(path, verbose, quiet):
    global name
    if quiet != True:
        print('searching files...', file=sys.stderr)
    file = all_dict(path)[0][0]
    from distutils.sysconfig import get_python_lib as gpl
    print('reading package files...', file=sys.stderr)
    with open(file, mode='rb') as fh:
        mystr = to_str(str(str(str(to_str(fh.read())).replace('\\n', '\n')).replace('\\r', '\r')).replace('\\n', ''))
    e = mystr.split('\r')
    the = all_dict(path, ex=False, exceptions=None, file_types=['py_install_zip'], maps=False, files=True, print_data=False)[0][0]
    mystr.replace('\n', '')
    with open(all_dict(path, ex=False, exceptions=None, file_types=['info'], maps=False, files=True, print_data=False)[0][0]) as info:
        rpackage_info = str(info.read())
    package_info = rpackage_info.split('\n')
    if verbose:
        print('getting info about package...', file=sys.stderr)
    info_dict = {}
    for small in package_info:
        try:
            key, value = small.split('=')
            info_dict[key] = value
            value = value
            
        except:
            pass
        else:
            if 'name' in key:
                from distutils.sysconfig import get_python_lib as gpl
                base_path = gpl() + '\\' + value
                name = value
                del key, value
                continue
            elif key == 'version':
                version = value
                del key, value
                continue
            else:
                del key, value
                continue
    try:
        from distutils.sysconfig import get_python_lib as gpl
        mapsdel =all_dict(gpl() + '\\' + info_dict['name'], maps=True, files=False)
    except:
        pass
    for i in mapsdel:
        try:
            _
            shutil.rmtree(i)
        except:
            pass
    if quiet != True:
        print('generating info file...', file=sys.stderr)
    lijst = info_dict['maps']
    lijst = str(str(str(str(lijst.replace('[', '')).replace(']', '')).replace("'", '')).replace('\\\\', '\\')).split(", ")
    
    print(info_dict['name'])
    
    base = gpl() + '\\' + info_dict['name']
    delete = base
    
    if os.path.isdir(base):
        print('found older installation')
        
        if quiet != True:
            print('uninstalling...')
    try:
        for i in range(10000):
            shutil.rmtree(delete, True)
        _list = all_dict(delete, file_types=None)
        for i in _list:
            os.rmdir(i)
        print('done')
    except Exception:
        pass
    try:
        os.mkdir(base)
    except:
        pass
    try:
        os.mkdir(base)
        os.mkdir(os.path.abspath('\\lib'))
    except Exception:
        pass
    base = base_path
    for inum in range(0, len(lijst)):
        i = lijst[inum]
        print(os.path.join(base, i))
        try:
            os.remove(os.path.join(base, i))

        except:
            pass
    try:
        os.makedirs(lijst)
    except:
        pass
    try:
        os.makedirs(base)
    except:
        pass
    with open(os.path.join(gpl(), info_dict['name'], f'{name}.info'), mode='w+') as done:
        done.write(rpackage_info)
    if quiet != True:
        print('building to temp file...', file=sys.stderr)
    mystr = mystr.split('##########')
    tp = tempfile.mkdtemp()

    import time
    pbar = tqdm.tqdm(mystr)
    if time != None:
        for i in pbar:
            
            try:
                path, data = i.split('>>>>>>>>>>>>>>>')
                if verbose:
                    pbar.set_description(f'processing file: {path}...')
                a = path
            except Exception:
                pass
            else:
                
                data = str(data)
                from distutils.sysconfig import get_python_lib as gpl
                path2 = tp

                pat = path2 + '\\' + path
                dir_ = os.path.dirname(pat)
                try:
                    os.mkdir(dir_)
                except:
                    pass
                try:
                    with open(pat, mode='wb') as kk:
                        kk.write(to_bytes(str(str(data).replace('\\r', '\r')).replace('\\!n', '')))
                except Exception:
                    pass
        pbar.set_description(f'done building!')
    pbar.close()
    fik = install_zip(the, base, base)
    if quiet != True:
        print('removing temp dict...', file=sys.stderr)
    shutil.rmtree(tp, True)

    print('done!', file=sys.stderr)



