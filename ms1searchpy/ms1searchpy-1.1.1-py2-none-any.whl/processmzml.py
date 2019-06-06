import ms_deisotope
import cPickle
from multiprocessing import Queue, Process, cpu_count

path_to_ms_file = '/home/mark/Denmark/mzml_profile/QHF2_02182_VG.mzML'
start_time = 0
end_time = 99999

reader = ms_deisotope.MSFileLoader(path_to_ms_file)
reader.start_from_scan(rt=start_time)
ms1_scans = []
print 'start cycle'

def worker(qin, qout, shift, step):
    maxval = len(qin)
    start = 0
    while start + shift < maxval:
        bunch = qin[start+shift]

        # while True:
            # bunch = next(reader)
        #     print bunch.precursor
            # print bunch.precursor.scan_id, bunch.precursor.scan_time
        averaged = bunch.precursor.average(1)
        averaged.pick_peaks()
        averaged.deconvolute(averagine=ms_deisotope.peptide,
                            scorer=ms_deisotope.PenalizedMSDeconVFitter(20., 2.),
                            max_missed_peaks=3, truncate_after=0.95)
    #     print averaged.pack()
        qout.put(averaged.pack())
            # ms1_scans.append(averaged.pack())

        # if result:
        #     qout.put(result)
        start += step
    qout.put(None)
qout = Queue()
count = 0

# while True:
qin = []
while True:
    try:
        bunch = next(reader)
        qin.append(bunch)
    except:
        break
# qin = list(islice(it, 500000))
# if not len(qin):
#     break
# print 'Loaded 500000 items. Ending cycle.'
procs = []
n = 12
for _ in range(n):
    p = Process(target=worker, args=(qin, qout, _, n))
    p.start()
    procs.append(p)

count = len(qin)

for _ in range(n):
    for item in iter(qout.get, None):
        ms1_scans.append(item)

for p in procs:
    p.join()

print 'Cycle finished.'





# while True:
#     bunch = next(reader)
# #     print bunch.precursor
#     print bunch.precursor.scan_id, bunch.precursor.scan_time
#     averaged = bunch.precursor.average(1)
#     averaged.pick_peaks()
#     averaged.deconvolute(averagine=ms_deisotope.peptide,
#                          scorer=ms_deisotope.PenalizedMSDeconVFitter(20., 2.),
#                          max_missed_peaks=3, truncate_after=0.95)
# #     print averaged.pack()
#     ms1_scans.append(averaged.pack())
#     if bunch.precursor.scan_time > end_time:
#         break

# # now all of the MS1 scans of interest are in `ms1_scans`

cPickle.dump(ms1_scans, open('/home/mark/JK.pickle', 'w'))

from ms_deisotope.feature_map import lcms_feature, feature_map, feature_fit

def aggregate_features(ms1_scans, aggregation_ppm_error=1e-5, min_length=3):
    '''
    Given a list of MS1 scans, aggregate peaks with close neutral masses over time,
    and construct a collection of MS1 features for each mass-charge pair. Returns a 
    feature_map.DeconvolutedLCMSFeatureMap object which is a Sequence-like object
    with methods for searching for features by neutral mass.
    '''
    peak_pairs = []
    for scan in ms1_scans:
        for peak in scan:
            peak_pairs.append((peak, scan.scan_time))
    peak_pairs = sorted(peak_pairs, key=lambda x: x[0].neutral_mass)

    features = dict()
    running_mean = 1
    running_total = 0
    running_weight = 0
    running_peaks = []

    for peak, scan_time in peak_pairs:
        if abs((peak.neutral_mass - running_mean) / running_mean) > aggregation_ppm_error:
            if running_peaks:
                features[running_mean] = running_peaks
            running_mean = peak.neutral_mass
            running_total = peak.neutral_mass * peak.intensity
            running_weight = peak.intensity
            running_peaks = [(peak, scan_time)]
        else:
            running_total += peak.neutral_mass * peak.intensity
            running_weight += peak.intensity
            running_mean = running_total / running_weight
            running_peaks.append((peak, scan_time))
    finalized_features = list()
    for key, value in features.items():
        if len(value) < min_length:
            continue
        charge_to_feature = dict()
        for peak, time in value:
            try:
                feature = charge_to_feature[peak.charge]
            except KeyError:
                feature = feature_fit.DeconvolutedLCMSFeature(charge=peak.charge)
                charge_to_feature[peak.charge] = feature
            feature.insert(peak, time)
        for feature in charge_to_feature.values():
            finalized_features.append(feature)
    return feature_map.DeconvolutedLCMSFeatureMap(finalized_features)

fmap = aggregate_features(ms1_scans, aggregation_ppm_error= 1e-5)

out = open('/home/mark/JK.features.tsv', 'w')
header = [
    'massCalib',
    'rtApex',
    'charge',
    'nIsotopes',
    'intensityApex',
    'nScans'
]
out.write('\t'.join(header) + '\n')
for feauture in fmap.features:
    nmass = feauture.neutral_mass
    RT = feauture.apex_time
    ch = feauture.charge
    I = feauture.intensity
    if I >= 1 and ch > 1:
        out.write('\t'.join(str(z) for z in [nmass, RT, ch, 5, I, 5]) + '\n')
out.close()
    
#         mass_ind = header.index('massCalib')
#         RT_ind = header.index('rtApex')
#         ch_ind = header.index('charge')
#         nIsotopes_ind = header.index('nIsotopes')
#         Int_ind = header.index('intensityApex')
#         nScans_ind = header.index('nScans')