from distutils.core import setup
from setuptools.command.install import install
import subprocess
from subprocess import check_call
import os

class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        # note: pip install suppresses all user stdout/stderr output unless -v/--verbose option is specified. 
        print "We are running in the postInstallCommand"
        cwd = os.path.dirname(os.path.realpath(__file__))
        check_call("bash %s/ha_tools.sh" % cwd, shell=True)
        install.run(self)
        print "NOTE: 'source ~/.bashrc' is necessary for HA commands to be accessible."


project_name = 'csr_azure_ha'
project_ver = '1.0.4'
setup(
    name=project_name,
    packages=[project_name],  # this must be the same as the name above
    version=project_ver,
    description='High availability of CSR 1000v routers in Azure cloud',
    author='Richard Williams',
    author_email='richawil@cisco.com',
    scripts=['csr_azure_ha/client_api/node_event.py',
             'csr_azure_ha/client_api/clear_params.py',
             'csr_azure_ha/client_api/revert_nodes.sh',
             'csr_azure_ha/client_api/create_node.py',
             'csr_azure_ha/client_api/set_params.py',
             'csr_azure_ha/client_api/delete_node.py',
             'csr_azure_ha/client_api/show_node.py',
             'csr_azure_ha/client_api/py_caller.py',
             'csr_azure_ha/client_api/node_event',
             'csr_azure_ha/client_api/clear_params',
             'csr_azure_ha/client_api/create_node',
             'csr_azure_ha/client_api/set_params',
             'csr_azure_ha/client_api/delete_node',
             'csr_azure_ha/client_api/show_node'
            ],
    # use the URL to the github repo
    url='https://github4-chn.cisco.com/csr1000v-azure/' + project_name,
    download_url='https://github4-chn.cisco.com/csr1000v-azure/' + project_name + '/archive/' + \
        project_ver + '.tar.gz',
    keywords=['cisco', 'azure', 'csr1000v', 'csr', 'guestshell'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    license="MIT",
    include_package_data=True,
#    install_requires=['csr_azure_guestshell'],
    cmdclass={
        'install': PostInstallCommand,
    },
)
