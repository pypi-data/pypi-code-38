import setuptools
import setuptools as s

try:
    import ready
except Exception:
    pass
def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()

package_data = dict()

with open("README.md", "r") as fh:
    long_description = fh.read()
import sys
import os
def run_py_check():
    version = sys.version_info[:2]
    needing = (3, 3)
    da = ''.join(str(version[0]) + '.' + str(version[1]))

    data = dict(version=da,
                 needing=3.3)
    if version < needing:
        sys.stderr.write('\
    ==========================\n\
    Unsupported Python version\n\
    ==========================\n\
    This version of os_sys requires Python %(needing)s, but you\'re trying to\n\
    install it on Python %(version)s\n\
    \n\
    this is may be becuse you are using a version of pip that doesn\'t\n\
    understand the setup script. make shure you\n\
    have pip >= 9.0 and setuptools >= 40.0.0, then try again:\n\
    \n\
        python -m pip install --upgrade pip setuptools\n\
        python -m pip install os_sys\n\
    \nthis will install the latest version of os_sys\n\n\n' % data)
        class PythonVersionError(Exception):
            '''not right python version'''
            pass
        raise PythonVersionError('you need at least python 3.3')
from distutils.sysconfig import get_python_lib as gpl
with open('data_types.txt') as dem:
    raw_data_types = dem.read()
data_types = raw_data_types.split('/')
p = data_types
overlay_warning = False
def check():
    path = str(str(gpl()) + 'os_sys')
    if os.path.isdir(path):
        print('\
========\n\
Warning!\n\
========\n\
you now installing os_sys on a mac, pc, laptop or something else where os_sys is al ready installd\n\
programs that use this lib while can give errors becuse you are not upgrading the lib on the right way\n\
if you want to upgrade this lib than you need to typ this on cmd:\n\
python -m pip install --upgrade os_sys', file=sys.stderr)
def run_after():
    if overlay_warning:
        sys.stderr.write('Warning: os_sys is al ready on your pc')
def all_dict():
    l = []
    for dirname, dirnames, filenames in os.walk('.'):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            data = os.path.join(dirname, subdirname)
            if '__pycache__' in data:
                dirnames.remove('__pycache__')
            elif 'os_sys.egg-info' in data:
                dirnames.remove('os_sys.egg-info')
            elif 'build' in dirnames:
                dirnames.remove('build')
            elif 'dist' in dirnames:
                dirnames.remove('dist')
            elif 'docs' in dirnames:
                dirnames.remove('docs')
            elif 'django' in dirnames:
                dirnames.remove('django')
                
            else:
                data = data.replace('.\\', '')
                data = data.replace('\\', '.')
                l.append(data)
    return l



def run():
    run_py_check()
    check()
    run_after()
    return ''
re = os.path.abspath
def all_maps(d, plus=None):
    
    lijst = [os.path.join(d, f) for f in os.listdir(d)]
    ret = []
    num = 0
    while num < len(lijst):
        if '.' in lijst[num]:
            pass
        else:
            if plus == None:
                ret.append(lijst[num])
            else:
                ret.append(str(plus)+'|'+str(lijst[num]))
        num += 1
    return ret
lijst = all_dict()

lijst[0].join(str(run()))
num = 0
while num < len(lijst):
    
    to = num
    
    package_data.setdefault(lijst[to], []).extend(p)
    num += 1
lijst = all_maps(os.path.abspath('os_sys\commands'))
#als ik bij version er str(int).dev achter zet dan is het een pre-releas

long_description = long_description.replace('evry', 'every')
def v():
    from bs4 import BeautifulSoup
    import requests
    url = "https://pypi.org/project/os-sys/"
    html = str(requests.get(url).content)
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    line
    text = text.replace('\\n', '\n')
    text = str(text)
    line = text.split('\n')
    for l in line:
        l = l.rstrip('\n')
        try:
            name, etc = l.split(' ')
        except:
            pass
        else:
            if 'os-sys' in name:
                return etc
    s = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    text = text.replace('\\n', '\n')
    text = str(text)
    line = text.split('\n')
    for l in line:
        l = l.rstrip('\n')
        try:
            name, etc = l.split(' ')
        except:
            pass
        else:
            if 'os-sys' in name:
                return etc

from setuptools.command.develop import develop
from setuptools.command.install import install
class Install(install):
    """Post-installation for installation mode."""
    def run(self):
        os.system('echo')
        install.run(self)

setuptools.setup(
    name="os_sys",
    version="1.9.3.dev",#.dev moet dan hier
    author="Matthijs labots",
    contact="python_libs",
    license='GNU General Public License',
    contact_email="py.libs@gmail.com",
    author_email="py.libs@gmail.com",
    description="a big lib with many usefull tools and it are not only os and sys tools...",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://stranica.nl/",
    python_requires='>=3',
    entry_points={'console_scripts': [
        'os_sys-wheel-builder = os_sys.wheel_build:main',
        'ins = ins.__main__:_main',
        'os_sys-wheel_console = os_sys.wheel_build:main',
        'server-admin = server.core.management:execute_from_command_line',
        'os_sys-server-admin = server.core.management:execute_from_command_line',
        'os_sys-devserver = os_sys.server:run',
        'os_sys-updater = os_sys.commands:update',
        'os_sys-download-setup_script = os_sys.commands:download_zip',
        'os_sys-if_not_work-write_new_scripts = os_sys.commands:init',
        'os_sys-setup_data-writer = os_sys.commands:init',
        'os_sys-re-init-os_sys = os_sys.commands:init',
        'os_sys-admin = os_sys.commands:run',
        'os_sys-re_installer = os_sys.commands:re_install',
        'os_sys-run-py_check = os_sys.commands:run_py_check',
        'os_sys-admin-run = os_sys.commands:test',
        'os_sys-text-editor = os_sys.commands:make_text',
        'os_sys-installer = os_sys.commands:install',
        'os_sys-easy-installer = os_sys.commands:install',
        'os_sys-easy-packages-installer = os_sys.commands:install',
        'os_sys-easy-install = os_sys.commands:install',
        'os_sys-console = os_sys.__main__:main',
        'os_sys-setup = os_sys.commands:setup_os_sys1',
        'os_sys-py_install-install_local_files = os_sys.py_install:install_local_files',
        'os_sys-py_install-installer-auto-install = os_sys.py_install.commands:auto_install',
        
        
        
    ]},
    keywords=['os', 'sys', 'server', 'ins', 'wsgi', 'devserver'],
    cmdclass={'install': Install},
    include_package_data=True,
    package_data=package_data,
    packages=list(list(package_data) + ['os_sys']),
    install_requires=['pygubu', 'pytz', 'sqlparse', 'progress', 'tqdm', 'progressbar', 'matplotlib', 'numpy',
                      'jupyter', 'pandas', 'beautifulsoup4', "Eel", "extract-zip", "text-editor",
                      "tuspy", "requests-download", "requests", "Send2Trash",
                      "pyspeedtest", "pytest", "wifi", "PyInstaller", "auto-py-to-exe",
                      "Django", "mysql-connector", "geocoder", "selenium", "psutil",
                      "pynput",
                      
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
        'Topic :: Desktop Environment :: File Managers',
        "Topic :: Internet",
        'Topic :: Internet :: File Transfer Protocol (FTP)',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Testing',
        'Topic :: System',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Operating System',
        'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 2.2',
        'Framework :: Django',
        'Topic :: Documentation',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: System',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Software Distribution',
        'Topic :: Text Processing :: Markup :: HTML',
        
        
        
        

        ],
    project_urls={
        'server documentation': 'https://www.stranica.nl/docs',
        'blog': 'https://stranica.nl/wordpress/wordpress/',
        'all files': 'https://github.com/Matthijs990/os_sys',
        'Downloads': 'https://stranica.nl/downloads.html',
        'download all files': 'https://github.com/Matthijs990/os_sys.git',
        'want to help': 'https://github.com/Matthijs990/os_sys/tree/master/do%20you%20want%20to%20help',
        'startpage': 'https://pypi.org/project/os-sys/',
        'made possible by': 'https://pypi.org',
        'help': 'https://github.com/Matthijs990/os_sys/issues',
        'github wiki(under development)': 'https://github.com/Matthijs990/os_sys/wiki',
        'just a chat to talk about python': 'https://github.com/Matthijs990/chat/issues/1',
        'github': 'https://github.com/Matthijs990/os_sys',
        'os_sys online': 'https://stranica.nl/os_sys/',
        'gitlab': 'https://gitlab.com/Matthijs990/os_sys',
        'read the docs': 'https://os-sys-wiki-page.readthedocs.io/en/latest/index.html',
        

    },
    
)


