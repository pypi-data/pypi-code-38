import angreal
import os
import stat
import subprocess
import getpass

here = os.path.dirname(__file__)

pypirc = os.path.expanduser(os.path.join('~', '.pypirc'))
requirements = os.path.join(here, '..', 'requirements', 'dev.txt')
setup_py = os.path.join(here, '..', 'setup.py')


@angreal.command()
def angreal_cmd():
    """

    Release to pypi.

    """

    if not os.path.isfile(pypirc):
        rv = input('No pypirc file detected do you wish to continue upload ? y/[n]')
        if rv == 'y':
            pypi_un = input('What is your pypi user name ?')
            pypi_pw = getpass.getpass('What is your pypi password ?')
            with open(pypirc, 'w') as f:
                print('[server-login]', file=f)
                print('username: {}'.format(pypi_un), file=f)
                print('password: {}'.format(pypi_pw), file=f)
            os.chmod(pypirc, stat.S_IRUSR)

        pypi_rv = subprocess.run('python {} bdist_wheel upload'.format(setup_py),
                                 shell=True, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT)

        if pypi_rv.returncode == 0:
            angreal.win('{{angreal._cleaned_name}} released to pypi.')
        else:
            angreal.error('Release failed.')
            exit(2)
