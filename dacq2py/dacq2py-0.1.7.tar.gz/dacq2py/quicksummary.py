#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 17:16:15 2018

@author: robin
"""

import yaml
import os
from dacq2py import OptoCluster
import numpy as np

d=yaml.load_all(open(os.path.join('/home/robin/Dropbox/Science/Analysis/Mouse_optogenetics/','SST_chr2_stm_trials_tets_and_clusts.yaml')))

while d:
    tr = d.next()
    fnames = tr.keys()
    for fname in fnames:
        T = OptoCluster.OptoClusterSummary(fname)
        if np.logical_and(np.sum(np.sum(T.TETRODE[1].waveforms,0),1)[0] == 0, np.sum(np.sum(T.TETRODE[2].waveforms,0),1)[0] == 0):
            print "{}".format(T.filename_root)
#            for tcs in zip(tr[fname]['Tetrodes'], tr[fname]['Clusters']):
#                tet = tcs[0]
#                clust = tcs[1]
#                before, after, change = T.getFiringRateDuringLaser(tet,clust,10)
#                if ( after > before ):
#                    print "after = {}, before = {}".format(after, before)
#                print "{} , t:{}, c:{}, ratio:{}".format(fname, tet, clust, )
import os
from glob import glob
import numpy as np
from dacq2py import OptoCluster

def get_tetrode_sum(OptoClusterSummary, tet_num):
    answer = False
    try:
        tet_sum = np.sum(np.sum(T.TETRODE[tet_num].waveforms,0),1)
        if tet_sum[0] == 0 and tet_sum[1] == 0:
            answer = True
    except AttributeError:
        pass
    except IOError:
        pass
    except ValueError:
        pass
    except IndexError:
        pass
    return answer
        

for dirpath, dirnames, filenames in os.walk('/home/robin/Dropbox/Science/Recordings'):
    for thisdir in dirnames:
        if 'OpenEphys' not in dirpath:
            if (thisdir.startswith('M')):
                if (thisdir[1].isdigit()): # gets us into M[xxx] type directories
                    axona_dir = os.path.join(dirpath, thisdir)
                    set_files = glob(axona_dir + "/*.set")
                    for fname in set_files:
                        fname = fname[:-4]
                        T = OptoCluster.OptoClusterSummary(fname)
                        tet_sums = []
                        for i in range(1, 5):
                            tet_sums.append(get_tetrode_sum(T, i))
                        if any(tet_sums):
                            print fname