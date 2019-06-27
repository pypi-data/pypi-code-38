import os, sys, requests
import string
all_letters = string.ascii_letters
__all__ = ['upload', 'upload_tree']
def all_dict(dictory, exceptions=None, file_types=None, maps=True, files=False, print_data=False):
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
    
    return [data, string_data]
def upload(file, link='http://httpbin.org/post', login=False, user=None, pwd=None):
    if login == True and user == None:
        user = input('username:')
        if pwd == None:
            pwd = input('password:')
    elif login == True and pwd == None:
        pwd = input('password:')
    else:
        pass
    if login:
        with open(str(file), 'rb') as f:
            r = requests.post(link, auth=(user, pwd), files={str(file): f})
    else:
        with open(str(file), 'rb') as f:
            r = requests.post(link, files={str(file): f})
    return str(r.text)
def upload_tree(dictory, link='http://httpbin.org/post', login=False, user=None, pwd=None):
    files = all_dict(dictory, None, None, False, True, False)[0]
    if login and user == None:
        user = input('username:')
        if pwd == None:
            pwd = input('password:')
    elif pwd == None:
        pwd = input('password:')
    else:
        pass
    for k in range(0, len(files)):
        try:
            pass
        except:
            pass
    response = []
    for i in range(0, len(files)):
        try:
            response.append(upload(str(files[i]), link, login=login, user=user, pwd=pwd))
        except Exception as ex:
            response.append('''error: %s by uploading file''' % ex)
    return response

def upload_api(link, file, chunk_size=1000, **headers):
    from tusclient import client
    import os
    b = os.path.getsize(file)
    for k in range(0, len(all_letters)):
        try:
            b = b.replace(str(all_letters[k]), '')
        except Exception:
            pass
    size = int(b)
    from tqdm import tqdm
    def read_in_chunks(file_object, chunk_size):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data
    maxi = size / chunk_size
    maxi = maxi
    if maxi < 1:
        maxi = 1
    pbar = tqdm(read_in_chunks(f, chunk_size))
    
    f = open(file, encoding='utf-8')
    for piece in pbar:
        r = requests.put(link, data=str(piece))
    pbar.close()
    try:
        requests.post(link, data=str(r))
    except Exception:
        pass
    
    

def upload_api_tree(link, dictory, chunk_size=1000, **headers):
    files = all_dict(dictory, None, None, False, True, False)[0]
    from tqdm import tqdm
    pbar = tqdm(list(files), mininterval=0.0001)
    for file in pbar:
        print('
')
        pbar.set_description("Processing %s" % file)
        print('
')
        try:
            upload_api(link, file, chunk_size, **headers)
        except Exception:
            upload(file, link)
        
    pbar.close()
    print('done!!', file=sys.stderr)

import inspect as _ins
import __main__ as my_module
__all__ = ['all_dict', 'upload', 'upload_api', 'upload_api_tree', 'upload_tree']


