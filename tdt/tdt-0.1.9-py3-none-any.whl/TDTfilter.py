import copy
import warnings

import numpy as np

def combine_time(tr1, tr2, logic):
    """logically combine two given time ranges with AND or OR operation
    e.g. tr1 = np.array([[6,2.5,5,8],[10,4,5.4,9]])
         tr2 = np.array([[3,5.2,7.5],[4,5.3,8.5]])
    combine_time(tr1, tr2, 'OR') = [[2.5, 5, 6],[4, 5.4, 10]]
    combine_time(tr1, tr2, 'AND') = [[2.5, 5, 6],[4, 5.4, 10]]
    """
    
    if tr1.shape[0] != 2 or tr2.shape[0] != 2:
        raise Exception('invalid time range size')
    
    max_ranges_possible = tr1.shape[1] + tr2.shape[1]
    valid_ranges = np.zeros((2, max_ranges_possible))

    # start with first time range, check the end timestamps and cut short if necessary
    valid_ind = -1
    if logic.upper() == 'AND':
        # put them in order
        id = np.argsort(tr1, 1)
        tr1 = tr1[:, id[0,:]]
        id = np.argsort(tr2, 1)
        tr2 = tr2[:, id[0,:]]
        for ii in range(tr1.shape[1]):
            start1 = tr1[0,ii]
            stop1 = tr1[1,ii]
            for jj in range(tr2.shape[1]):
                start2 = tr2[0,jj]
                stop2 = tr2[1,jj]
                if start2 > stop1:
                    # tr2 is already passed the end of tr1
                    # stop checking and move to next one
                    break
                if stop2 <= start1:
                    # tr2 ends before the beginning of tr1, skip
                    continue
                if valid_ind > -1:
                    if start1 > valid_ranges[0,valid_ind] and start1 < valid_ranges[1, valid_ind]:
                        valid_ranges[0, valid_ind] = start1
                        # if start1 is within last valid range, use it
                        # check end time
                        valid_ranges[1, valid_ind] = np.minimum(valid_ranges[1, valid_ind], stop1)
                        continue
                start_valid = np.maximum(start1, start2)
                stop_valid = np.minimum(stop1, stop2)
                valid_ind += 1
                valid_ranges[:,valid_ind] = [start_valid, stop_valid]

    elif logic.upper() == 'OR':
        # put all time ranges in order of starting time stamp
        all_ranges = np.concatenate((tr1.T, tr2.T)).T
        id = np.argsort(all_ranges,1)
        all_ranges = all_ranges[:, id[0,:]]
        
        # loop through ranges
        for ii in range(all_ranges.shape[1]):
            start1 = all_ranges[0, ii]
            stop1 = all_ranges[1, ii]
            
            if ii == 0:
                # first range is starting valid range
                curr_start_valid = start1
                curr_stop_valid = stop1
                valid_ind += 1
                valid_ranges[:,valid_ind] = [curr_start_valid, curr_stop_valid]
                continue
            
            if start1 <= curr_stop_valid and stop1 > curr_stop_valid:
                # if new time range is inside old one but end overlaps, use new end and loop
                curr_stop_valid = stop1
                valid_ranges[1, valid_ind] = curr_stop_valid
                continue
            
            if start1 > curr_stop_valid:
               # create new valid
               curr_start_valid = start1
               curr_stop_valid = stop1
               valid_ind += 1
               valid_ranges[:,valid_ind] = [curr_start_valid, curr_stop_valid]
    else:
        raise Exception("logic input {0} is not valid, use 'OR' or 'AND'".format(logic))
        
    valid_ranges = valid_ranges[:,:valid_ind+1]
    return valid_ranges

def get_valid_ind(ts, time_ranges):
    """compare timestamps against all time_ranges
    only keep timestamps that are included inside a time_ranges interval
    e.g. ts = [1, 2, 3, 2.5, 4.5, 3.5, 4, 5]
         time_ranges = [[3, 5], 
                        [4, 6]]
    include timestamps that are on [3, 4) or [5, 6)
    returns [2 5 7]
    valid time stamps are then ts[get_valid_ind(ts, time_ranges)]
    """
    
    # preallocate
    keep = np.zeros(len(ts), dtype=np.uint64)
    keep_ind = 0
    
    # loop over all ts and see if we want to keep it
    for j in range(len(ts)):
        ind1 = ts[j] >= time_ranges[0,:]
        ind2 = ts[j] < time_ranges[1,:]
        if np.any(ind1 & ind2):
            keep[keep_ind] = j
            keep_ind += 1
        
    # truncate
    keep = keep[:keep_ind]
    return keep
    
def epoc_filter(data, epoc, *, values=None, modifiers=None, t=None, tref=False, keepdata=True):
    """TDT tank data filter. Extract data around epoc events.
    data = epoc_filter(data, epoc) where data is the output of read_block,
    epoc is the name of the epoc to filter on, and parameter value pairs
    define the filtering conditions.
    
    If no parameters are specified, then the time range of the epoc event
    is used as a time filter.
    
    Also creates data.filter, a string that describes the filter applied.
    Optional keyword arguments:
        values      specify array of allowed values
                      ex: tempdata = epoc_filter(data, 'Freq', values=[9000, 10000])
                        > retrieves data when Freq = 9000 or Freq = 10000
        modifiers   specify array of allowed modifier values.  For example,
                      only allow time ranges when allowed modifier occurred
                      sometime during that event, e.g. a correct animal response.
                      ex: tempdata = epoc_filter(data, 'Resp', modifiers=[1])
                        > retrieves data when Resp = 1 sometime during the allowed
                        time range.
        t           specify onset/offset pairs relative to epoc onsets. If the
                      offset is not provided, the epoc offset is used.
                      ex: tempdata = epoc_filter(data, 'Freq', t=[-0.1, 0.5])
                        > retrieves data from 0.1 seconds before Freq onset to 0.4
                          seconds after Freq onset. Negative time ranges are discarded.
        tref        use the epoc event onset as a time reference. All timestamps for
                      epoc, snippet, and scalar events are then relative to epoc onsets.
                      ex: tempdata = epoc_filter(data, 'Freq', tref=True)
                        > sets snippet timestamps relative to Freq onset
        keepdata    keep the original stream data array and add a field called
                      'filtered' that holds the data from each valid time range. 
                      Defaults to True.
    
    IMPORTANT! Use a time filter (t argument) only after all value filters have been set.
    """
    
    data = copy.deepcopy(data)
    
    filter_string = ''

    if not hasattr(data, 'epocs'):
        raise Exception('no epocs found')
    elif len(data.epocs.keys()) == 0:
        raise Exception('no epocs found')

    fff = data.epocs.keys()
    match = '';
    all_names = []
    for k in data.epocs.keys():
        all_names.append(data.epocs[k].name)
        if data.epocs[k].name == epoc:
            match = k

    if not hasattr(data.epocs, match):
        raise Exception('epoc {0} is not a valid epoc event, valid events are: {1}'.format(epoc, all_names))

    if t:
        try:
            if len(t) > 2:
                raise Exception('{0} t vector must have 1 or 2 elements only'.format(repr(t)))
        except:
            raise Exception('{0} t vector must have 1 or 2 elements only'.format(repr(t)))
    
    ddd = data.epocs[match]

    time_ranges = None
    
    # VALUE FILTER, only use time ranges where epoc value is in filter array
    if values:
        # find valid time ranges
        try:
            # use this for numbers
            valid = np.isclose(ddd.data, values)
        except:
            try:
                # use this for Note strings
                valid = np.isin(ddd.data, values)
            except:
                raise Exception('error in valud filter')
        
        time_ranges = np.vstack((ddd.onset[valid], ddd.offset[valid]))

        # create filter string
        filter_string = '{0}:VALUE in [{1}];'.format(epoc, ','.join([str(v) for v in values]))

        # AND time_range with existing time ranges
        if hasattr(data, 'time_ranges'):
            time_ranges = combine_time(time_ranges, data.time_ranges, 'AND')
            data.time_ranges = time_ranges
    
    # modifiers FILTER, only use time ranges where modifier epoc value is in array
    if modifiers:
        if not hasattr(data, 'time_ranges'):
            raise Exception('no valid time ranges to modify')
        
        time_ranges = data.time_ranges
        
        # only look at epocs in our modifier set
        ddd.onset = ddd.onset[np.isclose(ddd.data, modifiers)]
        
        # loop through all current time ranges
        keep = np.zeros(time_ranges.shape[1])
        for i in range(time_ranges.shape[1]):
            # if valid modifier is in this time range, keep it
            for j in range(len(ddd.onset)):
                if ddd.onset[j] >= time_ranges[0,i] and ddd.onset[j] < time_ranges[1,i]:
                    keep[i] = 1

        # remove duplicates
        data.time_ranges = time_ranges[:, keep==1]
        
        # create filter string
        filter_string = '{0}:MODIFIER in [{1}];'.format(epoc, ','.join([str(s) for s in modifiers]))

    #TIME FILTER
    t1 = 0
    t2 = np.nan
    if t:
        t1 = t[0]
        if len(t) == 2:
            t2 = t[1]
        
        if not time_ranges:
            # preallocate
            time_ranges = np.zeros((2, len(ddd.onset)))
            for j in range(len(ddd.onset)):
                time_ranges[:, j] = [ddd.onset[j], ddd.offset[j]]
        else:
            time_ranges = data.time_ranges
        
        # find valid time ranges
        for j in range(time_ranges.shape[1]): #= 1:size(time_ranges,2)
            if np.isnan(t2):
                time_ranges[:, j] = [time_ranges[0,j]+t1, time_ranges[1,j]]
            else:
                time_ranges[:, j] = [time_ranges[0,j]+t1, time_ranges[0,j]+t1+t2]
        
        # throw away negative time ranges
        if np.all(~np.isnan(time_ranges)):
            time_ranges = time_ranges[:,time_ranges[0,:]>0]
        
        # create filter string
        if np.isnan(t2):
            filter_string = 'TIME:{0} [{1}];'.format(epoc, np.round(t1,2))
        else:
            filter_string = 'TIME:{0} [{1}:{2}];'.format(epoc, np.round(t1,2), np.round(t2,2))
        data.time_ranges = time_ranges
        data.time_ref = [t1, t2]

    
    # TREF FILTER
    if tref:
        filter_string += 'REF:{0}'.format(epoc)
        if hasattr(tref, "__len__"):
            if len(tref) > 1:
                t1 = tref[0]
    
    if values or modifiers or t or tref:
        pass
    else:
        # no filter specified, use EPOC time ranges
        time_ranges = np.concatenate((ddd.onset.T, ddd.offset.T))
        # AND time_range with existing time ranges
        if hasattr(data, 'time_ranges'):
            time_ranges = combine_time(time_ranges, data.time_ranges, 'AND')
            data.time_ranges = time_ranges
        filter_string = 'EPOC:{0};'.format(epoc)
        
    # set filter string
    if hasattr(data, 'filter'):
        data.filter += filter_string
    else:
        data.filter = filter_string

    time_ranges = data.time_ranges

    # FILTER ALL EXISTING DATA ON THESE TIME RANGES
    # filter streams
    if data.streams:
        for k in data.streams.keys():
            fs = data.streams[k].fs
            filtered = []
            max_ind = max(data.streams[k].data.shape)
            for j in range(time_ranges.shape[1]):
                onset = np.uint64(np.round(time_ranges[0,j]*fs))
                offset = np.uint64(np.round(time_ranges[1,j]*fs)+1)
                # throw it away if onset or offset extends beyond recording window
                if np.isinf(offset):
                    if onset <= max_ind and onset > 0:
                        if data.streams[k].data.ndim == 1:
                            filtered.append(data.streams[k].data[onset:])
                        else:
                            filtered.append(data.streams[k].data[:,onset:])
                        break
                else:
                    if offset <= max_ind and offset > 0 and onset <= max_ind and onset > 0:
                        if data.streams[k].data.ndim == 1:
                            filtered.append(data.streams[k].data[onset:offset])
                        else:
                            filtered.append(data.streams[k].data[:,onset:offset])
            if keepdata:
                data.streams[k].filtered = filtered
            else:
                data.streams[k].data = filtered
                data.streams[k].pop('filtered')
    
    # filter snips
    if data.snips:
        warning_value = -1
        for k in data.snips.keys():
            ts = data.snips[k].ts
            
            # preallocate
            keep = np.zeros(len(ts), dtype=np.uint64)
            diffs = np.zeros(len(ts)) # for relative timestamps
            keep_ind = 0
            
            for j in range(len(ts)):
                ind1 = ts[j] > time_ranges[0,:]
                ind2 = ts[j] < time_ranges[1,:]
                ts_ind = np.where(ind1 & ind2)[0]
                if len(ts_ind) > 0:
                    if len(ts_ind) > 1:
                        min_diff = np.min(np.abs(time_ranges[1, ts_ind[0]]-time_ranges[1, ts_ind[1]]), np.abs(time_ranges[1, ts_ind[0]]-time_ranges[1, ts_ind[1]]))
                        warning_value = min_diff
                        continue
                    keep[keep_ind] = np.uint64(j)
                    diffs[keep_ind] = ts[j] - time_ranges[0, ts_ind] + t1; # relative ts
                    keep_ind += 1
            
            if warning_value > 0:
                warnings.warn('time range overlap, consider a maximum time range of %.2fs'.format(warning_value), Warning)
            
            # truncate
            keep = keep[:keep_ind]
            diffs = diffs[:keep_ind]
            if hasattr(data.snips[k], 'data'):
                if len(data.snips[k].data) > 0:
                    data.snips[k].data = data.snips[k].data[keep]
            
            if tref:
                data.snips[k].ts = diffs
            else:
                data.snips[k].ts = data.snips[k].ts[keep]
            
            # if there are any extra fields, keep those
            for kk in data.snips[k].keys():
                if kk in ['ts', 'name', 'data', 'sortname', 'fs', 'code', 'size', 'type', 'dform']:
                    continue
                if len(data.snips[k][kk]) >= np.max(keep):
                    data.snips[k][kk] = data.snips[k][kk][keep]
    
    # filter scalars, include if timestamp falls in valid time range
    if data.scalars:
        for k in data.scalars.keys():
            ts = data.scalars[k].ts
            keep = get_valid_ind(ts, time_ranges);
            if keep:
                # scalars can have multiple rows
                if data.scalars[k].data.ndim > 1:
                    data.scalars[k].data = data.scalars[k].data[:,keep]
                else:
                    data.scalars[k].data = data.scalars[k].data[keep]
                data.scalars[k].ts = data.scalars[k].ts[keep]
            else:
                data.scalars[k].data = []
                data.scalars[k].ts = []

    # filter epocs, include if onset falls in valid time range
    if data.epocs:
        for k in data.epocs.keys():
            ts = data.epocs[k].onset
            keep = get_valid_ind(ts, time_ranges)
            if len(keep) > 0:
                data.epocs[k].data = data.epocs[k].data[keep]
                data.epocs[k].onset = data.epocs[k].onset[keep]
                if hasattr(data.epocs[k], 'notes'):
                    if hasattr(data.epocs[k].notes, 'ts'):
                        keep2 = get_valid_ind(data.epocs[k].notes.ts, time_ranges)
                        data.epocs[k].notes.ts = data.epocs[k].notes.ts[keep2]
                        data.epocs[k].notes.index = data.epocs[k].notes.index[keep2]
                        data.epocs[k].notes.notes = data.epocs[k].notes.notes[keep2]
                    else:
                        data.epocs[k].notes = data.epocs[k].notes[keep]
                if hasattr(data.epocs[k], 'offset'):
                    data.epocs[k].offset = data.epocs[k].offset[keep]
            else:
                data.epocs[k].data = []
                data.epocs[k].onset = []
                if hasattr(data.epocs[k], 'offset'):
                    data.epocs[k].offset = []
                if hasattr(data.epocs[k], 'notes'):
                    data.epocs[k].notes = []
    
    return data
    
if __name__ == '__main__':
    pass
    
    #import sys
    #import matplotlib.pyplot as plt

    '''# LFP example
    BLOCK_PATH = 'F:\\svn\\TDT\\C_TDT_STUFF\\Examples\\TDTMatlabSDK\\Examples\\ExampleData\\Algernon-180308-130351'
    data = read_block(BLOCK_PATH, evtype=['epocs','scalars','streams'], channel=3)
    #data = read_block(BLOCK_PATH, evtype=['epocs','scalars','streams'])
    data2 = epoc_filter(data, 'PC0/', t=[-0.3, 0.8])
    '''

    '''# test get_valid_ind
    ts = np.array([1, 2, 3, 2.5, 4.5, 3.5, 4, 5])
    time_ranges = np.array([[3,5],[4,6]])
    ggg = get_valid_ind(ts, time_ranges)
    print(time_ranges)
    print('valid_ind', ggg)
    print(ts[ggg])
    '''
    
    '''# test combine_time 'AND'
    tr1 = np.array([[2.5,5,8],[4,6,9]])
    tr2 = np.array([[3,5,8],[4,6,8.5]])
    ggg = combine_time(tr1, tr2, 'AND')
    print(tr1)
    print(tr2)
    print('valid_range', ggg)
    tr1 = np.array([[7.1,6,2.5,5],[9,7,4,5.4]])
    tr2 = np.array([[3,5.2,6.3,7.5],[4,5.3,7.1,8.5]])
    ggg = combine_time(tr1, tr2, 'AND')
    print(tr1)
    print(tr2)
    print('valid_range\n', ggg)
    '''
    
    '''# test combine_time 'OR'
    #tr1 = np.array([[6,2.5,5,8],[10,4,5.4,9]])
    #tr2 = np.array([[3,5.2,7.5],[4,5.3,8.5]])
    tr1 = np.array([[7.1,6,2.5,5],[9,7,4,5.4]])
    tr2 = np.array([[3,5.2,6.3,7.5],[4,5.3,7.1,8.5]])
    ggg = combine_time(tr1, tr2, 'OR')
    print(tr1)
    print(tr2)
    print('valid_range\n', ggg)
    '''
    