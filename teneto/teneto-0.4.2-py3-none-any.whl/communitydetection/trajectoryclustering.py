import networkx as nx
import os
import pandas as pd
import scipy.spatial.distance as distance
from scipy.signal import hilbert
import numpy as np
import itertools
from concurrent.futures import ProcessPoolExecutor
from teneto.utils import tnet_to_nx
import tempfile
import shutil
from itertools import repeat, combinations
import teneto
import time


def amplitude_to_phase(data):
    """
    Input in should be time series.
    """
    analytic_signal = hilbert(data)
    instantaneous_phase = np.angle(analytic_signal)
    return instantaneous_phase.transpose()


def get_all_subset_combinations(gint, sigma):

    out = []
    k = sigma
    while True:
        o = list(combinations(gint, k))
        if len(o) == 0:
            break
        out += o
        k += 1
    return list(map(lambda x: set(x), out))


def add_subsets(tmpname):

    # Hry community indicies
    df = pd.read_hdf(tmpname, 'communities')

    dfnew = pd.DataFrame(columns=['i', 'j', 't'])
    for i, row in df.iterrows():
        nodes = pd.read_hdf(tmpname, 'community_' + str(i))
        # with pd.HDFStore(tmpname) as hdf:
        #     hdf.remove('community_' + str(i))
        tdf = pd.read_hdf(tmpname, 'communities_in_time',
                          columns='t', where='community_index in ' + str(i))
        nodepairs = np.array(
            list(itertools.combinations(np.concatenate(nodes.values), 2)))
        for _, t in tdf.iterrows():
            tmp = np.hstack([nodepairs, np.array(
                np.repeat(t['t'], len(nodepairs)), ndmin=2).transpose()])
            dfnew = dfnew.append(pd.DataFrame(tmp, columns=['i', 'j', 't']))
        dfnew = dfnew.drop_duplicates()

    dfnew.reset_index(drop=True, inplace=True)
    dfnew = dfnew.astype('float')
    # Note: this could be added iteratively instead of all at once to save memory
    dfnew.to_hdf(tmpname, 'communities_adj', format='table', data_columns=True)
    # with pd.HDFStore(tmpname) as hdf:
    #     hdf.remove('communities_in_time')
    #     hdf.remove('communities')


def delete_complete_subsets(tmpname, kappa):

    t1 = time.time()
    df = pd.read_hdf(tmpname, 'communities')

    groups = []
    gi = []
    for i, row in df.iterrows():
        gi.append(i)
        nodes = pd.read_hdf(tmpname, 'community_' + str(i))
        groups.append(set(map(int, nodes['nodes'].values)))

    for n, g in enumerate(groups):
        ind = [str(i) for i, gg in enumerate(groups)
               if g.issubset(gg) and not g.issuperset(gg)]
        if ind:
            wherestr = 'community_index in ' + \
                ' | community_index in '.join(ind)
            dftmp = pd.read_hdf(tmpname, 'communities_in_time',
                                columns='t', where=wherestr)
            dfcurrent = pd.read_hdf(tmpname, 'communities_in_time',
                                    columns='t', where='community_index == ' + str(gi[n]))
            traj1 = np.split(dftmp['t'].values, np.where(
                np.diff(dftmp['t'].values) > kappa+1)[0]+1)
            traj2 = np.split(dfcurrent['t'].values, np.where(
                np.diff(dfcurrent['t'].values) > kappa+1)[0]+1)
            overlap = [n for m in traj2 for n in traj1 if set(n) == set(m)]
            if overlap:
                overlap = np.concatenate(overlap)
                wherestr = '(t in ' + ' | t in '.join(map(str, list(overlap))
                                                      ) + ') & community_index in ' + str(gi[n])
                with pd.HDFStore(tmpname) as hdf:
                    hdf.remove('communities_in_time', wherestr)
    t2 = time.time()
    #print('delete complete subsets:' + str(t2-t1))


def distance_rule(data, epsilon, raw_signal):
    """
    Given time series data. 

    data is node,time
    """
    data = data.transpose()
    # convery signal to phase if raw_signal == 'phase'
    if raw_signal == 'phase':
        data = amplitude_to_phase(data)
    # add noise to signal here

    # Go through each time-point and add time-point
    passed_signals = []
    for n in range(data.shape[0]):
        for m in range(n+1, data.shape[0]):
            # For large data, could load from a hdf5 file and also write to hdf5 here.
            # Distance funciton here is taxicab.
            if raw_signal == 'amplitude':
                dtmp = np.array(np.abs(data[n]-data[m]))
            elif raw_signal == 'phase':
                dtmp = np.remainder(np.abs(data[n] - data[m]), np.pi)
            ids = np.where(dtmp <= epsilon)[0]
            i = np.repeat(n, len(ids))
            j = np.repeat(m, len(ids))
            passed_signals += list(zip(*[i, j, ids]))
    return pd.DataFrame(passed_signals, columns=['i', 'j', 't'])


def size_rule_apply(clusters, t, sigma):
    while True:
        try:
            c = next(clusters)
            if len(c) >= sigma:
                yield sorted(list(c))
        except (RuntimeError, StopIteration):
            return


def _clusterfun(traj, t, rule, sigma, N):
    if rule == 'flock':
        clusterfun = nx.find_cliques
    elif rule == 'convoy':
        clusterfun = nx.connected_components
    nxobj = tnet_to_nx(traj, t=t)
    clusters = clusterfun(nxobj)
    traj_clusters = size_rule_apply(clusters, t, sigma)
    return traj_clusters


def size_rule(traj, sigma, rule, tmpname, N, initialise=True, largestonly=False, njobs=1):
    tmax = traj['t'].max() + 1
    if rule == 'flock':
        clusterfun = nx.find_cliques
    elif rule == 'convoy':
        clusterfun = nx.connected_components
    if initialise == True:
        initialized = False
        t1 = time.time()
        for t in np.arange(tmax):
            clusters = clusterfun(tnet_to_nx(traj, t=t))
            traj_clusters = size_rule_apply(clusters, t, sigma)
            initialized = add_to_hdf5tmp(
                list(traj_clusters), t, tmpname, N, initialized)
        if initialized == False:
            return False
        t2 = time.time()
        #print('Clusterfun: ' + str(t2-t1))
    #df = pd.read_hdf(tmpname, 'communities_in_time')
    # else:
    #    df = pd.read_hdf(tmpname,'communities')
    #    for i,r in df.iterrows():
    #        with pd.HDFStore(tmpname) as hdf:
    #            nrows = hdf.get_storer('communities_' + str(i)).nrows
    #        if nrows < sigma:
    #            hdf = pd.HDFStore(tmpname)
    #            hdf.remove('communities_in_time', 'community_index == ' + str(i))
    #            hdf.close()


def time_rule(tau, kappa, tmpname):
    df = pd.read_hdf(tmpname, 'communities_adj')
    # This make sure that each ij pair considered has at least timeol as many hits (for speed)
    dfg = df.groupby(['i', 'j'])['t'].transform('size') >= tau
    df = df[dfg]
    # get ij indicies
    ijind = df.groupby(['i', 'j']).count().reset_index()
    removerows = []
    addrow = []
    for _, row in ijind.iterrows():
        # i is always smaller than j
        dft = teneto.utils.get_network_when(
            df, i=row['i'], j=row['j'], logic='and')
        d = np.split(sorted(dft['t'].values), np.where(
            np.diff(sorted(dft['t'].values)) > kappa+1)[0]+1)
        # get index of those to be deleted
        rr = list(filter(lambda x: len(x) < tau, d))
        rr = list(map(lambda x: x.tolist(), rr))
        if len(rr) > 0:
            rr = np.concatenate(rr)
            removerows += list(dft['t'][dft['t'].isin(rr)].index)
        # get index of rows to be added
        ar = list(filter(lambda x: len(x) >= tau, d))
        print(ar)
        ar = list(filter(lambda x: len(x) < x.max()-x.min(), ar))
        print(ar)
        ar = list(map(lambda x: set(np.arange(x.min(),x.max()+1)).difference(set(x)), ar))
        print(ar)
        for r in ar: 
            for t in r:
                addrow.append((row['i'],row['j'], t))
        print(addrow)
    if len(removerows) > 0:
        df.drop(sorted(removerows), axis=0, inplace=True)
    df = pd.concat([df,pd.DataFrame(addrow,columns=['i','j','t'])]).reset_index(drop=True)

    return df


def add_to_hdf5tmp(traj_clusters, t, tmpname, N, initialized=False):
    #traj_clusters = [list(map(str,tc)) for tc in traj_clusters]

    # Workaround since pandas can store empty dataframe
    if not initialized and len(traj_clusters) > 0:
        hdf = pd.HDFStore(tmpname, mode='w')
        df = pd.DataFrame(data={'community_index': list(np.arange(len(traj_clusters))), 't': list(
            np.repeat(0, len(traj_clusters)))}, index=np.arange(len(traj_clusters)))
        df.to_hdf(tmpname, 'communities_in_time',
                  format='table', data_columns=True)

        df = pd.DataFrame(data={'community': np.arange(
            len(traj_clusters))}, index=np.arange(len(traj_clusters)))
        df.to_hdf(tmpname, 'communities', format='table', data_columns=True)
        for i, tc in enumerate(traj_clusters):
            df = pd.DataFrame(data={'nodes': tc})
            df.to_hdf(tmpname, 'community_' + str(i),
                      format='table', data_columns=True)
        hdf.close()
        initialized = True
    elif len(traj_clusters) > 0:
        communities = pd.read_hdf(tmpname, 'communities')
        cliind = communities['community'].tolist()
        cli = []
        for c in cliind:
            nodes = pd.read_hdf(tmpname, 'community_' + str(c))
            cli.append(list(map(int, nodes['nodes'].values)))
        maxcli = len(cli)
        new_cli_ind = []
        add_traj = []
        for c in traj_clusters:
            if c in cli:
                new_cli_ind.append(cli.index(c))
            else:
                new_cli_ind.append(maxcli)
                maxcli += 1
                add_traj.append(c)
        if new_cli_ind:
            with pd.HDFStore(tmpname) as hdf:

                nrows = hdf.get_storer('communities_in_time').nrows
                lastrow = hdf.select('communities_in_time',
                                     start=nrows-1, stop=nrows)
                newstartind = int(lastrow.index[0]) + 1
                hdf.append('communities_in_time', pd.DataFrame(list(zip(*[list(new_cli_ind), list(np.repeat(t, len(new_cli_ind)))])), columns=[
                           'community_index', 't'], index=list(np.arange(newstartind, newstartind+len(new_cli_ind)))), format='table', data_columns=True)
                if add_traj:
                    nrows = hdf.get_storer('communities').nrows
                    lastrow = hdf.select(
                        'communities', start=nrows-1, stop=nrows)
                    newstartind = int(lastrow.index[0]) + 1
                    hdf.append('communities', pd.DataFrame(np.arange(newstartind, newstartind+len(add_traj)), columns=[
                               'community'], index=np.arange(newstartind, newstartind+len(add_traj))), format='table', data_columns=True)
                    for n, i in enumerate(np.arange(newstartind, newstartind+len(add_traj))):
                        df = pd.DataFrame(data={'nodes': add_traj[n]})
                        df.to_hdf(tmpname, 'community_' + str(i),
                                  format='table', data_columns=True)

    return initialized


def delete_null_communities(tmpname):
    ind = pd.read_hdf(tmpname, 'communities').index
    hdf = pd.HDFStore(tmpname)
    for idx in ind:
        if len(hdf.select_as_coordinates('communities_in_time', where='community_index == ' + str(idx))) == 0:
            hdf.remove('communities', 'index == ' + str(idx))
            hdf.remove('community_' + str(idx))
    hdf.close()


def delete_noise_communities(tmpname, N_data):

    df = pd.read_hdf(tmpname, 'communities')
    del_community = []
    for i, row in df.iterrows():
        nodes = pd.read_hdf(tmpname, 'community_' + str(i))
        if nodes['nodes'].max() >= N_data:
            del_community.append(i)

    hdf = pd.HDFStore(tmpname)
    for idx in del_community:
        hdf.remove('communities_in_time', 'community_index == ' + str(idx))
        hdf.remove('communities', 'index == ' + str(idx))
        hdf.remove('community_' + str(idx))
    hdf.close()


def find_tctc_hdf(data, timetol, disttol, trajsize, skiptol=0, rule='convoy', noise=None, largestonly=False, raw_signal='amplitude', return_array=False, returndf=True, tempdir=None, savedf=False, savename=None, njobs=1):
    # Data is time,node
    # Get distance matrix

    if noise is not None:
        if len(noise.shape) == 1:
            noise = np.array(noise, ndmin=2).transpose()
        N_data = data.shape[1]
        data = np.hstack([data, noise])

    N = data.shape[1]
    T = data.shape[0]
    traj = distance_rule(data, disttol, raw_signal)

    # Make a hdf5 tempfile
    rlast = 0
    if savedf and not savename:
        savename = './teneto_communities_cdtc.h5'
    if savename and savename[-3:] != '.h5':
        savename += '.h5'

    if len(traj) == 0:
        if returndf:
            return [], []
        else:
            return

    while True:
        with tempfile.NamedTemporaryFile(suffix='.h5', dir=tempdir) as temp:

            if len(traj) == 0:
                df = []
                cdf = []
                break

            initialize = True
            t = time.time()
            print('-------')
            c = size_rule(traj, trajsize, rule, temp.name, N,
                          initialise=initialize,  largestonly=largestonly, njobs=njobs)

            df = pd.read_hdf(temp.name, 'communities_in_time')
            # doing this in case it is all empty
            cdf = pd.read_hdf(temp.name, 'communities')
            # make better output names
            comlist = []
            for i, row in cdf.iterrows():
                nodes = pd.read_hdf(temp.name, 'community_' + str(i))
                comlist.append(nodes['nodes'].values)
            cdf['community'] = comlist
            print(len(cdf))
            add_subsets(temp.name)
            print(len(pd.read_hdf(temp.name, 'communities_adj')))
            traj_new = time_rule(timetol, skiptol, temp.name)
            traj_new = traj_new.astype(int)
            print(len(traj_new))
            if len(traj_new) == len(traj):
                if noise is not None:
                    delete_noise_communities(temp.name, N_data)
                # delete_null_communities(temp.name)
                #delete_complete_subsets(temp.name, skiptol)
                if return_array == True: 
                    df = traj_new
                if returndf == True:
                    df = pd.read_hdf(temp.name, 'communities_in_time')
                    # doing this in case it is all empty
                    cdf = pd.read_hdf(temp.name, 'communities')
                    # make better output names
                    comlist = []
                    for i, row in cdf.iterrows():
                        nodes = pd.read_hdf(temp.name, 'community_' + str(i))
                        comlist.append(nodes['nodes'].values)
                    cdf['community'] = comlist
                if savedf == True:
                    shutil.copy(temp.name, savename)
                    print('Saved at ' + savename)
                break
            else:
                traj = traj_new

    if returndf:
        return df, cdf
    elif return_array:
        return df

        

def find_tctc(data, timetol, disttol, trajsize, skiptol=0, largedataset=False, rule='convoy', noise=None, largestonly=False, raw_signal='amplitude', returndf=True, return_array=False, tempdir=None, savedf=False, savename=None, njobs=1):
    # Get distance matrix
    if largedataset:
        return find_tctc_hdf(data, timetol, disttol, trajsize, skiptol=skiptol, rule=rule, noise=noise, largestonly=largestonly, raw_signal=raw_signal, returndf=returndf, return_array=return_array, tempdir=tempdir, savedf=savedf, savename=savename, njobs=njobs) 
    else: 
        N_data = data.shape[1]
        if noise is not None:
            if len(noise.shape) == 1:
                noise = np.array(noise, ndmin=2).transpose()
            N_data = data.shape[1]
            data = np.hstack([data, noise])

        N = data.shape[1]
        T = data.shape[0]

        if raw_signal == 'amplitude':
            d = np.array([np.abs(data[:, n]-data[:, m])
                        for n in range(data.shape[-1]) for m in range(data.shape[-1])])
            d = np.reshape(d, [data.shape[-1], data.shape[-1], data.shape[0]])

        elif raw_signal == 'phase':
            analytic_signal = hilbert(data.transpose())
            instantaneous_phase = np.angle(analytic_signal)
            d = np.zeros([data.shape[1], data.shape[1], data.shape[0]])
            for n in range(data.shape[1]):
                for m in range(data.shape[1]):
                    d[n, m, :] = np.remainder(
                        np.abs(instantaneous_phase[n, :] - instantaneous_phase[m, :]), np.pi)

        # Shape of datin (with any addiitonal 0s or noise added to nodes)
        dat_shape = [int(d.shape[-1]), int(d.shape[0])]
        # Make trajectory matrix 1 where distance critera is kept
        traj_mat = np.zeros([dat_shape[1], dat_shape[1], dat_shape[0]])
        traj_mat[:, :, :][d <= disttol] = 1

        t1 = 1
        t2 = 2
        # The next two rules have to be run iteratively until it converges. i.e. when applying the trajsize and timetol parameters, if nothing more is pruned, then this is complete
        # There may be a case where running it in this order could through some value that is unwanted due to the skipping mechanic.
        # Doing it in the other order does create possible bad values.
        while t1 != t2:

            t1 = traj_mat.sum()
            cliques = []
            if traj_mat.sum() > 0:
                # Run the trajectory clustering rule
                if rule == 'flock':

                    cliques = [list(filter(lambda x: (len(x) >= trajsize) and (len(set(x).intersection(np.arange(N_data,N+1))) == 0), nx.find_cliques(
                        nx.graph.Graph(traj_mat[:, :, t])))) for t in range(traj_mat.shape[-1])]
                    #cliques = []
                    # with ProcessPoolExecutor(max_workers=njobs) as executor:
                    #    job = {executor.submit(_cluster_flocks,traj_mat[:,:,t],trajsize) for t in range(traj_mat.shape[-1])}
                    #    for j in as_completed(job):
                    #        cliques.append(j.result()[0])

                elif rule == 'convoy':
                    cliques = [list(map(list, filter(lambda x: (len(x) >= trajsize) and (len(set(x).intersection(np.arange(N_data,N+1))) == 0), nx.connected_components(
                        nx.graph.Graph(traj_mat[:, :, t]))))) for t in range(traj_mat.shape[-1])]

                # Reset the trajectory matrix (since info is now in "cliques").
                # Add the infomation from clique into traj_mat (i.e trajsize is now implemented)
                traj_mat = np.zeros([dat_shape[1], dat_shape[1], dat_shape[0]])
                # Due to advanced index copy, I've done this with too many forloops
                for t in range(dat_shape[0]):
                    for c in cliques[t]:
                        # Make one of index vectors a list.
                        cv = [[i] for i in c]
                        traj_mat[cv, c, t] = 1

            print(dat_shape)
            print(timetol)
            print(skiptol)
            if traj_mat.sum() > 0:
                # Now impose timetol criteria. This is done by flattening and (since timetol has been added to the final dimension)
                # Add some padding as this is going to be needed when flattening (ie different lines must have at least timetol+skiptol spacing between them)
                traj_mat = np.dstack([np.zeros([dat_shape[1], dat_shape[1], 1]), traj_mat, np.zeros(
                    [dat_shape[1], dat_shape[1], timetol+skiptol])])
                # Make to singular vector
                traj_mat_vec = np.array(traj_mat.flatten())
                # Add an extra 0
                traj_mat_dif = np.append(traj_mat_vec, 0)
                # Use diff. Where there is a 1 trajectory starts, where -1 trajectory ends
                traj_mat_dif = np.diff(traj_mat_dif)
                start_ones = np.where(traj_mat_dif == 1)[0]
                end_ones = np.where(traj_mat_dif == -1)[0]
                skip_ind = np.where(start_ones[1:]-end_ones[:-1] <= skiptol)[0]
                start_ones = np.delete(start_ones, skip_ind+1)
                end_ones = np.delete(end_ones, skip_ind)

                traj_len = end_ones - start_ones
                # whereever traj_len is not long enough, loop through ind+t and make these 0
                ind = start_ones[traj_len >= timetol] + 1
                l2 = traj_len[traj_len >= timetol]
                # for t in range(timetol-1): # this didn't work (but was quicker) because of timetol bug
                #    traj_mat[ind+t] = 0
                # Looping over each valid trajectory instance is slower but the safest was to impose timetol restrain and reinserting it.
                traj_mat = np.zeros(traj_mat_vec.shape)
                for i in range(len(ind)):
                    traj_mat[ind[i]:ind[i]+l2[i]] = 1
                traj_mat = traj_mat.reshape(
                    dat_shape[1], dat_shape[1], dat_shape[0]+skiptol+timetol+1)
                # remove padding
                traj_mat = traj_mat[:, :, 1:dat_shape[0]+1]

            t2 = traj_mat.sum()

        return traj_mat
