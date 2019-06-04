import subprocess
import sys
import os
import shutil


def main(network):
    dirname = os.path.dirname(__file__)
    banner = open(os.path.join(dirname, 'banner.txt')).read()
    init = os.path.join(dirname, 'bash-init.sh')
    print(banner)

    shutil.copy(init, 'bash-init.sh')

    p = subprocess.Popen('bash --init-file bash-init.sh', shell=True, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    p.wait()
