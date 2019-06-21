from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import argparse

import numpy as np
import pandas as pd

import sys
sys.dont_write_bytecode = True

def cut_equi_dist():
    pass


def cut_equi_freq():
    pass


def cut_by_dtree():
    pass


# Binning algorithm should be improved further.
def calc_psi_list(data1, data2, nbins):
    # load data as Series
    data1 = pd.Series(data1)
    data2 = pd.Series(data2)
    # sort data1
    data1 = data1.sort_values()
    data1.index = range(data1.shape[0])
    # calculate bin values
    nsamp1 = float(data1.shape[0])
    nsamp2 = float(data2.shape[0])
    frac = nsamp1 / nbins
    bins = []
    for i in range(1, nbins):
        idx = int(round(i * frac))
        bins.append(data1[idx])
    bins.append(float("inf"))
    bins.append(float("-inf"))
    bins = sorted(list(set(bins)))
    # calculate psi values
    psi_list = []
    for i in range(len(bins) - 1):
        range_str = "(%f, %f]" % (bins[i], bins[i + 1])
        cnt1 = sum((data1 > bins[i]) & (data1 <= bins[i + 1]))
        cnt2 = sum((data2 > bins[i]) & (data2 <= bins[i + 1]))
        pct1 = cnt1 / nsamp1
        pct2 = cnt2 / nsamp2
        psi_val = (pct1 - pct2) * np.log((pct1 + 1e-8) / (pct2  + 1e-8))
        psi_list.append({"range": range_str,
                         "cnt1": cnt1, "cnt2": cnt2,
                         "pct1": pct1, "pct2": pct2,
                         "psi_value": psi_val})
    return pd.DataFrame(psi_list)


# correlation analysis
def correlate(y_label, y_pred1, y_pred2, cut=10):
    res = pd.DataFrame({'label': y_label, 'pred1': y_pred1, 'pred2': y_pred2})
    res['pred_grid1'] = pd.qcut(res.pred1, cut)
    res['pred_grid2'] = pd.qcut(res.pred2, cut)
    print(res.groupby(['pred_grid1', 'pred_grid2'])['label'].agg(['count', 'sum', 'mean']))


def read_res(src):
    root, ext = os.path.splitext(src)
    if ext == ".txt":
        pddf = pd.read_csv(src, sep='\t', names=["label", "score"])
    elif ext == ".csv":
        pddf = pd.read_csv(src)
    else:
        raise Exception("Unsupported extension")
    return pddf


if __name__ == "__main__":
    print("Edited on 12-10-2018")
    # some instances for applying analyze
    parser = argparse.ArgumentParser(description="Analysis tool")
    parser.add_argument("--mode", type=str, choices=["univar", "score", "psi"])
    parser.add_argument("--src1", type=str,
                        help="load data file from path")
    parser.add_argument("--src2", type=str,
                        help="load data file from path")
    parser.add_argument("--feat", type=str, nargs='*')

    args = parser.parse_args()

    if args.mode == "psi":
        df1 = read_res(args.src1)
        df2 = read_res(args.src2)
        psi_list = calc_psi_list(df1['score'], df2['score'], 10)
        print(psi_list["psi_value"].sum())

    # data = pd.read_table("data_ca.txt", sep="\t")
    # y = data['gb_tag']
    # score1 = data['a_score']
    # score2 = data['score']
    # correlate(y, score1, score2)