try:
    import subprocess32 as sp
except ModuleNotFoundError:
    import subprocess as sp
import shlex

def run_command(cmd):
    p = sp.run(shlex.split(cmd), stdout=sp.PIPE, stderr=sp.PIPE)
    return p.stdout, p.stderr
