import os
from subprocess import call, check_output

os.chdir("/root/pykat")

call("git pull".split())

git_describe = str(check_output('git describe --tags'.split())).split("-")

vals = {
    "version": git_describe[0],
    "release": git_describe[1],
}

print(vals)

os.chdir("/root")            
call("fpm -s python -t rpm --no-python-dependencies --no-python-fix-dependencies --no-python-fix-name pykat/setup.py".split())
call("cp pykat-{version}.{release}-1.noarch.rpm /host".format(**vals).split())