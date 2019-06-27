"""
This is used to merge multiple CSV file, created after we realized that MergeTool written in Java doesn't handle
FIPS columns properly (removes zeros)

Assumes that all of the files to be merged use Geo_FIPS columng as their key.

v0.1
"""

import pandas as pd
import os
import sys
import time

from loguru import logger as log


def cols_to_remove(cols, pkeys):
    """
    remove repeating columns
    :return:
    """
    cols_rm = [i for i in cols if i in cols_list and i not in pkeys]
    cols_list.extend(cols)
    return cols_rm


def read_and_merge(fn, keys_values, str_keys, wf=''):
    stats = []  # get some statistics for error checking
    dtype = {}
    main_df = pd.DataFrame()
    for i, f in enumerate(fn):
        if str_keys:
            dtype = {keys_values[i]: 'str'}
        if i == 0:
            log.info(f'Starting with {fn[0]}')
            main_df = pd.read_csv(os.path.join(wf, fn[0]), dtype=dtype)
            stats.append(main_df.shape)
            cols_to_remove(main_df.columns, [])  # this is called just to populate global variable cols_list TODO find a bettwer way to deal with this
        else:
            log.info(f'Adding {fn[i]}...')
            add_df = pd.read_csv(os.path.join(wf, f), dtype=dtype)
            add_df.drop(cols_to_remove(add_df.columns, keys_values), axis=1, inplace=True)
            stats.append(add_df.shape)
            main_df = main_df.merge(add_df, how='outer', left_on=keys_values[i - 1], right_on=keys_values[i])
    return main_df, stats


def analyze_inputs(fn, top_limit):
    """
    This columns should recognize what columns can be use for merging
    :param fn:
    :param top_limit:
    :return:
    """

    base_df = pd.read_csv(fn[0], nrows=top_limit)
    matching_columns = []
    for i, f in enumerate(fn):
        if i == 0:
            continue
        else:
            tmp_df = pd.read_csv(fn[0], nrows=top_limit)
            for col in tmp_df.columns:
                for index, base_col in enumerate(base_df.columns):
                    if all(tmp_df[col] == base_df[base_col]):
                        matching_columns.append(col)
                        cols_diff = list(base_df.columns.difference(tmp_df.columns)) + [col]
                        tmp_df_short = tmp_df.loc[:, cols_diff]
                        base_df = tmp_df_short.merge(base_df, how='inner', left_on=col, right_on=base_col)
                    if index == base_df.shape[1] and len(matching_columns) == 0:
                        log.info('No auto match!')
                        return None
    return matching_columns


def checks_stats(statist):
    for i, stat in enumerate(statist):
        # log.info(f'DF growth {stat}')
        if stat[0] > 0 and stat[0] != statist[i - 1][0]:
            log.info(f'Some rows are lost between dfs {i} and {i - 1}')


def write_stats(stat):
    for i, s in enumerate(stat):
        log.info(f'Table nr. {i + 1}: {s}')


def main(geography, keys_for_merge):
    start_time_geo = time.time()
    file_names = [f for f in os.listdir(working_folder) if f.endswith('.csv') and geography in f]
    if auto_keys:
        top_key = 100  # this is the number of rows used for key analysis, parametrize this if needed

        keys_for_merge = analyze_inputs(file_names, top_key)
        if not keys_for_merge:
            log.info('Please add keys!')
            sys.exit()
    else:
        log.info('Keys set manualy.')

    if len(keys_for_merge) != len(file_names):
        log.error('NUMBER OF KEYS MUST HAVE MATCHING NUMBER OF FILES!!!')
        sys.exit()

    result_df, statistic = read_and_merge(file_names, keys_for_merge, string_keys, working_folder)
    checks_stats(statistic)
    log.info('Writing output file!')

    result_df.to_csv(os.path.join(working_folder, geography + '_' + output_file_name), index=False)
    statistic.append(result_df.shape)
    write_stats(statistic)
    log.info(f'Geo {geography} done in {time.time() - start_time_geo} seconds.')


if __name__ == '__main__':

    if len(sys.argv) > 0:
        log.info('enter arguments')

    start_time = time.time()

    # string_keys, auto_keys, working_folder, output_file_name, keys, geographies = [a for i, a in enumerate(sys.argv) if i not in [0, 1]]

    string_keys = True
    auto_keys = False
    working_folder = r'D:\local_projects\blocks_level_data\data\00 raw data\NEW'  # d:\local_projects\ACS 2017 5yr local\maps data\SL150' #  r'D:\SHARE\C1990_SL150'
    output_file_name = 'final.csv'
    keys = ['Geo_FIPS'] * 21  #  , 'Geo_FIPS', 'Geo_FIPS']  # TODO parametrize all of this

    geographies = ["SL150"]  #  "SL060", "SL150" ["SL040", "SL050", "SL060", "SL860", "SL160", "SL310", "SL500", "SL795", "SL950", "SL960", "SL970", "SL610", "SL620", "SL140"]

    global cols_list
    cols_list = []

    for geo in geographies:
        main(geo, keys)

    log.info(f'Everything done in {time.time() - start_time} seconds.')
