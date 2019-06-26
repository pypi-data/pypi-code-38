"""pwclip packaging information"""
name = 'pwclip'
provides = ['pwcli', 'pwclip', 'ykclip']
version = '1.6.0'
install_requires = [
    'argcomplete', 'paramiko', 'psutil', 'python-gnupg',
    'python-yubico', 'PyYAML', 'wget', 'cryptography']
url = 'https://github.com/d0n/pwclip'
download_url = 'http://deb.janeiskla.de/ubuntu/pool/main/p/pwclip/python3-pwclip_%s-1_all.deb'%version
license = "GPLv3+"
author = 'Leon Pelzer'
description = 'password-manager - temporarily saves passwords to the clipboard'
author_email = 'mail@leonpelzer.de'
classifiers = ['Environment :: Console',
               'Environment :: MacOS X',
               'Environment :: Win32 (MS Windows)',
               'Environment :: X11 Applications',
               'Intended Audience :: Developers',
               'Intended Audience :: End Users/Desktop',
               'Intended Audience :: System Administrators',
               'Intended Audience :: Information Technology',
               'License :: OSI Approved :: ' \
                   'GNU General Public License v3 or later (GPLv3+)',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 3',
               'Topic :: Security',
               'Topic :: Security :: Cryptography',
               'Topic :: Desktop Environment',
               'Topic :: Utilities',
               'Topic :: Desktop Environment']
include_package_data = True
long_description = ''
try:
	long_description = str('\n\n\n'.join(
        str(open('pwclip/docs/changelog.rst', 'r').read()).split('\n\n\n')[:4]
        )).format(CurrentVersion='%s (current)\n----------%s'%(
            version, '-'*len(version)))
except (FileNotFoundError, NotADirectoryError):
	long_description = ''
try:
	__rs = []
	with open('pwclip/docs/readme.rst', 'r') as __r:
		__rrs = __r.readlines()
	for l in __rrs:
		if l.startswith('.. include::'):
			__rst = l.split('.. include::')[1].lstrip(' ./').strip()
			try:
				with open('pwclip/docs/%s'%__rst, 'r') as __i:
					__rs = __rs + [i for i in __i.readlines()]
				continue
			except FileNotFoundError:
				pass
		__rs.append(l)
	long_description = ''.join(__rs).format(ChangeLog=long_description)
except (FileNotFoundError, NotADirectoryError):
    long_description = ''
try:
	open('pwclip/docs/conf.py', 'w+').write(str(
            open('pwclip/docs/conf.py.tmpl', 'r').read()
        ).format(VersionString=version))
except (FileNotFoundError, NotADirectoryError):
	pass
entry_points = {
    'console_scripts': ['pwcli = pwclip.__init__:pwcli'],
    'gui_scripts': ['pwclip = pwclip.__init__:pwclip',
                    'ykclip = pwclip.__init__:ykclip']}
package_data = {
    '': ['pwclip/docs/'],
    '': ['pwclip/example']}
data_files=[
    ('share/man/man1', ['pwclip/docs/pwclip.1']),
    ('share/pwclip', [
        'pwclip/example/ca.crt', 'pwclip/example/commands.rst',
        'pwclip/example/ssl.crt', 'pwclip/example/ssl.key',
        'pwclip/example/passwords.yaml'])]
