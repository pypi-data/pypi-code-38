import subprocess
p = subprocess.Popen('ll', stdout=subprocess.PIPE)
while p.poll() == None:
    print p.stdout.readline()
print '123'
print p.stdout.readlines()
