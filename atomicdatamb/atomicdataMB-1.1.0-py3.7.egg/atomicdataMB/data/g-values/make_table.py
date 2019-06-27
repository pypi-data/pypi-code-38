newfile = open('Ca.4227.KillenXXXX.dat', 'w')
newfile.write('a = 0.354\n')
newfile.write('vel     :       4227\n')

for l in open('Ca_gval_50_354.txt', 'r').readlines():
    a = l.split(' ')
    b = tuple(c for c in a if c != '')
    newfile.write('%s  :  %s' % b)
newfile.close()



