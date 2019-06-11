from tridesclous import *
import numpy as np
import matplotlib.pyplot as plt
import time


#~ dirname = '/home/samuel/Documents/projet/tridesclous/example/tridesclous_olfactory_bulb/'
#~ chan_grp = 0

dirname = '/home/samuel/Documents/projet/DataSpikeSorting/GT 252/tdc_20170623_patch1/'
chan_grp = 1

#~ dirname = '/home/samuel/Documents/projet/DataSpikeSorting/spikesortingtest/tdc_silico_0/'
#~ chan_grp = 0

#~ dirname = '/home/samuel/Documents/projet/DataSpikeSorting/tridesclous_datasets/tdc_locust/'
#~ chan_grp = 0


#~ dirname = '/home/samuel/Documents/projet/DataSpikeSorting/tridesclous_datasets/tdc_olfactory_bulb/'
#~ chan_grp = 0

#~ dirname = '/home/samuel/Documents/projet/DataSpikeSorting/tridesclous_datasets/tdc_purkinje/'
#~ chan_grp = 0

#~ dirname = '/home/samuel/Documents/projet/DataSpikeSorting/tridesclous_datasets/tdc_striatum_rat/'
#~ chan_grp = 0

dataio = DataIO(dirname=dirname)



def debug_peeler():
    cc = CatalogueConstructor(dataio, chan_grp=chan_grp)
    
    print(cc.info)
    initial_catalogue = dataio.load_catalogue(chan_grp=chan_grp)
    print(initial_catalogue['n_left'])
    #~ exit()

    peeler = Peeler(dataio)
    
    peeler.change_params(catalogue=initial_catalogue, n_peel_level=2, chunksize=1024)
    
    t1 = time.perf_counter()
    peeler.run(chan_grp=chan_grp, duration=None)
    #~ peeler.run(chan_grp=chan_grp, duration=60.)
    t2 = time.perf_counter()
    print('peeler.run_loop', t2-t1)

    

def detect_anomalies():
    all_spikes = dataio.get_spikes(chan_grp=chan_grp)
    #~ print(spikes)
    labels = np.unique(all_spikes['label'])
    labels = labels[labels>=0]
    for label in labels:
        keep, = np.nonzero(all_spikes['label']==label)
        spikes = all_spikes[keep]
        spike_times = spikes['index'] / dataio.sample_rate
        
        print('#')
        print(label, spike_times.shape)
        
        isi = np.diff(spike_times)
        bad,  = np.nonzero(isi<0.001)
        print(bad.size)
        print(bad)
        print(keep[bad])
        print(isi[bad])
        print(spike_times[bad])
        fig, ax = plt.subplots()
        ax.hist(isi, bins=np.arange(0, 0.5, 0.001))
        ax.set_title('n_bad {}'.format(bad.size))
        plt.show()
        
        

#Bug cell 2
#~ #
#~ 2 (70,)
#~ 5
#~ [39 40 45 49 61]
#~ [14236 14239 16006 17671 21563]
#~ [  6.50000000e-04   5.00000000e-05   0.00000000e+00   0.00000000e+00
   #~ 1.00000000e-04]
#~ [ 11.76165  11.7623   13.21335  14.62885  17.9826 ]



#Silico 0      6.97693333
#~ #
#~ 0 (2688,)
#~ 34
#~ [  52  119  258  378  519  542  589  613  670  715  768 1150 1255 1397 1427
 #~ 1512 1600 1756 1817 1966 2051 2052 2068 2136 2140 2153 2233 2270 2414 2429
 #~ 2524 2533 2602 2614]
#~ [ 1454  3344  7212 10772 14680 15310 16646 17367 18999 20327 21956 32915
 #~ 36022 40188 40987 43487 46065 50495 52227 56649 59170 59173 59644 61607
 #~ 61689 62046 64307 65326 69621 69992 72756 72985 75115 75409]
#~ [  2.36666667e-03   1.00000000e-04   2.63333333e-03   1.00000000e-04
   #~ 1.96666667e-03   2.73333333e-03   3.36666667e-03   1.33333333e-04
   #~ 1.30000000e-03   1.00000000e-04   4.10000000e-03   2.16666667e-03
   #~ 3.86666667e-03   1.00000000e-04   1.00000000e-04   1.43333333e-03
   #~ 3.33333333e-05   1.46666667e-03   4.00000000e-03   3.33333333e-04
   #~ 4.66666667e-03   2.80000000e-03   1.33333333e-04   4.56666667e-03
   #~ 1.90000000e-03   4.36666667e-03   3.10000000e-03   3.96666667e-03
   #~ 2.20000000e-03   3.33333333e-05   3.30000000e-03   3.50000000e-03
   #~ 1.00000000e-04   2.96666667e-03]
#~ [   3.06923333    6.97693333   14.98206667   22.32683333   30.4337
   #~ 31.74023333   34.51153333   35.99216667   39.3829       42.12403333
   #~ 45.46306667   68.16946667   74.5726       83.0961       84.7772
   #~ 89.91766667   95.24046667  104.38763333  107.96356667  117.07113333
  #~ 122.20236667  122.20703333  123.1972      127.2075      127.3733
  #~ 128.12703333  132.8019      134.89423333  143.79736667  144.5897
  #~ 150.23836667  150.6981      155.03533333  155.6538    ]
    
    
    
#OB !!!!!!3.8175
#
#~ 4 (266,)
#~ 4
#~ [ 72 122 175 241]
#~ [1224 2244 3890 5587]
#~ [  0.00000000e+00   1.00000000e-04   0.00000000e+00   2.30000000e-03]
#~ [  3.8175   6.5705  10.0211  13.7436]


#striatum rat !!!!!!213.86555

#
#~ 0 (780,)
#~ 1
#~ [296]
#~ [1294]
#~ [  5.00000000e-05]
#~ [ 213.86555]


if __name__ == '__main__':
    debug_peeler()
    
    detect_anomalies()
    
    
    