#!/usr/bin/env python

import sys

# import pprint


def mean(data):
    return sum(data) / float(len(data))


def ssd(data):
    # sum of square deviations
    m = mean(data)
    return sum((x - m)**2 for x in data)


def stddev(data, ddof=1):
    # ddof == 0: population standard deviation
    # ddof == 1: sample standard deviation

    return (ssd(data) / (len(data) - ddof))**0.5


data = dict()

for fname in sys.argv[1:]:
    data[fname] = dict()
    sizes       = set()

    with open(fname, 'r') as fin:

        for line in fin.readlines():
            ldata = line.split()
            n     = ldata[0]
          # print n
            sizes.add(int(n))
            ldata = ldata[1:]
            if n not in data[fname]:
                data[fname][n] = list()
                for i in range(len(ldata)):
                    data[fname][n].append(list())
            for i in range(len(ldata)):
                data[fname][n][i].append(float(ldata[i]))

# pprint.pprint(data)

for fname in data:
    print
    labels = fname.split('.')[0].split('_')
    oname  = '%s.%s' % (labels[0], labels[1])
    print oname, 
    with open('data/%s' % oname, 'w') as fout:
        for n in sorted(sizes):
            print n, 
            fout.write('%5d' % n)
            for i in range(9):
                tmp = data[fname][str(n)][i]
                fout.write('\t%8.2f\t%6.2f' % (mean(tmp), stddev(tmp)))
            fout.write('\n')

print

