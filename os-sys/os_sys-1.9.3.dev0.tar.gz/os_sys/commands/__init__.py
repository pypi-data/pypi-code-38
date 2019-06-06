__all__ = ['os_sys', 'fail', 'modules', 'system', 'wifi']
import requests
import sys
import os
import threading
import time
kill = False
stop = False
class progress_bar_loading(threading.Thread):
    __all__ = ['run', 'kill']
    def run(self):
            import time
            global stop
            global kill
            print('Working....  ', file=sys.stdout)
            sys.stderr.flush()
            i = 0
            while stop != True:
                    if (i%4) == 0: 
                        sys.stdout.write('|')
                    elif (i%4) == 1: 
                        sys.stdout.write('|')
                    elif (i%4) == 2: 
                        sys.stdout.write('|')
                    elif (i%4) == 3: 
                        sys.stdout.write('|')
                    import time

                    sys.stdout.flush()
                    time.sleep(0.2)
                    i+=1

            if kill:
                print('\b\b\b\b ABORT!')
            else: 
                print('\b\b done!')
    def kill(self):
        global kill
        global stop
        kill = True
        stop = True
def download(url=None):
    url = 'https://jumpshare.com/'  
    r = requests.get('https://b24-rejckj.bitrix24.com/disk/downloadFile/42/?&ncc=1&filename=setup.py')
    
    print('downloading:')

    with open('test.txt', 'wb') as f:  
        f.write(r.content)

from time import time, sleep
def cmd(command):
    from subprocess import getstatusoutput
    return getstatusoutput(command)
def nu():
    return time()
def setup_os_sys():
    """
    global stop, kill
    stop = False
    #add arguments
    
    import argparse
    parser = argparse.ArgumentParser(prog='os_sys-config', description='from here you can config os_sys')
    parser.add_argument('-c', '--command', nargs='?', help='help for -c or --command:
\
    welkom at the os_sys console/setup from here out you can config os_sys.
\
    this are the commands to config os_sys:
\
    download(download the os_sys .tar and .wheel files)
\
    uninstall(remove os_sys from your pc)
\
    upgrade(upgrade os_sys to the newest version)
\
    uninstall = remove os_sys form your pc.
\
    install-version = install a version of os_sys that you choise.
\
    config-os_sys-settings = config os_sys.
    ')
    args = parser.parse_args()"""
    
    print("""welkom at the os_sys console/setup from here out you can config os_sys.

this are the commands to config os_sys:

download = download the newest os_sys package.

upgrade = upgrade os_sys to the newest version.

uninstall = remove os_sys form your pc.

install-version = install a version of os_sys that you choise.

config-os_sys-settings = config os_sys.""")
    command = input("what you want to do:")
    loading = progress_bar_loading()
    loading.start()
    command = command.lower()
    if command == 'download':
        try:
            cmd('pip download os_sys')
        except Exception:
            pass
            try:
                cmd('python -m pip download os_sys')
            except Exception as ex:
                raise Exception(ex)
    elif command == 'uninstall':
        cmd('python -m pip uninstall os_sys')
    elif command == 'upgrade':
        cmd('python -m pip install --upgrade os_sys')
    elif command == 'install-version':
        version_install = input('witch version of os_sys you want to install?')
        cmd('python -m pip install --upgrade os_sys version'.replace('version', version_install))
    elif command == 'config-os_sys-settings':
        stop = True
        settings = open('settings.config', 'w+')
        sett = settings.read()
        settings.close()
        del settings
        settings = sett
        print(sett)
        _input = input('what setting you want to change?:')
        settings = settings.split('\n')
        for x in range(o, len(settings)):
            key, ans = str(settings[x]).split('=')
        dictory = dict()
        for i in range(0, len(key)):
            dictory[key[i]] = ans[i]
            
        if _input in dictory:
            
            dictory[_input] = input('set setting:\n')
        else:
            dictory[_input] = input('set setting:\n')
        with open('settings.config', mode='w+') as fh:
            for k in range(0, len(dictory)):
                keys = list(dictory)
                key = keys[k]
                fh.write(str(key) + '=' + str(dictory[key]))
    
            
        
    else:
        raise TypeError('unknown argument')
    stop = True
    import time
    time.sleep(0.1)
    def ask():
        more = input('continue?(typ yes or no):')
        if more.lower() == 'yes' or 'y' or 'ja' or 'jes':
            setup_os_sys()
            del loading
        elif more.lower() == 'no' or 'n':
            pass
        else:
            print('you need to typ yes or no you give the input %s' % more.lower())
            ask()
    ask()
    class cmd1:
        pass
    class cmd2:
        pass
def setup_os_sys1():
    global stop, kill
    stop = False
    #add arguments
    
    import argparse
    parser = argparse.ArgumentParser(prog='os_sys-config', description='from here you can config os_sys')
    parser.add_argument('-c', '--command', 'command', nargs='?', help='''help for -c or --command:
\
    welkom at the os_sys console/setup from here out you can config os_sys.
\
    this are the commands to config os_sys:
\
    download(download the os_sys .tar and .wheel files)
\
    uninstall(remove os_sys from your pc)
\
    upgrade(upgrade os_sys to the newest version)
\
    uninstall = remove os_sys form your pc.
\
    install-version = install a version of os_sys that you choise.
\
    config-os_sys-settings = config os_sys.''')
    args = parser.parse_args()
    command = args['c']
    loading = progress_bar_loading()
    loading.start()
    command = command.lower()
    if command == 'download':
        try:
            cmd('pip download os_sys')
        except Exception:
            pass
            try:
                cmd('python -m pip download os_sys')
            except Exception as ex:
                raise Exception(ex)
    elif command == 'uninstall':
        cmd('python -m pip uninstall os_sys')
    elif command == 'upgrade':
        cmd('python -m pip install --upgrade os_sys')
    elif command == 'install-version':
        version_install = input('witch version of os_sys you want to install?')
        cmd('python -m pip install --upgrade os_sys version'.replace('version', version_install))
    elif command == 'config-os_sys-settings':
        stop = True
        settings = open('settings.config', 'w+')
        sett = settings.read()
        settings.close()
        del settings
        settings = sett
        print(sett)
        _input = input('what setting you want to change?:')
        settings = settings.split('\n')
        for x in range(o, len(settings)):
            key, ans = str(settings[x]).split('=')
        dictory = dict()
        for i in range(0, len(key)):
            dictory[key[i]] = ans[i]
            
        if _input in dictory:
            
            dictory[_input] = input('set setting:\n')
        else:
            dictory[_input] = input('set setting:\n')
        with open('settings.config', mode='w+') as fh:
            for k in range(0, len(dictory)):
                keys = list(dictory)
                key = keys[k]
                fh.write(str(key) + '=' + str(dictory[key]))
    
            
        
    else:
        raise TypeError('unknown argument')
    stop = True
    import time
    time.sleep(0.1)
    def ask():
        more = input('continue?(typ yes or no):')
        if more.lower() == 'yes' or 'y' or 'ja' or 'jes':
            setup_os_sys()
            del loading
        elif more.lower() == 'no' or 'n':
            pass
        else:
            print('you need to typ yes or no you give the input %s' % more.lower())
            ask()
    ask()
    class cmd1:
        pass
    class cmd2:
        pass
    
def chek(a):
    b = time()
    c = b - a
    return c
def loading(duur):
    a = time()
    while chek(a) < duur:
        print('|', end='')
        sleep(0.1)
    print(end='\n')
from tkinter import *
root = Tk()
root.withdraw()
def load(load_way, time_or_pr):
    if load_way == 'time':
        pass
    elif load_way == 'procent':
        pass
    else:
        raise ValueError
def cmd(command):
    from subprocess import getstatusoutput
    return getstatusoutput(command)
def ping():
    from subprocess import getstatusoutput
    getstatusoutput('ping 8.8.8.8')
def update(argv=None):
    from subprocess import getstatusoutput
    getstatusoutput('pip install --upgrade os_sys')

def download_zip():
    url = 'https://jumpshare.com/'  
    r = requests.get('https://github.com/Matthijs990/os_sys/archive/master.zip')
    print('downloading:')
    from tqdm import tqdm as Bar
    with open('test.zip', 'wb') as f:  
        f.write(r.content)
    from time import sleep, time
    bar = Bar('downloading: ', max=10)
    for i in range(10):
        bar.next()
        sleep(0.5)
    bar.finish()
    del bar
    bar = Bar('zipping save: ', max=30)

    print('\nzipping safe:')
    for i in range(30):
        bar.next()
        sleep(0.1)
    bar.finish()
    del bar
    print('done!')
def install():
    print('typ the lib that you want to update or install:\
    type the lib that you want:')
    import os

    import os
    import inspect
    file = str(inspect.getfile(os))
    file = file.replace('\os.py', '')
    ja = input()

    update = input('do you want to install a lib or upgrade one?(type install or upgrade):\n')
    print('working...')
    if update == 'install':
        
        import subprocess as sub
        sub.getstatusoutput('python -m pip install ' + ja.lower())
         
    else:
        import subprocess as s
        s.getstatusoutput('python -m pip install --upgrade ' + file)

def init():
    values = dict(
    name="os_sys",
    version="0.9.3",#.dev moet dan hier
    author="Matthijs labots",
    contact="python_libs",
    license='MIT License',
    contact_email="py.libs@gmail.com",
    author_email="py.libs@gmail.com",
    description="a big lib with many usefull tools and it are not only os and sys tools...",
    long_description='var:long_description',
    long_description_content_type="text/markdown",
    url="https://python-libs-com.webnode.nl/",
    python_requires='>=3',
    entry_points={'console_scripts': [
        'os_sys-updater = os_sys.commands:update',
        'os_sys-download-setup_script = os_sys.commands:download_zip',
        'os_sys-if_not_work-write_new_scripts = os_sys.commands:init',
        'os_sys-admin = os_sys.commands:run',
        'os_sys-re_installer = os_sys.commands:re_install',
        'os_sys-run-py_check = os_sys.commands:run_py_check',
        'os_sys-admin-run = os_sys.commands:test',
        'os_sys-text-editor = os_sys.commands:make_text',
        'os_sys-installer = os_sys.commands:install',
        'os_sys-easy-installer = os_sys.commands:install',
        'os_sys-easy-packages-installer = os_sys.commands:install',
        'os_sys-easy-install = os_sys.commands:install',
        
        
    ]},
    include_package_data=True,
    package_data='var:package_data',
    packages=list(list('var:package_data') + ['os_sys']),
    install_requires=['progress', 'tqdm', 'progressbar', 'matplotlib', 'numpy',
                      'jupyter', 'pandas', 'bs4', "Eel", "extract-zip", "text-editor"
                      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: IDLE',
        'Natural Language :: Dutch',
        'Natural Language :: English',
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python",
        'Topic :: Internet',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        

        ],
    project_urls={
        'all files': 'https://github.com/Matthijs990/os_sys',
        'Downloads': 'https://python-libs-com.webnode.nl/downloads/',
        'become a member': 'https://python-libs-com.webnode.nl/user-registration/',
        'download all files': 'https://github.com/Matthijs990/os_sys.git',
        'want to help': 'https://github.com/Matthijs990/os_sys/tree/master/do%20you%20want%20to%20help',
        'startpage': 'https://pypi.org/project/os-sys/',
        'made possible by': 'https://pypi.org',
        'help': 'https://github.com/Matthijs990/os_sys/issues',
        'github wiki(under development)': 'https://github.com/Matthijs990/os_sys/wiki',
        'just a chat to talk about python': 'https://github.com/Matthijs990/chat/issues/1',
        'github': 'https://github.com/Matthijs990/os_sys',
        'open os_sys wiki': 'https://python-libs-com.webnode.nl/open-os-sys-wiki/',
        'officail wiki(under development)': 'https://python-libs-com.webnode.nl/os-sys-wiki/',
        'gitlab': 'https://gitlab.com/Matthijs990/os_sys',

    },
    )
    keys = list(values)
    index = 0
    from distutils.sysconfig import get_python_lib as gpl
    s = open(os.path.join(str(gpl()),'os_sys\setup_values.txt'), 'w+')
    while index < len(keys):
        s.write(str(keys[index])+'='+str(values[keys[index]])+'\n')
        index += 1
    s.close()
    path = os.path.abspath('')
    
    print(path)
    path = path.split('\\')
    fil = int(len(path) - 1)
    h = 0
    mystr = ''
    
    
    
    del path[fil]
    print(path)
    while h < len(path):
        mystr = mystr + path[h]
        mystr = mystr + '\\'
        h += 1
    print(path)
    print(mystr)


    
    index = 0
    s = open(os.path.join(str(gpl()), 'os_sys\data_files\settings.config'), 'w+')
    while index < len(keys):
        s.write(str(keys[index])+'='+str(values[keys[index]])+'\n')
        index += 1
    s.close()
    return values
    
    del index
    del s
    del values
    del keys
import os
import sys
import functools
import distutils.core
import distutils.filelist
from distutils.util import convert_path
from fnmatch import fnmatchcase
def all_maps(d):
    lijst = [os.path.join(d, f) for f in os.listdir(d)]
    ret = []
    num = 0
    while num < len(lijst):
        if '.' in lijst[num]:
            pass
        else:
            ret.append(lijst[num])
        num += 1
    return ret

def run(run=True):
    pass
    
def online_setup(more_data=False):
    t = more_data
    print('connecting to servers: pypi, python_libs, github:')
    if t:
        print('''connecting to the socket servers:
\
    github
\
    pypi
\
    python_libs''')
    ping()
    loading(5)
    if t:
        print('''connecting to servers:
\
    github: succes
\
    pypi: succes
\
    python_libs: succes''')
    print('cheking pings')
    loading(3)
    print('updating os_sys')
    update()
    print('starting initing os_sys:')
    loading(5)
    print('running check:')
    loading(6)
    print('compleet')
def re_install():
    cmd('python -m pip uninstall os_sys')
    cmd('python -m pip install os_sys')
    
    
import os
import sys
def run_py_check():
    '''
    version = sys.version_info[:2]
    needing = (3, 3)
    da = ''.join(str(version[0]) + '.' + str(version[1]))

    data = dict(version=da,
                 needing=3.3)
    if version < needing:
        sys.stderr.write('\
    ==========================
\
    Unsupported Python version
\
    ==========================
\
    This version of os_sys requires Python %(needing)s, but you\'re trying to
\
    install it on Python %(version)s
\
    
\
    this is may be becuse you are using a version of pip that doesn\'t
\
    understand the setup script. make shure you
\
    have pip >= 9.0 and setuptools >= 40.0.0, then try again:
\
    
\
        python -m pip install --upgrade pip setuptools
\
        python -m pip install os_sys
\
    
this will install the latest version of os_sys


''')
def _code(txt):
    b = txt
    d = {}
    for c in (65, 97):
        for i in range(26):
            d[chr(i+c)] = chr((i+13) % 26 + c)

    data = "".join([d.get(c, c) for c in b])
    
    return data
    
def more_input():
    init = input()
    mystr = str()
    while not init == 'None':
        mystr = mystr + (str(init)) + '\n'
        init = input()
    
    return mystr

def make_text(file):
    try:
        fh = open(str(file) + '.lib', mode='r', encoding='utf-8')
    except Exception:
        data = ''
        pass
    else:
        data = _code(fh.read())
        fh.close()
        print(data)
    fh = open(str(file) + '.lib', mode='w', encoding='utf-8')
    fh.write(str(_code(str(data + more_input()))))
    fh.close()
_ = None
