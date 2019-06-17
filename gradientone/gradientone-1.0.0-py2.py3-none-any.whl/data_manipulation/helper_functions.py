import json
from enum import IntEnum

from numpy import histogram, std, cumsum, insert


def my_mean(a_list):
    if len(a_list) == 0:
        return 0
    else:
        return sum(a_list) / float(len(a_list))


def load_json_file(filename='volts.json'):
    with open(filename, 'r') as f:
        return json.loads(f.read())


def get_diffs(vals):
    if not vals:
        return []
    if len(vals) == 1:
        return []
    v1 = 0
    diffs = []
    for v in vals:
        diffs.append(v - v1)
        v1 = v
    del diffs[0]
    return diffs


def get_diffs_btw_edge_vidxs(edge_vidxs=None, volts=None):
    if not edge_vidxs:
        edge_vidxs = get_edge_voltage_indexes(volts)
    return get_diffs(edge_vidxs)


def get_edge_voltage_indexes(volts=None, midpoint=None, filename="volts.json",
                             channel="ch1"):
    if not volts:
        volts = get_volts(filename, channel=channel)
    if not midpoint:
        vmin = min(volts)
        vmax = max(volts)
        midpoint = (vmax - vmin) / 2.0
    edge_vidxs = []
    fall_flag = True
    rise_flag = False
    for i, v in enumerate(volts):
        if fall_flag and v < midpoint:
            edge_vidxs.append(i)
            fall_flag = False
            rise_flag = True
        if rise_flag and v > midpoint:
            edge_vidxs.append(i)
            rise_flag = False
            fall_flag = True
    return edge_vidxs


def get_frequency(filename, channel="ch1", time_bin=None):
    edges = get_edge_voltage_indexes(filename=filename, channel=channel)
    if len(edges) == 1:
        print("No edges for file: ", filename)
        return 0
    diffs = [edges[i] - edges[i - 1] for i in range(1, len(edges))]
    contents = load_json_file(filename)
    if "time_step" in contents.keys():
        time_bin = float(contents["time_step"])
    elif not time_bin:
        time_bin = 1.0
    diff_mean = my_mean(remove_outliers(diffs))
    if time_bin == 0:
        raise ValueError("Time bin is zero")
    if diff_mean == 0:
        raise ValueError("diff mean is zero, pre outlier extraction was:",
                         my_mean(diffs), "len of diffs was:", len(diffs))
    return 1 / (time_bin * 2.0 * diff_mean)


def get_histo(vals, bins=[0, 150, 200, 250, 300], numbins=None):
    if numbins and vals:
        vmax = max(vals)
        vmin = min(vals)
        diff = vmax - vmin
        bin_size = diff / float(numbins)
        bins = [vmin + bin_size * i for i in range(numbins)]

    histo = histogram(vals, bins)
    return histo


def running_mean(x, N):
    _cumsum = cumsum(insert(x, 0, 0))
    return (_cumsum[N:] - _cumsum[:-N]) / N


def get_transition_ranges(volts):
    class State(IntEnum):
        low = 0
        high = 1
        rising = 2
        falling = 3
        unknown = 4
    # calculate the ranges by percentile or by range
    frac = 0.10
    by_percentile = False
    shrink_factor = 1
    mean_bins = 3
    volts = running_mean(volts, mean_bins)
    #volts = ScopeTransmitter().shrink(voltage_list=volts, mode="average",
    #                                  max_length=len(volts)/shrink_factor)
    if by_percentile:
        tenth_percentile = sorted(volts)[int(frac * len(volts))]
        ninetieth_percentile = sorted(volts)[int((1.0 - frac) * len(volts))]
    else:
        tenth_percentile = (max(volts) - min(volts)) * frac + min(volts)
        ninetieth_percentile = (max(volts) - min(volts)) * (1.0 - frac) + min(
            volts)
    # set the initial state
    if volts[0] < tenth_percentile:
        state = State.low
    elif tenth_percentile <= volts[0] < ninetieth_percentile:
        state = State.unknown
    else:
        state = State.high
    rising_start = None
    falling_start = None
    rising_edges = []
    falling_edges = []
    for i in range(1, len(volts)):
        # deal with each of the states. If the next voltage moves outside
        # of the range of values, then it triggers a state transition.
        if state == State.low:
            if volts[i] >= tenth_percentile:
                state = State.rising
                rising_start = i
        elif state == State.high:
            if volts[i] < ninetieth_percentile:
                state = State.falling
                falling_start = i
        elif state == State.rising:
            if volts[i] >= ninetieth_percentile:
                state = State.high
                rising_edges.append([rising_start*shrink_factor, i*shrink_factor])
        elif state == State.falling:
            if volts[i] < tenth_percentile:
                state = State.low
                falling_edges.append([falling_start*shrink_factor, i*shrink_factor])
        # if the state is unknown, wait for it to get into either the low
        # or high range before setting the state
        elif state == State.unknown:
            if volts[i] < tenth_percentile:
                state = State.low
            elif volts[i] >= ninetieth_percentile:
                state = State.high
    return rising_edges, falling_edges, tenth_percentile, ninetieth_percentile


def get_volts(filename="volts.json", channel="ch1"):
    if filename.split(".")[1] == "json":
        contents = load_json_file(filename)
        if "data" in contents.keys():
            if channel in contents["data"].keys():
                return [float(val) for val in contents["data"][
                    channel] if len(str(val)) > 0 ]
    if filename.split(".")[1] == "csv":
        fh_lines = open(filename, "r").readlines()
        return [float(fh_lines[i].split(",")[0]) for i in range(1, len(fh_lines))]


def get_times(filename="volts.json", channel="ch1"):
    if filename.split(".")[1] == "json":
        contents = load_json_file(filename)
        if "time_step" in contents.keys():
            time_step = float(contents["time_step"])
        if "data" in contents.keys():
            if channel in contents["data"].keys():
                num_points = len(contents["data"][channel])
    return [i*time_step for i in range(num_points)]


def remove_outliers(data, sigma=3):
    prev_length = -1
    while prev_length != len(data):
        prev_length = len(data)
        data = [val for val in data if abs(val-my_mean(data)) < sigma*std(data)]
    return data

