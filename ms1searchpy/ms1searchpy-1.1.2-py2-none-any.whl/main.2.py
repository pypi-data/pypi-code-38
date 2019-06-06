import os
import cPickle
import utils
import numpy as np
from scipy.stats import binom, scoreatpercentile
from scipy.optimize import curve_fit
from scipy import exp
import operator
from copy import copy, deepcopy
from collections import defaultdict, Counter
import re
from pyteomics import parser, mass, fasta, auxiliary as aux, achrom
try:
    from pyteomics import cmass
except ImportError:
    cmass = mass
import subprocess
from sklearn import linear_model
import tempfile
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
try:
    import seaborn
    seaborn.set(rc={'axes.facecolor':'#ffffff'})
    seaborn.set_style('whitegrid')
except:
    pass


def calc_F(X1, n, lenF):
    F = np.zeros(lenF, dtype=np.float64)
    F[0] = 1
    # inrange = range(lenF-1, -1, -1)
    for j in xrange(0, n, 1):
        diffv = X1[j]
        ar_shift = shift5(F, X1[j], 0)
        F = F + ar_shift
        # for jj in inrange[:-diffv]:
        #     F[jj] += F[jj-diffv]
    return F

def shift5(arr, num, fill_value=np.nan):
    result = np.empty_like(arr, dtype=np.float64)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result = arr
    return result

def get_RCs2(sequences, RTs, lcp = -0.21,
            term_aa = False, **kwargs):
    labels = kwargs.get('labels')

    # Make a list of all amino acids present in the sample.
    peptide_dicts = [
            parser.amino_acid_composition(peptide, False, term_aa,
                               allow_unknown_modifications=True,
                               labels=labels)
            if not isinstance(peptide, dict) else peptide
        for peptide in sequences]

    detected_amino_acids = {aa for peptide_dict in peptide_dicts
                                for aa in peptide_dict}

    composition_array = []
    for pdict in peptide_dicts:
        loglen = np.log(parser.length(pdict))
        composition_array.append([pdict.get(aa, 0.)
             * (1. + lcp * loglen)
               for aa in detected_amino_acids] + [1.])

    if term_aa:
        for term_label in ['nterm', 'cterm']:
            normalizing_peptide = []
            for aa in detected_amino_acids:
                if aa.startswith(term_label):
                    normalizing_peptide.append(1.0)
                elif (term_label+aa) in detected_amino_acids:
                    normalizing_peptide.append(-1.0)
                else:
                    normalizing_peptide.append(0.0)
            normalizing_peptide.append(0.0)
            composition_array.append(normalizing_peptide)
            RTs.append(0.0)
    
    model_ransac = linear_model.RANSACRegressor(linear_model.LinearRegression(n_jobs=12), min_samples=0.5, max_trials=5000, random_state=42)
    model_ransac.fit(np.array(composition_array), np.array(RTs))
    RCs = model_ransac.estimator_.coef_
    if term_aa:
        for term_label in ['nterm', 'cterm']:
            RTs.pop()

    # Form output.
    RC_dict = {}
    RC_dict['aa'] = dict(
        zip(list(detected_amino_acids),
            RCs[:len(detected_amino_acids)]))
    RC_dict['aa'][parser.std_nterm] = 0.0
    RC_dict['aa'][parser.std_cterm] = 0.0
    RC_dict['const'] = RCs[len(detected_amino_acids)]
    RC_dict['lcp'] = lcp

    # Find remaining terminal RCs.
    if term_aa:
        for term_label in ['nterm', 'cterm']:
            # Check if there are terminal RCs remaining undefined.
            undefined_term_RCs = [aa for aa in RC_dict['aa']
                                if aa[1:5] != 'term'
                                and term_label + aa not in RC_dict['aa']]
            if not undefined_term_RCs:
                continue

            # Find a linear relationship between internal and terminal RCs.
            defined_term_RCs = [aa for aa in RC_dict['aa']
                              if aa[1:5] != 'term'
                              and term_label + aa in RC_dict['aa']]

            a, b, r, stderr = linear_regression(
                [RC_dict['aa'][aa] for aa in defined_term_RCs],
                [RC_dict['aa'][term_label+aa] for aa in defined_term_RCs])

            # Define missing terminal RCs using this linear equation.
            for aa in undefined_term_RCs:
                RC_dict['aa'][term_label + aa] = a * RC_dict['aa'][aa] + b
    inlier_mask = model_ransac.inlier_mask_
    outlier_mask = np.logical_not(inlier_mask)
    return RC_dict, outlier_mask


def process_file(args):
    # fname = args['file']
    # ftype = fname.rsplit('.', 1)[-1].lower()
    utils.seen_target.clear()
    utils.seen_decoy.clear()
    return process_peptides(args)


def peptide_processor(peptide, **kwargs):
    seqm = peptide
    results = []
    m = cmass.fast_mass(seqm, aa_mass=kwargs['aa_mass']) + kwargs['aa_mass'].get('Nterm', 0) + kwargs['aa_mass'].get('Cterm', 0)
    acc_l = kwargs['acc_l']
    acc_r = kwargs['acc_r']
    dm_l = acc_l * m / 1.0e6
    dm_r = acc_r * m / 1.0e6
    start = nmasses.searchsorted(m - dm_l)
    end = nmasses.searchsorted(m + dm_r)
    idx = set(range(start, end))
    for i in idx:
        peak_id = ids[i]
        I = Is[i]
        massdiff = (m - nmasses[i]) / m * 1e6
        results.append((seqm, massdiff, rts[i], peak_id, I, Scans[i], Isotopes[i], mzraw[i], avraw[i], charges[i]))
    return results


def prepare_peptide_processor(fname, args):
    global nmasses
    global rts
    global charges
    global ids
    global Is
    global Scans
    global Isotopes
    global mzraw
    global avraw
    nmasses = []
    rts = []
    charges = []
    ids = []
    Is = []
    Scans = []
    Isotopes = []
    mzraw = []
    avraw = []

    min_ch = args['cmin']
    max_ch = args['cmax']

    min_isotopes = args['i']
    min_scans = args['sc']

    print 'Reading spectra ...'
    for m, RT, c, peak_id, I, nScans, nIsotopes, mzr, avr in utils.iterate_spectra(fname, min_ch, max_ch, min_isotopes, min_scans):
        nmasses.append(m)
        rts.append(RT)
        charges.append(c)
        ids.append(peak_id)
        Is.append(I)
        Scans.append(nScans)
        Isotopes.append(nIsotopes)
        mzraw.append(mzr)
        avraw.append(avr)

    i = np.argsort(nmasses)
    nmasses = np.array(nmasses)[i]
    rts = np.array(rts)[i]
    charges = np.array(charges)[i]
    ids = np.array(ids)[i]
    Is = np.array(Is)[i]
    Scans = np.array(Scans)[i]
    Isotopes = np.array(Isotopes)[i]
    mzraw = np.array(mzraw)[i]
    avraw = np.array(avraw)[i]

    fmods = args['fmods']
    aa_mass = mass.std_aa_mass
    if fmods:
        for mod in fmods.split(','):
            m, aa = mod.split('@')
            if aa == '[':
                aa_mass['Nterm'] = float(m)
            elif aa == ']':
                aa_mass['Cterm'] = float(m)
            else:
                aa_mass[aa] += float(m)

    acc_l = args['ptol']
    acc_r = args['ptol']

    return {'aa_mass': aa_mass, 'acc_l': acc_l, 'acc_r': acc_r, 'args': args}


def peptide_processor_iter_isoforms(peptide, **kwargs):
    out = []
    out.append(peptide_processor(peptide, **kwargs))
    return out

def get_results(ms1results):
    resdict = dict()
    labels = [
        'seqs',
        'md',
        'rt',
        'ids',
        'Is',
        'Scans',
        'Isotopes',
        'mzraw',
        'av',
        'ch'
    ]
    for label, val in zip(labels, zip(*ms1results)):
        resdict[label] = np.array(val)
    return resdict

def filter_results(resultdict, idx):
    for label in resultdict.keys():
        resultdict[label] = resultdict[label][idx]
    return resultdict

def process_peptides(args):
    fname = args['file']
    fdr = args['fdr'] / 100
    try:
        outpath = args['outpath']
    except:
        outpath = False

    def calc_sf_all(v, n, p):
        sf_values = np.log10(1 / binom.sf(v, n, p))
        sf_values[np.isinf(sf_values)] = 1
        return sf_values

    elude_path = args['elude']
    elude_path = elude_path.strip()

    ms1results = []
    peps = utils.peptide_gen(args)
    kwargs = prepare_peptide_processor(fname, args)
    func = peptide_processor_iter_isoforms
    print 'Running the search ...'
    for y in utils.multimap(1, func, peps, **kwargs):
        for result in y:
            if len(result):
                ms1results.extend(result)

    prefix = args['prefix']
    protsN, pept_prot, protsNfull = utils.get_prot_pept_map(args)

    resdict = get_results(ms1results)
    del ms1results

    isdecoy = lambda x: x[0].startswith(prefix)
    isdecoy_key = lambda x: x.startswith(prefix)
    escore = lambda x: -x[1]

    p1 = set(resdict['seqs'])

    if len(p1):
        prots_spc2 = defaultdict(set)
        for pep, proteins in pept_prot.iteritems():
            if pep in p1:
                for protein in proteins:
                    prots_spc2[protein].add(pep)

        for k in protsN:
            if k not in prots_spc2:
                prots_spc2[k] = set([])
        prots_spc = dict((k, len(v)) for k, v in prots_spc2.iteritems())

        names_arr = np.array(prots_spc.keys())
        v_arr = np.array(prots_spc.values())
        n_arr = np.array([protsN[k] for k in prots_spc])

        top100decoy_score = [prots_spc.get(dprot, 0) for dprot in protsN if isdecoy_key(dprot)]
        top100decoy_N = [val for key, val in protsN.items() if isdecoy_key(key)]
        p = np.mean(top100decoy_score) / np.mean(top100decoy_N)
        print 'p=%s' % (np.mean(top100decoy_score) / np.mean(top100decoy_N))

        prots_spc = dict()
        all_pvals = calc_sf_all(v_arr, n_arr, p)
        for idx, k in enumerate(names_arr):
            prots_spc[k] = all_pvals[idx]

        checked = set()
        for k, v in prots_spc.items():
            if k not in checked:
                if isdecoy_key(k):
                    if prots_spc.get(k.replace(prefix, ''), -1e6) > v:
                        del prots_spc[k]
                        checked.add(k.replace(prefix, ''))
                else:
                    if prots_spc.get(prefix + k, -1e6) > v:
                        del prots_spc[k]
                        checked.add(prefix + k)

        filtered_prots = aux.filter(prots_spc.items(), fdr=fdr, key=escore, is_decoy=isdecoy, remove_decoy=True, formula=1,
                                    full_output=True)

        identified_proteins = 0

        for x in filtered_prots:
            identified_proteins += 1
        print 'results for default search: number of identified proteins = %d' % (identified_proteins, )

        print 'Running mass recalibration...'

        true_md = []
        true_isotopes = []
        true_seqs = []
        true_prots = set(x[0] for x in filtered_prots)
        for pep, proteins in pept_prot.iteritems():
            if any(protein in true_prots for protein in proteins):
                true_seqs.append(pep)

        e_ind = np.in1d(resdict['seqs'], true_seqs)

        true_seqs = resdict['seqs'][e_ind]
        true_md.extend(resdict['md'][e_ind])
        true_md = np.array(true_md)
        true_isotopes.extend(resdict['Isotopes'][e_ind])
        true_isotopes = np.array(true_isotopes)

        e_ind = true_isotopes >= 4
        true_md = true_md[e_ind]
        true_seqs = true_seqs[e_ind]

        mass_left = args['ptol']
        mass_right = args['ptol']

        def noisygaus(x, a, x0, sigma, b):
            return a * exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + b

        def calibrate_mass(bwidth, mass_left, mass_right, true_md):

            bbins = np.arange(-mass_left, mass_right, bwidth)
            H1, b1 = np.histogram(true_md, bins=bbins)
            b1 = b1 + bwidth
            b1 = b1[:-1]


            popt, pcov = curve_fit(noisygaus, b1, H1, p0=[1, np.median(true_md), 1, 1])
            mass_shift, mass_sigma = popt[1], abs(popt[2])
            return mass_shift, mass_sigma, pcov[0][0]

        mass_shift, mass_sigma, covvalue = calibrate_mass(0.001, mass_left, mass_right, true_md)
        if np.isinf(covvalue):
            mass_shift, mass_sigma, covvalue = calibrate_mass(0.01, mass_left, mass_right, true_md)
        print 'Calibrated mass shift: ', mass_shift
        print 'Calibrated mass sigma in ppm: ', mass_sigma

        e_all = abs(resdict['md'] - mass_shift) / (mass_sigma)
        r = 3.0
        e_ind = e_all <= r
        resdict = filter_results(resdict, e_ind)

        zs_all = e_all[e_ind] ** 2

        p1 = set(resdict['seqs'])

        prots_spc2 = defaultdict(set)
        for pep, proteins in pept_prot.iteritems():
            if pep in p1:
                for protein in proteins:
                    prots_spc2[protein].add(pep)

        for k in protsN:
            if k not in prots_spc2:
                prots_spc2[k] = set([])
        prots_spc = dict((k, len(v)) for k, v in prots_spc2.iteritems())

        names_arr = np.array(prots_spc.keys())
        v_arr = np.array(prots_spc.values())
        n_arr = np.array([protsN[k] for k in prots_spc])

        top100decoy_score = [prots_spc.get(dprot, 0) for dprot in protsN if isdecoy_key(dprot)]
        top100decoy_N = [val for key, val in protsN.items() if isdecoy_key(key)]
        p = np.mean(top100decoy_score) / np.mean(top100decoy_N)
        print 'p=%s' % (np.mean(top100decoy_score) / np.mean(top100decoy_N))

        prots_spc = dict()
        all_pvals = calc_sf_all(v_arr, n_arr, p)
        for idx, k in enumerate(names_arr):
            prots_spc[k] = all_pvals[idx]

        checked = set()
        for k, v in prots_spc.items():
            if k not in checked:
                if isdecoy_key(k):
                    if prots_spc.get(k.replace(prefix, ''), -1e6) > v:
                        del prots_spc[k]
                        checked.add(k.replace(prefix, ''))
                else:
                    if prots_spc.get(prefix + k, -1e6) > v:
                        del prots_spc[k]
                        checked.add(prefix + k)

        filtered_prots = aux.filter(prots_spc.items(), fdr=fdr, key=escore, is_decoy=isdecoy, remove_decoy=True, formula=1,
                                    full_output=True)

        identified_proteins = 0

        for x in filtered_prots:
            identified_proteins += 1
        print 'results for default search after mass calibration: number of identified proteins = %d' % (identified_proteins, )



        print 'Running RT prediction...'
        true_seqs = []
        true_rt = []
        true_isotopes = []
        true_prots = set(x[0] for x in filtered_prots)#[:5])
        for pep, proteins in pept_prot.iteritems():
            if any(protein in true_prots for protein in proteins):
                true_seqs.append(pep)
        e_ind = np.in1d(resdict['seqs'], true_seqs)


        true_seqs = resdict['seqs'][e_ind]
        true_rt.extend(resdict['rt'][e_ind])
        true_rt = np.array(true_rt)
        true_isotopes.extend(resdict['Isotopes'][e_ind])
        true_isotopes = np.array(true_isotopes)

        e_ind = true_isotopes >= 4
        true_seqs = true_seqs[e_ind]
        true_rt = true_rt[e_ind]
        true_isotopes = true_isotopes[e_ind]

        best_seq = defaultdict(list)
        newseqs = []
        newRTs = []
        for seq, RT in zip(true_seqs, true_rt):
            best_seq[seq].append(RT)
        for k, v in best_seq.items():
            newseqs.append(k)
            newRTs.append(np.median(v))
        true_seqs = np.array(newseqs)
        true_rt = np.array(newRTs)

        RC, outmask = get_RCs2(true_seqs, true_rt)

        if elude_path:
            outtrain = tempfile.NamedTemporaryFile(suffix='.txt')
            outres = tempfile.NamedTemporaryFile(suffix='.txt')
            outres_name = outres.name
            outres.close()
            ns = true_seqs[~outmask]
            nr = true_rt[~outmask]
            ll = len(ns)
            for seq, RT in zip(ns[:ll], nr[:ll]):
                outtrain.write(seq + '\t' + str(RT) + '\n')
            outtrain.flush()

            subprocess.call([elude_path, '-t', outtrain.name, '-e', outtrain.name, '-a', '-g', '-o', outres_name])
            pepdict = dict()
            train_RT = []
            train_seq = []
            for x in open(outres_name).readlines()[3:]:
                seq, RT, RTexp = x.strip().split('\t')
                pepdict[seq] = float(RT)
                train_seq.append(seq)
                train_RT.append(float(RTexp))
            train_RT = np.array(train_RT)
            RT_pred = np.array([pepdict[s] for s in train_seq])
            aa, bb, RR, ss = aux.linear_regression(RT_pred, train_RT)
        else:
            RC = achrom.get_RCs_vary_lcp(true_seqs[~outmask], true_rt[~outmask])
            RT_pred = np.array([achrom.calculate_RT(s, RC) for s in true_seqs])
            aa, bb, RR, ss = aux.linear_regression(RT_pred, true_rt)
        print aa, bb, RR, ss


        best_sigma = ss
        RT_sigma = best_sigma

    else:
        print 'No matches found'

    p1 = set(resdict['seqs'])

    pepdict = dict()    
    if elude_path:
        outtest = tempfile.NamedTemporaryFile(suffix='.txt')
        for seq in p1:
            outtest.write(seq + '\n')
        outtest.flush()

        subprocess.call([elude_path, '-t', outtrain.name, '-e', outtest.name, '-a', '-o', outres_name])
        for x in open(outres_name).readlines()[3:]:
            seq, RT = x.strip().split('\t')
            pepdict[seq] = float(RT)
        outtest.close()
        outtrain.close()
    else:
        for seq in p1:
            pepdict[seq] = achrom.calculate_RT(seq, RC)
    rt_pred = np.array([pepdict[s] for s in resdict['seqs']])
    rt_diff = resdict['rt'] - rt_pred
    e_all = (rt_diff) ** 2 / (RT_sigma ** 2)
    zs_all = zs_all + e_all
    r = 9.0
    e_ind = e_all <= r
    resdict = filter_results(resdict, e_ind)
    rt_diff = rt_diff[e_ind]
    zs_all = zs_all[e_ind]

    e_ind = zs_all <= args['rtt'] ** 2
    resdict = filter_results(resdict, e_ind)
    rt_diff = rt_diff[e_ind]
    zs_all = zs_all[e_ind]


    if outpath:
        base_out_name = os.path.splitext(os.path.join(outpath, os.path.basename(fname)))[0]
    else:
        base_out_name = os.path.splitext(fname)[0]

    with open(base_out_name + '_protsN.csv', 'w') as output:
        output.write('dbname\ttheor peptides\n')
        for k, v in protsN.items():
            output.write('\t'.join((k, str(v))) + '\n')
   
    with open(base_out_name + '_PFMs.csv', 'w') as output:
        output.write('sequence\tmass diff\tRT diff\tpeak_id\tIntensity\tnScans\tnIsotopes\tproteins\tm/z\tRT\taveragineCorr\tcharge\n')
        for seq, md, rtd, peak_id, I, nScans, nIsotopes, mzr, rtr, av, ch in zip(resdict['seqs'], resdict['md'], rt_diff, resdict['ids'], resdict['Is'], resdict['Scans'], resdict['Isotopes'], resdict['mzraw'], resdict['rt'], resdict['av'], resdict['ch']):
            output.write('\t'.join((seq, str(md), str(rtd), str(peak_id), str(I), str(nScans), str(nIsotopes), ';'.join(pept_prot[seq]), str(mzr), str(rtr), str(av), str(ch))) + '\n')
            
    p1 = set(resdict['seqs'])

    pep_pid = defaultdict(set)
    pid_pep = defaultdict(set)
    for pep, pid in zip(resdict['seqs'], resdict['ids']):
        pep_pid[pep].add(pid)
        pid_pep[pid].add(pep)

    if len(p1):
        prots_spc_final = dict()
        prots_spc_copy = False
        banned_dict = dict()
        prots_spc2 = False
        unstable_prots = set()
        p0 = False

        while(len(p1)):
            if not prots_spc2:
                prots_spc2 = defaultdict(set)
                for pep, proteins in pept_prot.iteritems():
                    if pep in p1:
                        for protein in proteins:
                            prots_spc2[protein].add(pep)

                for k in protsN:
                    if k not in prots_spc2:
                        prots_spc2[k] = set([])
                unstable_prots = set(prots_spc2.keys())
            tmp_spc_new = dict((k, sum(banned_dict.get(l, 1) for l in v) if k in unstable_prots else tmp_spc.get(k, 0)) for k, v in prots_spc2.iteritems())
            tmp_spc = tmp_spc_new
            prots_spc = tmp_spc_new
            if not prots_spc_copy:
                prots_spc_copy = deepcopy(prots_spc)

            names_arr = np.array(prots_spc.keys())
            # print len(v_arr), np.sum(v_arr == np.array(prots_spc.values()))#sum(zzz1 == zzz2 for zzz1, zzz2 in zip(v_arr, np.array(prots_spc.values())))
            v_arr = np.array(prots_spc.values())
            n_arr = np.array([protsN[k] for k in prots_spc])
            # l_list = 

            top100decoy_score = [prots_spc.get(dprot, 0) for dprot in protsN if isdecoy_key(dprot)]
            top100decoy_N = [val for key, val in protsN.items() if isdecoy_key(key)]
            p = np.mean(top100decoy_score) / np.mean(top100decoy_N)
            if not p0:
                p0 = float(p)


                # with open('/home/mark/tmp2.pickle', 'w') as tmppickle:
                #     cPickle.dump([prots_spc2, banned_dict, protsNfull], tmppickle)


                # with open('/home/mark/tmp.pickle', 'w') as tmppickle:
                #     cPickle.dump([v_arr, n_arr, p, names_arr], tmppickle)

                # with open('/home/mark/tmp3.pickle', 'w') as tmppickle:
                #     cPickle.dump(resdict, tmppickle)


            target_set = set()
            for k, v in protsNfull.iteritems():
                if not isdecoy_key(k):
                    target_set.update(v)

            md_all = resdict['md']
            sq_all = resdict['seqs']
            ids_all = resdict['ids']
            dq_all = np.array([(1 if z in target_set else 0) for z in sq_all])
            allowed_sq = np.array([banned_dict.get(vv, 1) for vv in sq_all])
            sq_all, md_all, ids_all, dq_all = sq_all[allowed_sq == 1], md_all[allowed_sq == 1], ids_all[allowed_sq == 1], dq_all[allowed_sq == 1]

            l_arr_decoy = []
            l_arr_target = []
            for k, v in prots_spc2.iteritems():
                if isdecoy_key(k):
                    l_arr_decoy.extend([len(vv) for vv in v if banned_dict.get(vv, 1)])
                else:
                    l_arr_target.extend([len(vv) for vv in v if banned_dict.get(vv, 1)])
            # cnt_matched = Counter(l_arr_decoy)
            # cnt_matched_tar = Counter(l_arr_target)
            l_arr_decoy_theor = []
            l_arr_target_theor = []
            for k, v in protsNfull.iteritems():
                if isdecoy_key(k):
                    l_arr_decoy_theor.extend([len(vv) for vv in v])
                else:
                    l_arr_target_theor.extend([len(vv) for vv in v])
                    
            minv = 6
            maxv = 31
            cbins, width = np.arange(minv, maxv+1, 1), 1
            H1d, b1d = np.histogram(l_arr_decoy_theor, bins=cbins)
            H2d, b2d = np.histogram(l_arr_decoy, bins=cbins)
            H3d = H2d.astype(np.float32)/H1d

            H1t, b1t = np.histogram(l_arr_target_theor, bins=cbins)
            H2t, b2t = np.histogram(l_arr_target, bins=cbins)
            H3t = H2t.astype(np.float32)/H1t

            H3 = H3d / H3t
            res_for_l = dict()
            for k, v in zip(b1d, H3):
                res_for_l[k] = v
            peps_l = dict()
            for seq in sq_all:
                curscore = res_for_l.get(len(seq), 1.0)
                if curscore <= peps_l.get(seq, 1.0):
                    peps_l[seq] = curscore
                

            md_mean = np.mean(md_all)
            md_std = np.std(md_all)
            md_z = np.array((md_all - md_mean) / md_std)

            minv = -4
            maxv = 4
            cbins, width = np.arange(minv, maxv+1, 0.2), 0.2
            H1d, b1d = np.histogram(md_z[dq_all == 1], bins=cbins)
            H2d, b2d = np.histogram(md_z[dq_all == 0], bins=cbins)
            # print(H1d)
            # print(H2d)
            H3d = H2d.astype(np.float32)/H1d#/np.sum([dq_all == 0])*np.sum([dq_all == 1])
            H3d[H3d >= 1] = 1.0
            H3d[np.isnan(H3d)] = 1.0
            # print(H3d)

            res_for_md = dict()
            for k, v in zip(b1d, H3d):
                res_for_md[int(round(k*5, 0))] = v

            peps_md = dict()
            for seq, md in zip(sq_all, md_z):
                curscore = res_for_md.get(int(round(md*5, 0)), 1.0)
                if curscore <= peps_md.get(seq, 1.0):
                    peps_md[seq] = curscore

            ###

            minv = 1
            maxv = 51
            cbins, width = np.arange(minv, maxv+1, 1), 1
            cnt_tmp = Counter(ids_all)
            cnt_id = np.array([cnt_tmp[z] for z in ids_all])
            H1d, b1d = np.histogram(cnt_id[dq_all == 1], bins=cbins)
            H2d, b2d = np.histogram(cnt_id[dq_all == 0], bins=cbins)
            # print(H1d)
            # print(H2d)
            H3d = H2d.astype(np.float32)/H1d#/np.sum([dq_all == 0])*np.sum([dq_all == 1])
            H3d[H3d >= 1] = 1.0
            H3d[np.isnan(H3d)] = 1.0
            # print(H3d)

            res_for_ids = dict()
            for k, v in zip(b1d, H3d):
                res_for_ids[k] = v

            peps_ids = dict()
            for seq, idd in zip(sq_all, cnt_id):
                curscore = res_for_ids.get(idd, 1.0)
                if curscore <= peps_ids.get(seq, 1.0):
                    peps_ids[seq] = curscore
            ###

            # print(peps_l)
            # print(peps_md)
            # print(res_for_md)
            prob_arr_decoy = []
            for k, v in prots_spc2.iteritems():
                if isdecoy_key(k):
                    prob_arr_decoy.extend([peps_l.get(vv, 1) * peps_md.get(vv, 1) * peps_ids.get(vv, 1) for vv in v if banned_dict.get(vv, 1)])
            cnt_matched = Counter(l_arr_decoy)
            decoy_num = 0
            for k, v in protsNfull.iteritems():
                if isdecoy_key(k):
                    decoy_num += len(v)
                    
            H1d, b1d = np.histogram(prob_arr_decoy, bins=np.arange(0, 1.01, 0.01))
            # print(H1d)
            H1n = np.cumsum(H1d).astype(np.float32) / decoy_num
            # print(H1n)
            H1n[H1n <= 0.0] = np.min(H1n[H1n!=0])
            p_vals_dict = {}
            for vval, pval in zip(H1n, b1d[:-1]):
                # print(int(round(pval * 100, 0)), vval, pval)
                p_vals_dict[int(round(pval * 100, 0))] = vval
            p_vals_dict[100] = p_vals_dict[99]
            # print(p_vals_dict)
            # l_arr_decoy = []
            # l_arr_target = []
            # for k, v in prots_spc2.iteritems():
            #     if isdecoy_key(k):
            #         # print(v)
            #         # print([banned_dict.get(vv, 1) for vv in v])
            #         l_arr_decoy.extend([len(vv) for vv in v if banned_dict.get(vv, 1)])
            #     else:
            #         l_arr_target.extend([len(vv) for vv in v if banned_dict.get(vv, 1)])
            # cnt_matched = Counter(l_arr_decoy)
            # cnt_matched_tar = Counter(l_arr_target)
            # l_arr_decoy_theor = []
            # l_arr_target_theor = []
            # for k, v in protsNfull.iteritems():
            #     if isdecoy_key(k):
            #         l_arr_decoy_theor.extend([len(vv) for vv in v])
            #     else:
            #         l_arr_target_theor.extend([len(vv) for vv in v])
            # cnt_theor = Counter(l_arr_decoy_theor)
            # cnt_theor_tar = Counter(l_arr_target_theor)
            # # l_arr_decoy = [(len(v) for k, v in prots_spc2.iteritems() if isdecoy_key(k) and banned_dict.get(v, 0)]
            # # l_arr_decoy_theor = [len(v) for k, v in prots_spc2.iteritems() if isdecoy_key(k)]
            # # prots_spc_copy = copy(prots_spc)
            # minL = min(l_arr_decoy_theor)
            # maxL = max(l_arr_decoy_theor)
            # pdict_dec = {}
            # for iii in range(minL, maxL+1, 1):
            #     pdict_dec[iii] = float(cnt_matched.get(iii, cnt_theor[iii])) / cnt_theor[iii]
            # minLt = min(l_arr_target_theor)
            # maxLt = max(l_arr_target_theor)
            # pdict_tar = {}
            # for iii in range(minLt, maxLt+1, 1):
            #     pdict_tar[iii] = float(cnt_matched_tar.get(iii, cnt_theor_tar[iii])) / cnt_theor_tar[iii]
            #     # print(iii, cnt_matched.get(iii, cnt_theor[iii]), cnt_theor[iii])
            # # print(cnt_matched)
            # # print(cnt_theor)
            # # print(pdict)

            # print 'p=%s' % (np.mean(top100decoy_score) / np.mean(top100decoy_N))

            prots_spc = dict()

            all_pvals = calc_sf_all(v_arr, n_arr, p)
            idx_best_100 = np.argsort(-all_pvals)
            v_arr = v_arr[idx_best_100]
            n_arr = n_arr[idx_best_100]
            names_arr = names_arr[idx_best_100]
            all_pvals = all_pvals[idx_best_100]

            for idx, nm in enumerate(names_arr[:100]):

                # D1 = np.array([1, 0, 0])
                # Q1 = np.array([0.1, 0.1, 0.1])
                n_t = int(n_arr[idx])
                # n_m = int(v_arr[idx])
                # n_d = n_t - n_m
                SEQ_array = protsNfull[nm]
                L_array = [len(v) for v in SEQ_array]
                D1 = np.array([1 if banned_dict.get(v, 1) else 0 for v in SEQ_array])
                # D1 = np.array([1] * n_m + [0] * n_d)
                # Q1 = np.array([p] * n_t)
                # Q1 = np.array([pdict.get(l, 1) for l in L_array])
                Q1 = np.array([p_vals_dict[int(round(100* peps_l.get(seq, 1) * peps_md.get(seq, 1) * peps_ids.get(vv, 1), 0))] for seq in SEQ_array])
                B_prob1 = np.prod(Q1 * D1 + (1 - D1)) * np.prod((1 - Q1) * (1 - D1) + (D1))
                X1_s = np.log((1-Q1)/Q1)
                k = np.max(X1_s) / 1000
                X1 = np.round(X1_s / k).astype(int)
                Q = np.sum(np.log(Q1))
                Y1_s = np.log(B_prob1) - Q
                # print(v_arr[idx], n_arr[idx])
                # print(B_prob1)
                # print(Y1_s)
                # # print(k)
                # print('\n')
                if np.isinf(Y1_s):
                    Y1_s = 0.0
                Y1 = int(np.round(Y1_s / k))
                S1_s = np.sum(X1 * (1 - D1))
                lenF = int(1 + np.sum(X1))
                n = n_t#len(D1)

                # F = [0] * lenF#np.zeros(lenF)
                # F[0] = 1
                # for j in xrange(0, n, 1):
                #     diffv = X1[j]
                #     for jj in xrange(lenF-1, -1, -1):
                        # F[jj] += F[jj-diffv]
                F = calc_F(X1, n, lenF)

                Sr = np.arange(0, Y1 + 1, 1)
                eSr = np.exp(k * Sr + Q)
                Prob_final = np.sum(F[:Y1+1]*eSr)
                prots_spc[nm] = 1./Prob_final#all_pvals[idx]
                # print(nm, Prob_final, n_m, n_t, all_pvals[idx])


            # all_pvals = calc_sf_all(v_arr, n_arr, p)
            # for idx, k in enumerate(names_arr):
            #     prots_spc[k] = all_pvals[idx]

            sortedlist_spc = sorted(prots_spc.iteritems(), key=operator.itemgetter(1))[::-1]
            best_prot, best_score = sortedlist_spc[0][0], sortedlist_spc[0][1]
            unstable_prots = set()
            if best_prot not in prots_spc_final:
                print(best_prot, best_score)
                prots_spc_final[best_prot] = best_score
                banned_pids = set()
                for pep in prots_spc2[best_prot]:
                    for pid in pep_pid[pep]:
                        banned_pids.add(pid)
                for pid in banned_pids:
                    for pep in pid_pep[pid]:
                        # banned_peptides.add(pep)
                        banned_dict[pep] = 0
                        for bprot in pept_prot[pep]:
                            unstable_prots.add(bprot)
                del banned_pids
            else:
                break

            prot_fdr = aux.fdr(prots_spc_final.items(), is_decoy=isdecoy)
            # print len(prots_spc_final), len(p1), prot_fdr
            num_tot_prots = len(prots_spc_final)
            if num_tot_prots % 25 == 0:
                print 'Approximately %d proteins identified at %.1f %% FDR' % (num_tot_prots, prot_fdr * 100)
                print p
            if prot_fdr >= 2.5 * fdr:
                break

                
        print 'p=%s' % (p0, )




        prots_spc = prots_spc_final
        sortedlist_spc = sorted(prots_spc.iteritems(), key=operator.itemgetter(1))[::-1]
        with open(base_out_name + '_proteins_full.csv', 'w') as output:
            output.write('dbname\tscore\tmatched peptides\ttheoretical peptides\n')
            for x in sortedlist_spc:
                output.write('\t'.join((x[0], str(x[1]), str(prots_spc_copy[x[0]]), str(protsN[x[0]]))) + '\n')

        checked = set()
        for k, v in prots_spc.items():
            if k not in checked:
                if isdecoy_key(k):
                    if prots_spc.get(k.replace(prefix, ''), -1e6) > v:
                        del prots_spc[k]
                        checked.add(k.replace(prefix, ''))
                else:
                    if prots_spc.get(prefix + k, -1e6) > v:
                        del prots_spc[k]
                        checked.add(prefix + k)

        filtered_prots = aux.filter(prots_spc.items(), fdr=fdr, key=escore, is_decoy=isdecoy, remove_decoy=True, formula=1, full_output=True)

        identified_proteins = 0

        for x in filtered_prots:
            identified_proteins += 1

        print 'TOP 5 identified proteins:'
        print 'dbname\tscore\tnum matched peptides\tnum theoretical peptides'
        for x in filtered_prots[:5]:
            print '\t'.join((str(x[0]), str(x[1]), str(int(prots_spc_copy[x[0]])), str(protsN[x[0]])))
        print 'results:%s;number of identified proteins = %d' % (fname, identified_proteins, )
        print 'R=', r
        with open(base_out_name + '_proteins.csv', 'w') as output:
            output.write('dbname\tscore\tmatched peptides\ttheoretical peptides\n')
            for x in filtered_prots:
                output.write('\t'.join((x[0], str(x[1]), str(prots_spc_copy[x[0]]), str(protsN[x[0]]))) + '\n')


        fig = plt.figure(figsize=(16, 12))
        DPI = fig.get_dpi()
        fig.set_size_inches(2000.0/float(DPI), 2000.0/float(DPI))

        df0 = pd.read_table(os.path.splitext(fname)[0].replace('.features', '') + '.features' + '.tsv')

        # Features RT distribution
        # TODO add matched features and matched to 1% FDR proteins features
        ax = fig.add_subplot(3, 1, 1)
        bns = np.arange(0, df0['rtApex'].max() + 1, 1)
        ax.hist(df0['rtApex'], bins = bns)
        ax.set_xlabel('RT, min', size=16)
        ax.set_ylabel('# features', size=16)

        # Features mass distribution

        # TODO add matched features and matched to 1% FDR proteins features
        ax = fig.add_subplot(3, 1, 2)
        bns = np.arange(0, df0['massCalib'].max() + 6, 5)
        ax.hist(df0['massCalib'], bins = bns)
        ax.set_xlabel('neutral mass, Da', size=16)
        ax.set_ylabel('# features', size=16)

        # Features intensity distribution

        # TODO add matched features and matched to 1% FDR proteins features
        ax = fig.add_subplot(3, 1, 3)
        bns = np.arange(np.log10(df0['intensityApex'].min()) - 0.5, np.log10(df0['intensityApex'].max()) + 0.5, 0.5)
        ax.hist(np.log10(df0['intensityApex']), bins = bns)
        ax.set_xlabel('log10(Intensity)', size=16)
        ax.set_ylabel('# features', size=16)

        plt.savefig(base_out_name + '.png')

    else:
        print 'No matches found'
