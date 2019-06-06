try:
    from . import server
except:
    import server
import __main__ as ma
firs = True
try:
    ma.firs
except:
    ma.firs = True
__all__ = ['path', 'config', 'HTTPResponse']
def paths(port=9999, *programs):

    return
def config(*programs, port=9999, host='127.0.0.1'):
    global ma
    global firs
    import sys
    arg = sys.argv[-1]
    if __name__ != 'wiuefhsesdkfhdoshfiosduv':
        if firs and ma.firs:
            server.run_(port, host, *programs)
            firs = False
            ma.firs = False
    else:
        print('typ runserver to run the server')
def HTTPResponse(response):
    return response
def path(program, name, *args, **kwargs):
    return name, program

def all_dict(dictory, exceptions=None, file_types=None, maps=False, files=True, print_data=False):
    import os
    global ti
    ti = ''
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
                file = fname_path.split('.', 1)
                no = int(len(file) - 1)
                file_type = '/*.' + str(file[-1])
                ti += file_type
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
def run_local(path='.', port=9999, host='127.0.0.1'):
    if path == '.':

        base_dir = '.'

    else:

        base_dir = path

    paths = all_dict(path)[0]

    _raw = []

    for path in paths:

        try:

            _path = str(path).replace(base_dir, '', 1)

            if base_dir == '':

                data = open(path.replace('.', os.path.abspath(), 1)).read()

            else:

                data = open(path).read()

            def func(request):

                return data

            _raw.append((_path.replace('\\', '/'), func))

        except Exception as ex:
            pass
    end = tuple(_raw)
    config(*end, port=port, host='127.0.0.1')
    
        
        
