# coding=utf-8

from .CfMetric import CfMetric
#from Tools.ListTools import is_list, is_number_list
#from Tools.NumberTools import is_number
from .BaseMetric import BaseMetric
from .PSI import calc_psi_list
import numpy as np
import pandas as pd
import sys
sys.dont_write_bytecode = True

# 基于pandas的
class Metric:
    def __init__(self, data, label_name=None, score_name=None):
        assert isinstance(data, pd.DataFrame), "support DataFrame only (for now)"
        self.data = data
        self.label_name = label_name if label_name is not None else 'gb_flag'
        assert self._check_label_valid(), self.label_name + " should take value from {0, 1}..."
        self.score_name = score_name
        self.len, self.dim = data.shape

    def _check_label_valid(self):
        if self.data[self.label_name].max() == 1 and self.data[self.label_name].min() == 0:
            return True
        return False

    # 返回KS；可选：KS_list和坏账
    def get_ks(self, col_name=None, print_list=False, bad_rate=False):
        col_name = col_name if col_name is not None else self.score_name
        if len(set(self.data[col_name].values)) < 2:
            print("all scores are the same.")
            return -1
        else:
            base_metric = BaseMetric(self.data[col_name].values)
            return base_metric.get_ks(self.get_label_values(), print_list, bad_rate)

    def get_label_values(self):
        return self.data[self.label_name].values

    # KS对比，返回坏账可选
    def compare_ks(self, other_name, my_name=None, other_missing_value=None, my_missing_value=None, bad_rate=False):
        my_name = my_name if my_name is not None else self.score_name
        data_ = self.data.copy()
        if other_missing_value is not None:
            print('remove other')
            data_ =data_[data_[other_name] != other_missing_value]
        if my_missing_value is not None:
            print('remove my')
            data_ =data_[data_[my_name] != my_missing_value]
            
        my_ks = self.get_ks(col_name=my_name, bad_rate=bad_rate)
        other_ks = self.get_ks(col_name=other_name, bad_rate=bad_rate)
        if not bad_rate:
            return my_ks, other_ks
        else:
            return my_ks[0], other_ks

    # =================  分群

    # 逐月PSI（或者其他split上比较）
    def get_psi_per_split(self, split_name='month', col_name=None, bins=10, list_=False, ret_simple=True):
        col_name = col_name if col_name is not None else self.score_name
        months = sorted(set(self.data[split_name].values))
        re = ''
        for ind in range(1, len(months)):
            tmp1 = self.data[self.data[split_name] == months[ind - 1]]
            tmp2 = self.data[self.data[split_name] == months[ind]]
            cs = calc_psi_list(tmp1[col_name].values, tmp2[col_name].values, nbins=bins)
            if ret_simple:
                re += "|" + str(cs["psi_value"].sum())
            else:
                re+= "{}~{}|PSI|{}\n".format(months[ind - 1], months[ind], cs["psi_value"].sum())
            if list_:
                print(cs["psi_value"].values)
        return re

    # 逐月PSI（或者其他split上比较）
    def get_psi_given_splits(self, splits, split_name='month', col_name=None, bins=10):
        col_name = col_name if col_name is not None else self.score_name
        act_splits = sorted(set(self.data[split_name].values))
        ret = {}
        for spl in splits:      # 计算每个给定split上的spi
            if spl in act_splits:
                # 实际数据中存在 spl的数据
                idx = act_splits.index(spl)
                if idx > 0:
                    # 存在上一个月的数据（不一定连续），计算spi
                    tmp1 = self.data[self.data[split_name] == act_splits[idx - 1]]
                    tmp2 = self.data[self.data[split_name] == act_splits[idx]]
                    #分桶数取最短板
                    bins = min(tmp1.shape[0],tmp2.shape[0],bins)
                    cs = calc_psi_list(tmp1[col_name].values, tmp2[col_name].values, nbins=bins)
                    ret[spl] = cs["psi_value"].sum()
        return ret

    # 逐月KS（或者其他split上比较）
    def get_ks_per_split(self, split_name='month', col_name=None, bad_rate=True):
        col_name = col_name if col_name is not None else self.score_name
        months = sorted(set(self.data[split_name].values))
        results = {}
        for month in months:
            tmp1 = self.data[self.data[split_name] == month]
            base_metric = BaseMetric(tmp1[col_name].values)
            res = base_metric.get_ks(tmp1[self.label_name].values, bad_rate=bad_rate)
            results[month] = res
            print("{} , KS={}".format(month, res))
        return results

    # 交叉分析
    def get_mix(self, other_data,  other_name, bins=10, on_keys=['pin', 'createtime'], my_name=None):
        assert isinstance(other_data, pd.DataFrame), "support DataFrame only (for now)"
        my_name = my_name if my_name is not None else self.score_name
        x = self.data.reset_index()
        ascore_data = other_data.reset_index()
        ascore_data = ascore_data.drop(self.label_name, axis=1)
        merged = pd.merge(x, ascore_data, on=on_keys)
        pred_score = merged[[my_name, self.label_name] + on_keys].sort_values(by=my_name)
        ascore_data = merged[[other_name] + on_keys].sort_values(by=other_name)
        bin_size = int(len(merged) / bins)
        results_bad = np.zeros((bins, bins))
        results_tot = np.zeros((bins, bins))
        result_badrate = np.zeros((bins, bins))
        for i in range(bins):
            print("processing {}th bin".format(i))
            ascore = ascore_data.iloc[i * bin_size: min((i + 1) * bin_size, len(merged))]
            for j in range(bins):
                pred = pred_score.iloc[j * bin_size: min((j + 1) * bin_size, len(merged))]
                merged_small = pd.merge(ascore, pred, on=on_keys)
                results_bad[i][j] = len(merged_small[merged_small[self.label_name] == 0])
                results_tot[i][j] = len(merged_small)
                result_badrate[i][j] = results_bad[i][j] * 1.0 / results_tot[i][j] if results_tot[i][j] > 0 else -1
        return results_tot, results_bad, result_badrate

    # 字段覆盖率
    def get_split_cover(self, col_lists, missing_value=-9999.8):
        # assert is_list(col_lists), "give me list of cols..."
        data_ = self.data.fillna(missing_value)
        for col in col_lists:
            tot_non = len(data_[data_[col] != missing_value])
            print("{}, tot/non={}\t{}\t{}".format(col, self.len, tot_non, tot_non * 1.0 / self.len))

    # 换入换出分析
    def swap_out(self, data, score_threshold, score_name=None, stratigy_name='gb_flag'):
        # assert is_number(score_threshold), "threshold should be a numeric"
        score_name = score_name if score_name is not None else self.score_name
        data[score_name+"_bin"] = data[score_name].apply(lambda x: 1 if x >= score_threshold else 0)
        print("stratigy VS score")
        print(data.groupby([stratigy_name, score_name]).size())

    # lift值和分段坏账
    def get_lift(self, score_name=None, bins=10):
        score_name = score_name if score_name is not None else self.score_name
        y = self.get_label_values()
        score_pred = self.data[score_name].values
        tot_bad = np.sum(y == 0)
        kv = list(zip(score_pred, y))
        kv_sorted = sorted(kv, key=lambda x: x[0])
        label_sorted = list(zip(*kv_sorted))[1]
        if len(label_sorted) % bins != 0:
            gewei = len(label_sorted) % 10
            label_sorted = label_sorted[: -1 * int(gewei)]
        bin_size = float(len(label_sorted) / bins)
        label_sorted = np.reshape(label_sorted, (bins, -1))
        num_goods = np.sum(label_sorted, axis=1)
        num_bads = bin_size - num_goods
        lift = num_bads / tot_bad
        bad_rad = 1 - num_goods / bin_size
        return bad_rad, lift

    # 分数段划分
    def split(self, bin=10, col_name=None, index_=None):
        # assert is_number(bin) or is_number_list(bin), "bin should be numeric or a numeric list"
        if index_ is None:
            index_ = "pin"
        self.data = self.data.set_index(index_)
        col_name = col_name if col_name is not None else self.score_name
        a = pd.qcut(self.data[col_name], bin)
        self.data[col_name+"_bin"] = a
        self.data = self.data.reset_index()
        print(a.value_counts())

    # 分段坏账 lift 第二版
    def print_lift_v2(self, bin=10, col_name=None, index_=None):
        col_name = col_name if col_name is not None else self.score_name
        print("split data..")
        self.split(bin, col_name, index_)
        print(self.data.groupby([col_name+"_bin", self.label_name]).size())

    # 按照有标签的激活用户来分段，然后应用在申请用户上
    # 保证apply_data中的交叉字段和data一致
    def get_mix_v2(self, other_col, apply_data, bin=10, col_name=None, index_=None):
        col_name = col_name if col_name is not None else self.score_name
        assert isinstance(apply_data, pd.DataFrame), "support DataFrame only (for now)"
        # 激活用户上的分段
        print("split data..")
        self.split(bin, col_name, index_)
        self.split(bin, other_col, index_)
        result = self.data.groupby([col_name+"_bin", other_col + "_bin", self.label_name]).size()
        # 申请数据上的分段
        splits_info = list(set(self.data[col_name+"_bin"].values))
        splits_info_other = list(set(self.data[other_col+"_bin"].values))
        apply_data[other_col+"_bin"] = apply_data[other_col].apply(lambda x: self._check_range(x, splits_info_other))
        apply_data[col_name+"_bin"] = apply_data[col_name].apply(lambda x: self._check_range(x, splits_info))
        result_apply = apply_data.groupby([col_name+"_bin", other_col + "_bin"]).size()
        print(result)
        print(result_apply)
        return result, result_apply

    def _check_range(self, score, list_info):
        for info in list_info:
            if float(score) in info:
                return info
        return -1

    def _count_bad(self, data):
        return len(data[data[self.label_name] == 0])

    def _count_good(self, data):
        return len(data[data[self.label_name] == 1])

    def _bad_rate(self, data):
        return self._count_bad(data) * 1.0 / len(data)

    # 分数分布，可输入分数的处理函数，可以用来求beta sum
    def get_distribution(self, col_name=None, max_=1.0, min_=0.0, step_size=0.01, func=None):
        col_name = col_name if col_name is not None else self.score_name
        arr = np.arange(min_, max_, step=step_size)
        arr = arr.tolist()
        arr.append(max_)
        result = []
        data = self.data.copy()
        if func is not None and hasattr(func, '__call__'):
            data[col_name] = data[col_name].apply(func)
        for ind in range(1, len(arr)):
            col_data = data[col_name].between(arr[ind - 1], arr[ind]).values.sum()
            result.append(col_data)
        return result, arr

if __name__ == "__main__":
    pass    
