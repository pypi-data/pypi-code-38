import microlab
import argparse

'''' Parser Settings '''''
parser = argparse.ArgumentParser(description='Microlab Node v:{}'.format(microlab.__version__))

python = parser.add_argument_group()
python.title = 'Python'
python.add_argument('--python',        action='store_true', help='python location in the environment')
python.add_argument('--pip',           action='store_true', help='pip location in the environment')
python.add_argument('--pip-install',   type=str,            help='install a python module from pipy')
python.add_argument('--pip-uninstall', type=str,            help='uninstall a python module from pipy')
python.add_argument('--pip-upgrade',   type=str,            help='upgrade a python module from pipy')

# Need parameters
workspace = parser.add_argument_group()
workspace.title = 'Workspace'
workspace.add_argument('--status', action='store_true',  help='show the status of workspace')
workspace.add_argument('--tests', action='store_true',  help='show the tests of workspace')
workspace.add_argument('--packages', action='store_true', help='show the packages of workspace')
workspace.add_argument('--create-workspace',   type=str,   help='create new workspace')
workspace.add_argument('--clean-workspace',   action='store_true',   help='clean the workspace')
workspace.add_argument('--rename',             type=str,   help='rename the workspace')
workspace.add_argument('--reversion',          type=str,   help='reversion the workspace')

package = parser.add_argument_group()
package.title = 'Package'
package.add_argument('--create-package',     type=str,   help='create new package')
package.add_argument('--install',            type=str,   help='install the package of workspace')
package.add_argument('--uninstall',          type=str,   help='uninstall the package of workspace')
package.add_argument('--start',              type=str,   help='start the package of workspace')
package.add_argument('--test',               type=str,   help='start a test')

# Boolean parameter
plugin = parser.add_argument_group()
plugin.title = 'Information'
plugin.add_argument('--software', action='store_true', help='software information')
plugin.add_argument('--network', action='store_true', help='network information on host')

application = parser.add_argument_group()
application.title = 'Application'
application.add_argument('--monitor',   action='store_true', help='monitor the hardware')
application.add_argument('--scan',      action='store_true', help='scan node network')

power = parser.add_argument_group()
power.title = 'Power'
power.add_argument('--shutdown', action='store_true', help='shutdown the device')
power.add_argument('--reboot', action='store_true', help='reboot the device')
power.add_argument('--cancel', action='store_true', help='cancel the shutdown or reboot device')


arguments = parser.parse_args()

if __name__ == '__main__':
    node = microlab.Node()

    if arguments.scan:
            node.scan()

    if arguments.pip:
        print(node.pip())

    if arguments.python:
        print(node.python())


    if arguments.pip_install is not None:
        node.pip_install(module=arguments.pip_install)

    if arguments.pip_uninstall is not None:
        node.pip_uninstall(module=arguments.pip_uninstall)

    if arguments.pip_upgrade is not None:
        node.pip_upgrade(module=arguments.pip_upgrade)


    if arguments.reboot:
        node.reboot()

    if arguments.shutdown:
        node.shutdown()

    if arguments.cancel:
        node.cancel()

    if arguments.software:
        node.software()

    if arguments.monitor:
        node.monitor()

    if arguments.network:
        node.network()

    if arguments.status:
        node.workspace_status()

    if arguments.packages:
        node.workspace_packages()

    if arguments.tests:
        node.workspace_tests()

    if arguments.create_workspace is not None:
        node.workspace_create(name=arguments.create_workspace)

    if arguments.clean_workspace:
        node.workspace_clean()

    if arguments.rename is not None:
        node.workspace_rename(name=arguments.rename)

    if arguments.reversion is not None:
        node.workspace_reversion(new_version=arguments.reversion)

    if arguments.create_package is not None:
        node.package_create(package={'name':arguments.create_package,
                                'arguments': '',
                                'directory': '',
                                'executor': 'main.py',
                                'installer': '-m pip install -r requirements.txt',
                                'uninstaller': '-m pip uninstall -r requirements.txt',
                                })

    if arguments.install is not None:
        node.package_install(arg=arguments.install)

    if arguments.uninstall is not None:
        node.package_uninstall(arg=arguments.uninstall)

    if arguments.start is not None:
        node.package_start(arg=arguments.start)

    if arguments.test is not None:
        if arguments.test == 'all':
            for test in node.microlab_tests:
                if test != 'monitoring':
                    node.start_microlab_test(arg=test)
        else:
            node.start_microlab_test(arg=arguments.test)
