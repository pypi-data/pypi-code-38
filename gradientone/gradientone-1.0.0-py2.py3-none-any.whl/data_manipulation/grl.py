import sys
import gzip
import json
import requests
from math import log10
from struct import pack

try:
    from __builtin__ import xrange
except ImportError:
    xrange = range

from requests_toolbelt.multipart.encoder import MultipartEncoder
from helper_functions import get_diffs, \
    get_diffs_btw_edge_vidxs, get_edge_voltage_indexes, get_histo, \
    load_json_file, my_mean


def binary_type(input):
    if int(sys.version[0]) < 3:
        return input
    else:
        return bytes(input, "utf-8")

TIMESTEP = 2.0e-08
START_TIME = -0.0199999852498

COMPANYNAME = 'GradientOne'
DOMAIN = 'gradientone-dev1.appspot.com'
# COMPANYNAME = 'Acme'
# DOMAIN = 'gradientone-dev2.appspot.com'

GATEWAY_ID = 'SD1'
SOFTWARE = 'version 1.0'

MAX_LENGTH_FOR_BROWSER = 100000
DEBUG_ON = True
SIMULATED = False
USE_GZIP = True
OAUTH2_ACTIVE = False
DEFAULT_LOGFILE = 'info.log'
ELIGIBLE_LOGFILE_SIZE = 2000000
MAX_NUM_LOGFILES = 10
DEFAULT_UI = 160


def write_to_json_file(filename, data=None):
    print("writing to file:", filename)
    with open(filename, 'wb') as f:
        output = json.dumps(data)
        #f.write(pack('5B', *output))
        f.write(binary_type(output))


def get_fall_idxs(volts, midpoint=0.6853):
    fall_idxs = []
    fall_flag = False
    for i, v in enumerate(volts):
        if v > midpoint:
            fall_flag = True
        if fall_flag and v < midpoint:
            fall_idxs.append(i)
            fall_flag = False
    return fall_idxs


def get_rise_ends(volts):
    rise_ends = []
    rise_flag = False
    for i, v in enumerate(volts):
        if v < 0:
            rise_flag = True
        if rise_flag and v > 0:
            rise_ends.append(i)
            rise_flag = False
    return rise_ends


def get_meanperiods(vals):
    diffs = get_diffs(vals)
    return my_mean(diffs)


def append_ui(slices, volts, vidx, ui):
    slices.append(volts[vidx:vidx + ui])
    return vidx + ui


def get_slices_by_centers(volts, ui=DEFAULT_UI):
    histo = get_histo(volts, numbins=100)
    print("voltage histogram:", histo)
    bins = histo[1]
    next_ui_start = 0
    slices = []
    skip_until_next_start = True
    for i, v in enumerate(volts):
        if i == next_ui_start:
            skip_until_next_start = False
        elif skip_until_next_start:
            continue
        if bins[49] < v < bins[50]:
            slice_start = i
            slice_end = i + ui
            slices.append(volts[slice_start:slice_end])
            next_ui_start = i + ui
            skip_until_next_start = True

    print("len(slices) for overlay", len(slices))
    return slices


def get_slices_by_centers_drift(volts, ui=DEFAULT_UI):
    """Returns slices using a centers with drifting ui algorithm

       Gets slices by checking when volts cross the centerline for
       starts and ends. This uses the ui to check minimum width for
       an eye and then uses a 'drifting' or dynamic ui for the exact
       slice rather than a fixed ui
    """
    histo = get_histo(volts, numbins=100)
    print("voltage histogram:", histo)
    bins = histo[1]
    next_ui_start = 0
    slices = []
    start_flag = True
    end_flag = False
    ui_start_idx = 0
    actual_ui_list = []
    skip_until_next_start = True
    for i, v in enumerate(volts):
        if i == next_ui_start:
            skip_until_next_start = False
            start_flag = True
        elif skip_until_next_start:
            continue
        if i > ui_start_idx + ui * 0.75:
            end_flag = True
        if start_flag and bins[48] < v < bins[52]:
            ui_start_idx = i
            start_flag = False
        elif end_flag and bins[48] < v < bins[52]:
            ui_end_idx = i
            actual_ui = ui_end_idx - ui_start_idx
            actual_ui_list.append(actual_ui)
            slice_start = ui_start_idx
            slice_end = ui_end_idx
            slices.append(volts[slice_start:slice_end])
            next_ui_start = i + ui
            skip_until_next_start = True
            end_flag = False
    print("len(slices) for overlay", len(slices))
    print("mean actual ui:", my_mean(actual_ui_list))
    return slices


def get_slices_by_highlows(volts):
    """Gets slices using highlow starts and fixed ui algorithm"""
    histo = get_histo(volts, numbins=100)
    bins = histo[1]
    print("histo of volts", histo)
    slices = []
    next_start = 0
    ui = 160
    skip_until_next_start = True
    for i, v in enumerate(volts):
        if i == next_start:
            skip_until_next_start = False
        if skip_until_next_start:
            continue
        if v < bins[1] or v > bins[98]:
            slices.append(volts[i:i + ui])
            next_start = i + ui
            skip_until_next_start = True
    return slices


def get_overlay(volts, ui):
    """Returns and overlay of voltage slices for an eye diagram"""
    overlay = []
    for i in range(int(ui)):
        overlay.append([])
    slices = get_slices_by_centers(volts, 165)
    # alternative ways to get slices for the overlay
    # slices = get_slices(volts, ui)
    # slices = get_slices_by_highlows(volts, ui)
    for slc in slices:
        for i, voltage in enumerate(slc):
            if i > len(overlay) - 1:
                overlay.append([])
            overlay[i].append(round_sig(voltage))
    return overlay


def get_overlay_with_drift(volts, slice_num=10):
    volt_slices = partition(volts, slice_num)
    tmp_overlays = []
    for i, volt_slice in enumerate(volt_slices):
        print("getting temp overlay for slice idx:", i)
        edge_vidxs = get_edge_voltage_indexes(volt_slice)
        diffs_btw_edges = get_diffs_btw_edge_vidxs(edge_vidxs)
        ui = DEFAULT_UI
        # if ui drifts, you need a new one each time
        # ui = get_ui(diffs_btw_edges)
        print("counting occurences of vdiffs btw edges:")
        get_counts(diffs_btw_edges)
        tmp = get_overlay(volt_slice, ui)
        tmp_overlays.append(tmp)
    return overlay_overlays(tmp_overlays)


def overlay_overlays(overlays):
    longest_overlay = get_longest(overlays)
    master_overlay = [[] for i in range(len(longest_overlay))]
    for overlay in overlays:
        for i, column in enumerate(overlay):
            master_overlay[i].extend(column)
    return master_overlay


def get_longest(list_of_lists):
    max_len = 0
    longest = []
    for lst in list_of_lists:
        if len(lst) > max_len:
            max_len = len(lst)
            longest = lst
    return longest


def partition(lst, n):
    division = len(lst) / float(n)
    return [lst[int(round(division * i)): int(round(division * (i + 1)))] for i in xrange(n)]  # nopep8


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    pass


def get_slices(lst, n):
    """ return successive n-sized slices from l.
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def open_gzip(file='file.txt.gz'):
    with gzip.open(file, 'rb') as f:
        return f.read()


def convert_to_counts(overlay):
    counts_of_volts_for_each_x = []
    for x_idx, volts_at_one_x in enumerate(overlay):
        # make sure volts_at_one_x is a list
        volts_at_one_x = volts_at_one_x if type(volts_at_one_x) == list else [volts_at_one_x]
        set_of_volts = set(volts_at_one_x)
        counts_at_one_x = []
        for v in set_of_volts:
            sys.stdout.write(
                "\rcounting x index:%s voltage:%s at  " % (x_idx, v))
            count = volts_at_one_x.count(v)
            counts_at_one_x.append((v, count))
        counts_of_volts_for_each_x.append(counts_at_one_x)
    return counts_of_volts_for_each_x


def get_high_counts(counts_of_volts_over_time):
    print("finding high counts...")
    high_counts = []
    for counts_of_volts in counts_of_volts_over_time:
        for count in counts_of_volts:
            if count[1] > 5:
                high_counts.append(count)
    return high_counts


def get_eye_diagram_data(counts_of_volts_over_time):
    eye_data = []
    for idx, counts_of_volts in enumerate(counts_of_volts_over_time):
        eye_data.append((idx * TIMESTEP + START_TIME, counts_of_volts))
    return eye_data


def round_dec(val, decimal_place=3):
    """Rounds to a given decimal place and rounds up on 5
       >>> round_dec(0.0045)
       0.005
       >>> round_dec(4.5e-05)
       0.0
       >>> round_dec(4.5e-05, 5)
       5e-05
       """
    val += 0.01 * 10 ** -decimal_place
    rounded_val = round(val, decimal_place)
    if rounded_val > 1e+36:
        rounded_val = float(str(rounded_val))
    return rounded_val


def round_sig(val, digits=3):
    """Rounds value to specified significant digits by determining
       decimal place needed to round number value and calling round_dec
       >>> round_sig(6.3193e-9)
       6.32e-09
       >>> round_sig(6.3193e-9, 4)
       6.319e-09
       >>> round_sig(0.55550)
       0.556
       """
    if val == 0:
        return 0.0
    decimal_place = int(-log10(abs(val))) + digits
    return float(str(round_dec(val, decimal_place)))


def gzip_and_post_file(file, file_key='', command_id=''):
    gzip_file = file + '.gz'
    if not file_key:
        file_key = gzip_file
    with open(file) as f_in, gzip.open(gzip_file, 'wb') as f_out:
        f_out.write(binary_type(f_in.read()))
    data_type = 'application/x-gzip'
    multipartblob = MultipartEncoder(
        fields={
            'file': (gzip_file, open(gzip_file, 'rb'), data_type),
            'command_id': command_id,
            'dec_factor': '1',
            'file_key': file_key,
        }
    )
    blob_url = requests.get("https://" + DOMAIN + "/upload/geturl")
    response = requests.post(blob_url.text, data=multipartblob,
                             headers={
                                'Content-Type': multipartblob.content_type})
    print(response.text)


def get_mode(alist):
    vals = set(alist)
    mode_count = 0
    mode_val = 0
    for val in vals:
        count = alist.count(val)
        if count > mode_count:
            mode_val = val
            mode_count = count
    return mode_val


def get_idle_line_idxs(volts, idle_voltage=1.379175, idle_threshold=1000):
    """Returns a list of tuples with the endpoint indexes idle lines"""
    idle_count = 0
    idle_start_idx = 0
    idle = False
    active_signal = False
    idle_line_idxs = []
    for i, v in enumerate(volts):
        # if previously active and now idle:
        if active_signal and v == idle_voltage:
            # mark the index for a potential idle line start
            idle_start_idx = i
        # check if idle and count, else mark active signal
        if v == idle_voltage:
            idle_count += 1
            active_signal = False
        else:
            active_signal = True
        # if idling long enough declare the line idle
        if idle_count > idle_threshold:
            idle = True
        # check for end of idle line
        if idle and v != idle_voltage:
            idle_line_idxs.append((idle_start_idx, i))
            active_signal = True
            idle = False
            idle_count = 0
    return idle_line_idxs


def get_sections(volts, idle_line_ends):
    sections = []
    start_idx = 0
    for i in idle_line_ends:
        section = volts[start_idx:i]
        if len(section) < 1:
            continue
        sections.append(section)
        start_idx = i
    return sections


def overlay_and_post_sections(sections, period, o_id='2016121519'):
    for i, section in enumerate(sections):
        overlay = get_overlay(section, int(period))
        print("length of overlay", len(overlay))
        # Get the counts and post
        counts_of_volts_over_time = convert_to_counts(overlay)
        file = 'counts_of_volts_over_time_rounded-' + str(i) + '.json'
        write_to_json_file(file, counts_of_volts_over_time)
        file_id = o_id + str(i)
        gzip_and_post_file(file, file_id)
    print(o_id)


def get_timestep(waveform=None):
    if not waveform:
        return TIMESTEP
    last_x = 0
    last_ts = 0
    for pt in waveform:
        ts = pt[0] - last_x
        if ts != last_ts:
            print("new ts:", ts)
        last_ts = ts
        last_x = pt[0]
    return last_ts


def get_counts(alist):
    valset = set(alist)
    counts = []
    for v in sorted(valset):
        tup = (v, alist.count(v))
        counts.append(tup)
        print("val: %s , count: %s" % tup)
    return counts


def get_occurrences(alist, value):
    return [i for i, x in enumerate(alist) if x == value]


def get_diffs_btw_falls():
    # Get the volts and break into sections divided by idle lines
    volts = load_json_file('volts.json')

    # Find the period
    vmin = min(volts)
    vmax = max(volts)
    midpoint = (vmax - vmin) / 2.0
    fall_idxs = get_fall_idxs(volts, midpoint)
    period = 160
    print("using period", period)
    diffs = get_diffs(fall_idxs)
    print("set of diffs between falls", set(diffs))
    get_counts(diffs)
    return diffs


def get_bits_and_vdiffs(diffs_btw_edges=None, nbits=365):
    bits = []
    short = False
    vdiffs = []
    for vdiff in diffs_btw_edges:
        vdiffs.append(vdiff)
        if short and vdiff < 106:
            bits.append(1)
            short = False  # reset short marker
        elif vdiff < 106:
            short = True
        else:
            bits.append(0)
            short = False
        if len(bits) == nbits:
            return bits, vdiffs
    print("returning less than %s bits" % nbits)
    return bits, vdiffs


def get_bits_and_vdiffs_by_edge_idx(start_edge_idx=96, nbits=365):
    # get_edges
    diffs_btw_edges = get_diffs_btw_edge_vidxs()
    return get_bits_and_vdiffs(diffs_btw_edges[start_edge_idx:], nbits)


def get_ui(preamble_voltages_btw_edges):
    if not preamble_voltages_btw_edges:
        return DEFAULT_UI
    mean = my_mean(preamble_voltages_btw_edges)
    lows = [x for x in preamble_voltages_btw_edges if x < mean]
    lowmean = my_mean(lows)
    highs = [x for x in preamble_voltages_btw_edges if x > mean]
    highmean = my_mean(highs)
    lms = lowmean * 2 * len(lows)
    hms = highmean * len(highs)
    ui = (lms + hms) / len(lows + highs)
    return ui


def get_midpoint(volts):
    vmin = min(volts)
    vmax = max(volts)
    midpoint = (vmax - vmin) / 2.0
    return midpoint


def get_preamble(diffs_btw_edges):
    bits, vdiffs = get_bits_and_vdiffs(diffs_btw_edges)
    SOP_start_idx = find_sequence([0, 0, 0, 1, 1], bits)
    print("SOP_start_idx", SOP_start_idx)
    print("Preamble end_idx", SOP_start_idx - 1)
    return bits[:SOP_start_idx]


def find_sequence(sequence, bits):
    """Returns index of first match of sequence in a list of bits"""
    if len(sequence) > len(bits):
        return False
    for index, bit in enumerate(bits):
        current = bits[index:index + len(sequence)]
        if sequence == current:
            return index
    # if no match found
    return False


def get_volts_for_overlay(preamblebits=64, overlay_start_edge_idx=96,
                          volts_file='volts.json'):
    """Gets the volts for the overlay plot. Reads a preamble and then reads
    volts for the overlay. The overlay_start_edge_idx is 96 by default to match
    the end of a 64 bit bmc preamble, but this can be tweaked if needed"""
    all_volts = load_json_file(volts_file)
    print("len(all_volts)", len(all_volts))
    midpoint = get_midpoint(all_volts)

    # volts = all_volts
    # calculate the idle voltage - commented if known to be 1.379175
    # idle_voltage = get_mode(volts)
    # get the idle line ends
    idle_line_idxs = get_idle_line_idxs(all_volts)
    print("idle_line_idxs:", idle_line_idxs)

    # get idxs for 3rd pulse
    v_start = idle_line_idxs[2][1]
    v_end = idle_line_idxs[3][0]
    volts = all_volts[v_start:v_end]
    print("len(volts) from idles", len(volts))

    # get the voltage indexs of rising and falling edges of waveform
    edge_vidxs = get_edge_voltage_indexes(volts, midpoint)
    print("len(edge_vidxs)", len(edge_vidxs))

    # get the number of voltage vdiffs between edges
    diffs_btw_edges = get_diffs_btw_edge_vidxs(edge_vidxs)
    print("len(diffs_btw_edges)", len(diffs_btw_edges))

    # for BMC the last edge index of preamble is number of bits * 1.5
    pre_end_edge_idx = int(preamblebits * 1.5)
    print("preamble end edge index (last edge of preamble)", pre_end_edge_idx)
    preamble_voltages_btw_edges = diffs_btw_edges[:pre_end_edge_idx]
    ui = get_ui(preamble_voltages_btw_edges)
    print("estimated ui from preamble", ui)

    # get number of vdiffs btw edges for overlay to then find bits
    print("index of first edge of overlay", overlay_start_edge_idx)
    overlay_diffs = diffs_btw_edges[overlay_start_edge_idx:]
    bits, overlay_vdiffs = get_bits_and_vdiffs(overlay_diffs, nbits=500)
    print("bits to be overlayed:", bits)
    print("len(bits)", len(bits))
    print("total vdiffs for these bits", sum(overlay_vdiffs))

    print("preamble start voltage idx", edge_vidxs[0])
    preamble_end_vidx = edge_vidxs[0] + sum(preamble_voltages_btw_edges)
    print("preamble end voltage idx", preamble_end_vidx)

    #######################################################################
    # Sometimes there is a gap between the end of preamble and start of
    # the volts for overlay. Ideally there is no gap, but this section
    # would allow for handling gaps
    # gap_edge_indxs = edge_vidxs[pre_end_edge_idx:overlay_start_edge_idx]
    # if gap_edge_indxs:
    #     gap_nsbte = get_diffs_btw_edge_vidxs(gap_edge_indxs)
    # else:
    #     gap_nsbte = []
    # o_start_vidx = preamble_end_vidx + sum(gap_nsbte)
    #######################################################################

    # With the indexes from preamble and the diffs between edges of overlay,
    # grab the section of the list of volts to be used for the overlay
    o_start_vidx = preamble_end_vidx
    o_end_vidx = o_start_vidx + sum(overlay_vdiffs)
    print("overlay - start_idx: %s , end_idx: %s" % (o_start_vidx, o_end_vidx))
    volts_for_overlay = volts[o_start_vidx:o_end_vidx]

    return volts_for_overlay


def count_and_post(overlay, file_key=''):
    """Get the counts and post"""
    counts_of_volts_over_time = convert_to_counts(overlay)
    file = 'counts_of_volts_over_time_rounded.json'
    write_to_json_file(file, counts_of_volts_over_time)
    gzip_and_post_file(file, file_key=file_key)
    print("file_key:", file_key)
    return counts_of_volts_over_time


def run():
    volts_for_overlay = get_volts_for_overlay()
    print("len(volts_for_overlay)", len(volts_for_overlay))
    # overlay = get_overlay_with_drift(volts_for_overlay)
    # counts = count_and_post(overlay)
    # return counts


if __name__ == "__main__":
    # run, overlay, count
    overlay_volts_counts = run()
