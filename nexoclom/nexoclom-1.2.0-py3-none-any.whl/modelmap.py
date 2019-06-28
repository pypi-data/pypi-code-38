import glob
import subprocess

result = open('modelmap.dat', 'r')
pyfiles = glob.glob('**/*.py')
for pyf in pyfiles:
    out = subprocess.run(['grep', 'import', 'pyf'])
    if len(out.stdout) > 0:
        lines = out.split('\n')
        modules = []
        for l in lines:
            words = l.split(' ')
            for i,w in enumerate(words):
                if w == 'import':
                    modules.append(pyf)


result.close()
