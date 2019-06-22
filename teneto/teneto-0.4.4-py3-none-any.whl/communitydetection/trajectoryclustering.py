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
from skopt import gp_minimize
from skopt.space import Real, Integer


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


def add_subsets(tmpname, hdf=False, tdf=None, df_com=None):

    # Get community indicies
    if hdf:
        df = pd.read_hdf(tmpname, 'communities')
    else:
        df = df_com

    dfnew = pd.DataFrame(columns=['i', 'j', 't'])
    for i, row in df.iterrows():
        if hdf:
            nodes = pd.read_hdf(tmpname, 'community_' + str(i))
            tdf = pd.read_hdf(tmpname, 'communities_in_time',
                              columns='t', where='community_index in ' + str(i))
        else:
            nodes = df['community'].iloc[i]
        # with pd.HDFStore(tmpname) as hdf:
        #     hdf.remove('community_' + str(i))

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
                dtmp = np.remainder(np.abs(data[n] - data[m]), np.pi*2)
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


def partition_inference(traj_mat, comp, tau, sigma, skiptol):
    vecinfo = {}
    vecinfo['vec'] = []
    vecinfo['start'] = np.empty(0)
    vecinfo['end'] = np.empty(0)
    vecinfo['size'] = np.empty(0)
    for i, tcomp in enumerate(comp):
        # This can go in parallel loop
        if len(tcomp) > 0:
            for traj in tcomp:
                vec = np.ones(len(tcomp))
                # Check it does not already exist.
                ignore = 0
                if i != 0:
                    cutoff = i-1-skiptol
                    if cutoff < 0:
                        cutoff = 0
                    if np.any(np.sum(np.sum(traj_mat[traj, :, cutoff:i][:, traj], axis=0), axis=0) == np.power(len(traj), 2)):
                        ignore = 1
                if ignore == 0:
                    # Check how long it continues
                    # For efficiency, increase in blocks
                    approxmaxlength = tau*2
                    a = np.sum(
                        np.sum(traj_mat[traj, :, i:i+approxmaxlength][:, traj], axis=0), axis=0)
                    if len(traj)*len(traj)*approxmaxlength == a.sum():
                        ok = 0
                        ii = 1
                        while ok == 0:
                            b = np.sum(np.sum(
                                traj_mat[traj, :, i+(approxmaxlength*ii):i+(approxmaxlength*(ii+1))][:, traj], axis=0), axis=0)
                            a = np.append(a, b)
                            ii += 1
                            if len(traj)*len(traj)*approxmaxlength == b.sum():
                                ok = 1
                            if i+(approxmaxlength*(ii+1)) > traj_mat.shape[-1]:
                                ok = 1
                    a = np.where(a == np.power(len(traj), 2))[0]
                    # Add an additional value that is false in case end of time series
                    if len(a) == 1:
                        stopind = i + 1
                    else:
                        a = np.append(a, a.max()+skiptol+2)
                        # Find the stop index (if stopind = 4 and start = 0, then traj_mat[:,:,start:stopind]==1)
                        stopind = i + \
                            np.split(a, np.where(
                                np.diff(a) > skiptol+1)[0]+1)[0][-1] + 1
                    # Add trajectory to dictionary
                    if (stopind - i) >= tau and len(traj) >= sigma:
                        vecinfo['vec'].append(sorted(traj))
                        vecinfo['start'] = np.append(vecinfo['start'], int(i))
                        vecinfo['end'] = np.append(
                            vecinfo['end'], int(stopind))
                        vecinfo['size'] = np.append(vecinfo['size'], len(traj))

    vecinfo = pd.DataFrame(vecinfo)

    vecinfo['start'] = vecinfo['start'].astype(int)
    vecinfo['end'] = vecinfo['end'].astype(int)
    # First check that there is not already a trajectory that is ongoing
    badrows = []
    for v in vecinfo.iterrows():
        skipselrule = (vecinfo['end'] == v[1]['end'])
        for u in vecinfo[skipselrule].iterrows():
            a = 1
            if u[1]['start'] > v[1]['start'] and sorted(u[1]['vec']) == sorted(v[1]['vec']):
                badrows.append(u[0])
    vecinfo = vecinfo.drop(badrows)

    # Then see if any subset trajectory can be placed earlier in time.
    for v in vecinfo.iterrows():
        skipselrule = (vecinfo['end'] <= v[1]['start']) & (
            vecinfo['end']+skiptol >= v[1]['start'])
        for u in vecinfo[skipselrule].iterrows():
            a = 1
            if set(u[1]['vec']).issuperset(v[1]['vec']):
                vecinfo.loc[v[0], 'start'] = u[1]['start']

    # It is possible to make the condition below effective_length
    vecinfo['length'] = np.array(vecinfo['end']) - np.array(vecinfo['start'])
    vecinfo = vecinfo[vecinfo['length'] >= tau]
    vecinfo = vecinfo[vecinfo['size'] >= sigma]

    # Make sure that the traj is not completely enguled by another
    badrows = []
    if skiptol > 0:
        for v in vecinfo.iterrows():
            skipselrule = (vecinfo['end'] == v[1]['end']) & (
                vecinfo['start'] < v[1]['start'])
            for u in vecinfo[skipselrule].iterrows():
                if set(v[1]['vec']).issubset(u[1]['vec']):
                    badrows.append(v[0])
        vecinfo = vecinfo.drop(badrows)

    return vecinfo


def time_rule(tau, kappa, tmpname, hdf=True, df=None):
    if hdf:
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
        ar = list(
            map(lambda x: set(np.arange(x.min(), x.max()+1)).difference(set(x)), ar))
        print(ar)
        for r in ar:
            for t in r:
                addrow.append((row['i'], row['j'], t))
    if len(removerows) > 0:
        df.drop(sorted(removerows), axis=0, inplace=True)
    df = pd.concat(
        [df, pd.DataFrame(addrow, columns=['i', 'j', 't'])]).reset_index(drop=True)

    return df


def add_to_hdf5tmp(traj_clusters, t, tmpname, N, initialized=False, hdf=True, df=None, df_com=None):
    #traj_clusters = [list(map(str,tc)) for tc in traj_clusters]

    # Workaround since pandas can store empty dataframe
    if not initialized and len(traj_clusters) > 0:
        df = pd.DataFrame(data={'community_index': list(np.arange(len(traj_clusters))), 't': list(
            np.repeat(0, len(traj_clusters)))}, index=np.arange(len(traj_clusters)))
        if hdf:
            hdf = pd.HDFStore(tmpname, mode='w')
            df.to_hdf(tmpname, 'communities_in_time',
                      format='table', data_columns=True)
            df = pd.DataFrame(data={'community': np.arange(
                len(traj_clusters))}, index=np.arange(len(traj_clusters)))
            df.to_hdf(tmpname, 'communities',
                      format='table', data_columns=True)
            for i, tc in enumerate(traj_clusters):
                df = pd.DataFrame(data={'nodes': tc})
                df.to_hdf(tmpname, 'community_' + str(i),
                          format='table', data_columns=True)
            hdf.close()
        else:
            communities = []
            for tc in traj_clusters:
                communities.append(tc)
            df_com = pd.DataFrame(
                data={'community': communities}, index=np.arange(len(traj_clusters)))
        initialized = True
    elif len(traj_clusters) > 0:
        if hdf:
            communities = pd.read_hdf(tmpname, 'communities')
            cliind = communities['community'].tolist()
            cli = []
            for c in cliind:
                nodes = pd.read_hdf(tmpname, 'community_' + str(c))
                cli.append(list(map(int, nodes['nodes'].values)))
        else:
            cli = df_com['community'].values.tolist()
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
            if hdf:
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
            else:
                newstartind = len(df)
                df = df.append(pd.DataFrame(data={'community_index': list(np.arange(newstartind, newstartind + len(new_cli_ind))), 't': list(
                    np.repeat(t, len(new_cli_ind)))}, index=np.arange(newstartind, newstartind + len(new_cli_ind))))
                newstartind = len(df_com)
                df_com = df_com.append(pd.DataFrame(data={'community': add_traj}, index=np.arange(
                    newstartind, newstartind + len(add_traj))))
    if hdf:
        return initialized
    else:
        return df, df_com


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


def find_tctc_hdf(data, tau, epsilon, sigma, skiptol=0, rule='convoy', noise=None, largestonly=False, raw_signal='amplitude', output='array', tempdir=None, savedf=False, savename=None, njobs=1):
    # Data is time,node
    # Get distance matrix

    if noise is not None:
        if len(noise.shape) == 1:
            noise = np.array(noise, ndmin=2).transpose()
        N_data = data.shape[1]
        data = np.hstack([data, noise])

    N = data.shape[1]
    T = data.shape[0]
    traj = distance_rule(data, epsilon, raw_signal)

    # Make a hdf5 tempfile
    rlast = 0
    if savedf and not savename:
        savename = './teneto_communities_cdtc.h5'
    if savename and savename[-3:] != '.h5':
        savename += '.h5'

    if len(traj) == 0:
        if output:
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
            c = size_rule(traj, sigma, rule, temp.name, N,
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
            add_subsets(temp.name)
            traj_new = time_rule(tau, skiptol, temp.name)
            traj_new = traj_new.astype(int)
            if len(traj_new) == len(traj):
                if noise is not None:
                    delete_noise_communities(temp.name, N_data)
                # delete_null_communities(temp.name)
                #delete_complete_subsets(temp.name, skiptol)
                if output == 'array':
                    df = traj_new
                if output == 'df':
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

    if output == 'df':
        return df, cdf
    elif output == 'array':
        return df


def find_tctc(data, tau, epsilon, sigma, skiptol=0, largedataset=False, rule='convoy', noise=None, largestonly=False, raw_signal='amplitude', output='array', tempdir=None, savedf=False, savename=None, njobs=1):
    r"""
    Runs TCTC community detection 

    data : array
        Multiariate series with dimensions: "time, node" that belong to a network. 
    tau : int
        tau specifies the minimum number of time-points of each temporal community must last. 
    epsilon : float 
        epsilon specifies the distance points in a community can be away from each other.
    sigma : int 
        sigma specifies the minimum number of nodes that must be in a community. 
    kappa : int
        kappa specifies the number of consecutive time-points that can break the distance or size rules. 
    largedataset : bool
        If true, runs with HDF5 (beta)
    rule : str
        Can be 'convoy' or 'flock'.
            - flock entials all nodes are max epsilon apart in a communiy.
            - convoy entails that there is at least one node that is epsilon apart. 
    noise : array (defauly None)
        Timeseries of dimensions "time, N" where N is the number of noise time series added. Any community that contains this time series is excluded.  
    largestonly : bool (default False) 
        If True only considers largest communities in rule application (should generally be false)
    raw_signal : str
        Can be amplitude or phase
    output : str
        Can be array or df
    tempdir : str
        Specify where the temporary directory is if largedataset is True
    savedf : bool
        If True, saves the dataframe output 
    savename : str
        If savedf = True, specify filename. 
    njobs : int
        number of jobs
    """
    # Get distance matrix
    if largedataset:
        return find_tctc_hdf(data, tau, epsilon, sigma, skiptol=skiptol, rule=rule, noise=noise, largestonly=largestonly, raw_signal=raw_signal, output=output, tempdir=tempdir, savedf=savedf, savename=savename, njobs=njobs)
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
        traj_mat[:, :, :][d <= epsilon] = 1

        t1 = 1
        t2 = 2
        # The next two rules have to be run iteratively until it converges. i.e. when applying the sigma and tau parameters, if nothing more is pruned, then this is complete
        # There may be a case where running it in this order could through some value that is unwanted due to the skipping mechanic.
        # Doing it in the other order does create possible bad values.
        while t1 != t2:

            t1 = traj_mat.sum()
            cliques = []
            if traj_mat.sum() > 0:
                # Run the trajectory clustering rule
                if rule == 'flock':

                    cliques = [list(filter(lambda x: (len(x) >= sigma) and (len(set(x).intersection(np.arange(N_data, N+1))) == 0), nx.find_cliques(
                        nx.graph.Graph(traj_mat[:, :, t])))) for t in range(traj_mat.shape[-1])]
                    #cliques = []
                    # with ProcessPoolExecutor(max_workers=njobs) as executor:
                    #    job = {executor.submit(_cluster_flocks,traj_mat[:,:,t],sigma) for t in range(traj_mat.shape[-1])}
                    #    for j in as_completed(job):
                    #        cliques.append(j.result()[0])

                elif rule == 'convoy':
                    cliques = [list(map(list, filter(lambda x: (len(x) >= sigma) and (len(set(x).intersection(np.arange(N_data, N+1))) == 0), nx.connected_components(
                        nx.graph.Graph(traj_mat[:, :, t]))))) for t in range(traj_mat.shape[-1])]

                # Reset the trajectory matrix (since info is now in "cliques").
                # Add the infomation from clique into traj_mat (i.e sigma is now implemented)
                traj_mat = np.zeros([dat_shape[1], dat_shape[1], dat_shape[0]])
                # Due to advanced index copy, I've done this with too many forloops
                for t in range(dat_shape[0]):
                    for c in cliques[t]:
                        # Make one of index vectors a list.
                        cv = [[i] for i in c]
                        traj_mat[cv, c, t] = 1

            if traj_mat.sum() > 0:
                # Now impose tau criteria. This is done by flattening and (since tau has been added to the final dimension)
                # Add some padding as this is going to be needed when flattening (ie different lines must have at least tau+skiptol spacing between them)
                traj_mat = np.dstack([np.zeros([dat_shape[1], dat_shape[1], 1]), traj_mat, np.zeros(
                    [dat_shape[1], dat_shape[1], tau+skiptol])])
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
                ind = start_ones[traj_len >= tau] + 1
                l2 = traj_len[traj_len >= tau]
                # for t in range(tau-1): # this didn't work (but was quicker) because of tau bug
                #    traj_mat[ind+t] = 0
                # Looping over each valid trajectory instance is slower but the safest was to impose tau restrain and reinserting it.
                traj_mat = np.zeros(traj_mat_vec.shape)
                for i in range(len(ind)):
                    traj_mat[ind[i]:ind[i]+l2[i]] = 1
                traj_mat = traj_mat.reshape(
                    dat_shape[1], dat_shape[1], dat_shape[0]+skiptol+tau+1)
                # remove padding
                traj_mat = traj_mat[:, :, 1:dat_shape[0]+1]

            t2 = traj_mat.sum()

        # remove noise
        traj_mat = traj_mat[:N_data, :N_data]
        if output == 'array':
            return traj_mat

        elif output == 'df':

            if np.sum(traj_mat) != 0:
                df = partition_inference(
                    traj_mat, cliques, tau, sigma, skiptol)
                return df
            else:
                return []


@use_named_args(space)
def _opt_trialdiff(**params):
    """
    data will have node, time
    """
    trial_onsets = [[20, 30, 40], [25, 35, 35]]
    length = 3

    ses_dif = []
    zerocount = 0
    broken = 0
    t = []
    offset = params['tau'] + params['kappa']
    # This could be in a main function and the diffs replace max_ses_dif
    for e in np.hstack(trial_onsets):
        ttmp = find_tctc(data[int(e)-offset:int(e+length+offset),:], params['tau'],
                         params['epsilon'], params['sigma'], params['kappa'], rule=rule, raw_signal=raw_signal)
        t.append(ttmp)
        if ttmp.sum() == 0:
            zerocount += 1
    t = np.stack(t)
    ses_dif.append(max_ses_dif(t[:, :, offset:-(offset)], trial_onsets))
    if zerocount > 10:
        broken = 1
        break
    if broken == 1:
        ses_dif = 1
    else:
        ses_dif = np.array(ses_dif).mean()

    #comp = compression(t)
    print('Session difference: ' + str(ses_dif))
    return ses_dif


@use_named_args(space)
def _opt_timepointdiff(**params):
    """
    data will have trial, node, time
    """


@use_named_args(space)
def _opt_templatesim(**params):
    """
    data will have trial, node, time
    """


def opt_tctc(pdata, aramsspace=None, optfun=None, n_calls=50, random_state=None, events=None, **optfunparams):

    if paramsspace is None:
        print('Using default parameter space. Usually this is best to optimize based on your data!')
        df = pd.DataFrame(data={'params': ['tau', 'sigma', 'kappa', 'epsilon'], 'min': [
                          1, 1, 0, 0], 'max': [5, 5, 2, 0.5], 'type': ['int', 'int', 'int', 'real']})

    space = []
    for i, row in df.iterrows():
        if row['type'] == 'int':
            space.append(Integer(row['min'], row['max'], name=row['type']))
        elif row['type'] == 'real':
            space.append(Real(row['min'], row['max'], name=row['type']))

    if isinstance(optfun, str):
        if optfun == 'trialdiff'
            optfun = _opt_trialdiff
        elif optfun == 'timepointdiff'
            optfun = _opt_trialdiff
        elif optfun == 'templatesim'
            optfun = _opt_trialdiff
        else:
            raise ValueError('Unknown optfun')

    res_gp = gp_minimize(optfun(**optfunparams), space,
                         n_calls=n_calls, random_state=random_state)
    return res_gp
