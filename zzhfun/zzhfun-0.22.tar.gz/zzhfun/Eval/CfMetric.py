# coding:utf8
import numpy as np
import pandas as pd
import warnings
from multiprocessing import Pool
from copy import deepcopy

from pandas import Series, DataFrame, read_csv, read_table
import sys
sys.dont_write_bytecode = True

def stable_cumsum(arr, axis=None, rtol=1e-05, atol=1e-08):
    """Use high precision for cumsum and check that final value matches sum
    Parameters
    ----------
    arr : array-like
        To be cumulatively summed as flat
    axis : int, optional
        Axis along which the cumulative sum is computed.
        The default (None) is to compute the cumsum over the flattened array.
    rtol : float
        Relative tolerance, see ``np.allclose``
    atol : float
        Absolute tolerance, see ``np.allclose``
    """
    out = np.cumsum(arr, axis=axis, dtype=np.float64)
    expected = np.sum(arr, axis=axis, dtype=np.float64)
    if not np.all(np.isclose(out.take(-1, axis=axis), expected, rtol=rtol,
                             atol=atol, equal_nan=True)):
        warnings.warn('cumsum was found to be unstable: '
                      'its last element does not correspond to sum',
                      RuntimeWarning)
    return out


# class psi:
#     def __init__(self, d_org, d_obj, seg=10):
#         self.breakpts = np.unique(np.percentile(d_org, [i * (100 / seg) for i in range(seg + 1)]))
#         self.org_cnt = np.histogram(d_org, self.breakpts)[0]
#         self.org_pct = 1.0 * self.org_cnt / len(d_org)
#         self.obj_cnt = np.histogram(d_obj, self.breakpts)[0]
#         self.obj_pct = 1.0 * self.obj_cnt / len(d_obj)
#         self.psi_seg = (self.org_pct - self.obj_pct) * np.log(self.org_pct / self.obj_pct)
# #        if (self.obj_pct == 0).any():
# #            print(self.org_pct.tolist())
# #            print(self.obj_pct.tolist())
# #            print(self.obj_cnt.tolist())
# #            print(self.psi_seg.tolist())
# #            raise Exception('divided by zero.')
#
#     @property
#     def psi(self):
#         return np.sum(self.psi_seg)
#
#     @property
#     def psi_list(self):
#         order = ['ScLf', 'ScRt', 'OrgCnt', 'ObjCnt', 'OrgPct', 'ObjPct', 'PSI']
#         return DataFrame({'ScLf': self.breakpts[1:],
#                           'ScRt': self.breakpts[:-1],
#                           'OrgCnt': self.org_cnt,
#                           'ObjCnt': self.obj_cnt,
#                           'OrgPct': self.org_pct,
#                           'ObjPct': self.obj_pct,
#                           'PSI': self.psi_seg})[order]


class CfMetric:
    def __init__(self, y_true, y_score, seg=10.0, pos_label=1):
        self.uniq_sort(y_true, y_score)
        self.seg = seg
        self.cal_dtl_inf()  # only for ks, not for ks_list
        self.cal_seg_inf()

    def uniq_sort(self, y_true, y_score):
        desc_score_indices = np.argsort(y_score, kind="mergesort")[::-1]
        self.y_score = y_score[desc_score_indices]
        self.y_true = y_true[desc_score_indices]

        # unique
        distinct_value_indices = np.where(np.diff(self.y_score))[0]
        self.threshold_idxs = np.r_[distinct_value_indices, y_true.size - 1]

        self.dtl_pos = stable_cumsum(self.y_true)[self.threshold_idxs]
        dtl_tot = 1 + self.threshold_idxs
        self.dtl_tot = 1.0 * dtl_tot / dtl_tot[-1]

    def cal_dtl_inf(self):
        '''计算细粒度的信息
        '''
        self.tps = self.dtl_pos
        self.tpr = 1.0 * self.tps / self.tps[-1]
        self.fps = 1 + self.threshold_idxs - self.tps
        self.fpr = 1.0 * self.fps / self.fps[-1]

        self.y_org = self.y_score[self.threshold_idxs]

    def cal_seg_inf(self):
        '''计算分段的汇总信息
        return
        ----------------
        分组阈值列表

        '''
        seg_tot = np.floor(self.dtl_tot * self.seg * 0.999)
        seg_value_indices = np.where(np.diff(seg_tot))[0]

        if len(seg_value_indices) > 0 and self.dtl_tot[seg_value_indices[-1]] <= (((self.seg - 1) * 1.0) / self.seg):
            seg_value_indices = np.r_[seg_value_indices, seg_tot.size - 1]
        else:
            seg_value_indices[-1] = seg_tot.size - 1

        self.seg_tps = self.dtl_pos[seg_value_indices]
        self.seg_tpr = 1.0 * self.seg_tps / self.seg_tps[-1]
        self.seg_fps = 1 + self.threshold_idxs[seg_value_indices] - self.seg_tps
        self.seg_fpr = 1.0 * self.seg_fps / self.seg_fps[-1]
        self.y_seg_value = self.y_score[self.threshold_idxs[seg_value_indices]]

        good_cunsum, good_sum = self.reversed_cunsum(self.seg_tps)
        bad_cunsum, bad_sum = self.reversed_cunsum(self.seg_fps)
        tot_sum = good_sum + bad_sum
        good_ratio = good_cunsum * 1.0 / good_cunsum[-1]
        bad_ratio = bad_cunsum * 1.0 / bad_cunsum[-1]
        score_left = self.y_seg_value[::-1]
        score_right = np.r_[self.y_score[0], self.y_seg_value[:-1]][::-1]

        self.seg_inf = DataFrame({'Id': range(len(score_right)),
                                  'ScLf': score_left,
                                  'ScRt': score_right,
                                  'GCsCnt': good_cunsum,
                                  'BCsCnt': bad_cunsum,
                                  'GCnt': good_sum,
                                  'BCnt': bad_sum})

    @staticmethod
    def reversed_cunsum(rev_arr):
        cunsum_ = rev_arr[-1] - rev_arr
        cunsum_ = np.r_[rev_arr[-1], cunsum_[:-1]]
        cunsum_ = cunsum_[::-1]
        num_ = np.r_[cunsum_[0], np.diff(cunsum_)]
        return cunsum_, num_

    @property
    def ks_list(self):
        ks_det = deepcopy(self.seg_inf)
        ks_det['GPct'] = 1.0 * ks_det.GCsCnt / ks_det.GCsCnt.ravel()[-1]
        ks_det['BPct'] = 1.0 * ks_det.BCsCnt / ks_det.BCsCnt.ravel()[-1]
        ks_det['KS'] = ks_det.BPct - ks_det.GPct
        order = ['Id', 'ScLf', 'ScRt', 'GCsCnt', 'BCsCnt', 'GCnt', 'BCnt', 'GPct', 'BPct', 'KS']
        return ks_det[order]

    @property
    def iv_list(self):
        iv_det = deepcopy(self.seg_inf)
        iv_det['GPct'] = 1.0 * iv_det.GCnt / iv_det.GCsCnt.ravel()[-1]
        iv_det['BPct'] = 1.0 * iv_det.BCnt / iv_det.BCsCnt.ravel()[-1]

        iv_det['IV'] = np.log(iv_det.GPct / iv_det.BPct) * (iv_det.GPct - iv_det.BPct)

        order = ['Id', 'ScLf', 'ScRt', 'GCnt', 'BCnt', 'GPct', 'BPct', 'IV']
        self.iv = np.sum(iv_det.IV)
        return iv_det[order]

    @property
    def iv(self):
        self.iv_list
        return self.iv

    @property
    def ks(self):
        return round(np.max(abs(self.tpr - self.fpr)) * 100, 2)

    @property
    def auc(self):
        return np.trapz(self.tpr, self.fpr)


def bad_ratio_ts(df, seg):
    df_s_c = df.score.quantile([1.0 * i / seg for i in range(1, seg)])
    max_v = max(df.score)
    df_s_c1 = [0.0, ] + list(df_s_c) + [max_v]
    df['flag'] = pd.cut(df.score, df_s_c1, labels=range(seg))
    df_res1 = df.groupby(['dt', 'flag']).gb_flag.mean()
    df_res2 = df.groupby(['dt', 'flag']).gb_flag.sum()
    df_res3 = df.groupby(['dt', 'flag']).gb_flag.count()
    return df_res1, df_res2, df_res3


def group_auc(dtf):
    dtf.columns = ['mon', 'y_true', 'y_pred']
    df_dt = set(dtf.mon.values)
    df_dt = sorted(df_dt)
    for dt in df_dt:
        try:
            df_tmp = dtf.ix[dtf.mon == dt,]
            # row = roc_auc_score(df_tmp.y_true.values, df_tmp.y_pred.values)
            cf = CfMetric(df_tmp.y_true.values, df_tmp.y_pred.values)
            # print cf.auc, cf.ks
            print('{0}\t{1}\t{2}'.format(dt, cf.auc, cf.ks))
        except:
            pass

#
# def var_psi_cal(var):
#     f1 = data1['{0}'.format(var)].values.ravel()
#     f2 = data2['{0}'.format(var)].values.ravel()
#     psi_s = psi(f1, f2)
#     print('{0},{1}'.format(var, psi_s.psi))
#     sys.stdout.flush()
#     return var, psi_s.psi_value


# def mul_psi_cal(file1, file2, igx):
#     global data1
#     global data2
#     print('*' * 50)
#     print('{0} VS {1}'.format(file1, file2))
#     data1 = read_table(file1, sep='\t')
#     data2 = read_table(file2, sep='\t')
#     pool = Pool(processes=20)
#     results = pool.map(var_psi_cal, field_list)
#     pool.close()
#     pool.join()
#     results1 = [i[0] for i in results]
#     results2 = [i[1] for i in results]
#     results = DataFrame(results2, index=results1)
#     results.columns = [str(igx)]
#     return results


# def test_psi():
#     df_org = read_table('score_1809', sep=',')
#     df_obj = read_table('score_1810', sep=',')
#     cf = psi(df_org.score.values, df_obj.score.values)
#     print(cf.psi)
#     print(cf.psi_list)


def test_iv():
    df = read_table('../data/tantic.csv', sep=',')
    df = df.fillna(-99)
    cf = CfMetric(df.label.values, df.Age.values, 3)
    print(cf.iv)
    print(cf.iv_list)


def test_ks():
    df = read_table('../data/tantic.csv', sep=',')
    df = df.fillna(-99)
    cf = CfMetric(df.label.values, df.Age.values, 3)
    print(cf.ks)
    print(cf.auc)
    print(cf.ks_list)


if __name__ == '__main__':
    # test_psi()
    test_iv()
    test_ks()
