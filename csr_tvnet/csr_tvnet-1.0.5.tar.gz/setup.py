from distutils.core import setup
project_name = 'csr_tvnet'
project_ver = '1.0.5'
setup(
    name=project_name,
    packages=['csr_tvnet'],
    version=project_ver,
    description='Transit Vnet Package',
    author='Vamsi Kalapala',
    author_email='vakalapa@cisco.com',
    scripts=["bin/setup_tvnet.py"],
    # use the URL to the github repo
    url='https://github4-chn.cisco.com/csr1000v-cloud/' + project_name,
    download_url='https://pypi.python.org/pypi?:action=display&name=%s&version=%s' % (
        project_name, project_ver),
    keywords=['cisco', 'guestshell', 'dmvpn', 'csr1kv', 'csr1000v'],
    classifiers=[],
    license="MIT"
)
