try:
    import subprocess32 as sp
except ModuleNotFoundError:
    import subprocess as sp
import shlex

def run_command(cmd, input_=None):
    p = sp.run(
        shlex.split(cmd), input=input_, stdout=sp.PIPE, stderr=sp.PIPE,
        encoding='utf-8',
    )
    return p.stdout, p.stderr
