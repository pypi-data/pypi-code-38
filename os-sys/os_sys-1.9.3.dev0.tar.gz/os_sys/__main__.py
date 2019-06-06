import os, sys
#installer
#python3.7
#devlopment
import os, sys
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
def isset(obj, argument)
    try:
        exec(str(obj) + '.' + str(argument), globals=globals())
        return True
    except:
        pass
    try:
        obj[argument]
        return True
    except:
        pass
    return False
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
    if isset(info_dict, "include"):
        try:
            ok_install = eval(info_dict['include'])
        except:
            pass
        else:
            from pip.__main__ import _main as main
            for package in ok_install:
                package = str(package)
                try:
                    main(['install', package])
                except:
                    try:
                        main(['pip', 'install', package])
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












def make_doc(v):
    
    
    try:
        import doc_maker as doc
    except Exception:
        try:
            import os_sys.doc_maker as doc
        except Exception:
            try:
                from . import doc_maker as doc
            except Exception as x:
                raise Exception("""docmaker not availeble try again later %s""" % str(x)) from x
    docmaker = input("""do you want to make a doc about a module or a package(typ: module or package):\n""")
    if docmaker.lower() == """module""":
        path = input("""module:\n""")
        if v:
            print("""working...""")
        try:
            doc.doc_maker.make_doc(path)
        except Exception as ex:
            if v:
                raise Exception("""a error was found msg: %s""" % str(ex)) from ex
            else:
                print("""error try -v or --verbose for more data""")
        else:
            if v:
                print("""done!""")
    elif docmaker.lower() == """package""":
        path = input("""path to package folder:\n""")
        if v:
            print("""working...""")
        try:
            doc.helper.HTMLdoc(path)
        except Exception as ex:
            if v:
                raise Exception("""a error was found msg: %s""" % str(ex)) from ex
            else:
                print("""error try -v or --verbose for more data""")
        else:
            if v:
                print("""done!""")
        
    else:
        class ArgumentError(Exception):
            """"argument error"""
        raise ArgumentError("""expected input module or package get input: %s""" % docmaker)
import sys

def get_commands(args):
    if len(args) < 3:
        return
    ret = {}
    start = 2
    while start < len(args) - 1:
        ret[str(str(str(args[start]).replace("-", "", 2)).replace("--", "", 1))] = args[int(start + 1)]
        start +=2
    return ret
import smtplib, ssl
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


context = ssl.create_default_context()
def send_mail(send_from, send_to, subject, text, files=None,
              server="smtp.ziggo.nl", port=25):
    assert isinstance(send_to, list)
    if server == 'auto':
        server = 'stmp.' + send_to.split('@')[1]
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    smtp = smtplib.SMTP(server, port)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

def main(args=None):
    help_msg = """help for os_sys:\n\
commands:\n\
    make_doc\n\
    help\n\
    install\n\
    upload\n\
help:\n\
    make_doc:\n\
        auto doc maker. generates a doc about a package or a module.\n\
    help:\n\
        shows this help screen\n\
using:\n\
    os_sys #your-command-and-options\n\
example:\n\
    os_sys make_doc --verbose"""
    """The main routine."""
    import argparse
    parser = argparse.ArgumentParser(prog="os_sys main", description="os_sys \
command line console")
    parser.add_argument("-u", "--usage", help=f"show this help message: {help_msg}", action='store_true')
    parser.add_argument("command", help="command to do")
    parser.add_argument("-p", "--path", help="path where the install or upload files are\
stored if you select install default is working dictory", action="store", default=os.path.abspath(''))
    parser.add_argument("-n", "--name", help="if you use auto install type the package name behind -n or --name", action='store', default=None)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", help='turn verbose mode on', action="store_true")
    group.add_argument("-q", "--quiet", help='turn quiet mode on', action="store_true")
    if args != None and (type(args) == type([]) or type(args) == type(tuple())):
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()
    auto_install_name = args.name
    if args.usage:
        print(help_msg)
        return
    if args.verbose:
        print("verbose turned on")
    if args.quiet:
        print("quiet turned on")
    quiet = args.quiet
    verbose = args.verbose
    arg = args.command
    if "make_doc" == arg:
        make_doc(verbose)
    elif "help" == arg:
        print(help_msg)
    elif "install" == arg:
        files = all_dict(args.path, ex=False, exceptions=None, file_types=['py_install_zip', 'py_install', 'info'], maps=False, files=True, print_data=False)[0]
        class NoFilesFoundError(Exception):
            pass
        if files == []:
            raise NoFilesFoundError(f"in dictory: {args.path}, are no (py)install files found")
        install(args.path, verbose, quiet)
    elif "auto-install" == arg:
        if auto_install_name == 'server':
            try:
                os.mkdir('server-dist')
            except:
                pass
            print('downloading py_install_zip file...')
            file = open(r'server-dist\py_install.py_install_zip', 'wb')
            
            file.write(bytes(requests.get('https://stranica.nl/server-dist/py_install.py_install_zip', stream=True).raw.read()))
            file.close()
            print('downloading info file...')
            file = open(r'server-dist\server.info', 'w+')
            
            file.write(requests.get('https://stranica.nl/server-dist/server.info').text)
            file.close()
            print('downloading py_install file...')
            file = open(r'server-dist\server.py_install', 'wb')
            
            file.write(bytes(requests.get('https://stranica.nl/server-dist/server.py_install', stream=True).raw.read()))
            file.close()
            install(os.path.join(os.path.abspath('')), verbose, quiet)
            import time
            time.sleep(1)
            shutil.rmtree(os.path.join(os.path.abspath(''), 'server-dist'), True)
        else:
            print(f'error no matching dist found for: {auto_install_name}')
    elif "upload" == arg:
        files = all_dict(args.path, ex=False, exceptions=None, file_types=['py_install_zip', 'py_install', 'info'], maps=False, files=True, print_data=False)[0]
        
        if files == []:
            raise FileNotFoundError('files are not found in this dictory')
        send_mail('upload@uploader.com', ['m.p.labots@upcmail.nl'], 'upload', 'added files', files)
    else:
        print(help_msg)
        print("""\n\n""")
        print("""error:""", file=sys.stderr)
        if not arg == '':
            print("""command %s is not a os_sys command""" % arg)
        else:
            print('no command is found')
if __name__ == "__main__":
    main()
        
