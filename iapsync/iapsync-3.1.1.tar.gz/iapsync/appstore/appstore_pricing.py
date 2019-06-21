import csv
import re
import os

_this_dir_ = os.path.dirname(os.path.realpath(__file__))

ALT_PRICE_TIERS = {
    'a': 510,
    'b': 530,
    '1': 550,
    '2': 560,
    '3': 570,
    '4': 580,
    '5': 590
}

def get_price_tier_table(path):
    if not path:
        path = '%s/pricing-matrix.csv' % _this_dir_
    rows = None
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = list(csv_reader)
    if not rows:
        raise TypeError('failed to get price info')

    head = rows[0]
    china_jj = -1
    for jj, col_name in enumerate(head):
        if jj == 0:
            continue
        if col_name.find('China') != -1 and col_name.find('CNY') != -1:
            if china_jj != -1:
                raise  TypeError('multi columns matched: China and CNY, not sure which to go!')
            china_jj = jj

    if china_jj == -1:
        raise  TypeError('no column matched: China and CNY!')

    price_rmb = list(map(lambda row: float(row[china_jj]), rows[2:]))

    # 获取普通等级
    def extract_num(s):
        m = re.search('^\s*等级\s*(\d+)\s*$', s)
        if not m:
            return None
        if m.lastindex != 1:
            raise TypeError('price tier 提取失败，格式错误')
        return int(m.group(1))

    price_tier_raw = []
    for ii, r in enumerate(rows[2:]):
        if not r or len(r) < 1:
            raise TypeError('价格表格式有问题，有空行')
        tier_raw = r[0]
        tier_value = extract_num(tier_raw)
        if tier_value is None:
            if ii == 0:
                tier_value = 0
            else:
                break
        price_tier_raw.append(tier_value)

    if not len(price_tier_raw):
        raise TypeError('price tier vector empty, should not happen')
    norm = []
    for ii, t in enumerate(price_tier_raw):
        if len(price_rmb) <= ii:
            raise TypeError('inconsistency')
        norm.append((t, price_rmb[ii]))

    # 获取备用等级
    def extract_alt_num(s):
        m = re.search('^\s*备用等级\s*(\w+)\s*$', s)
        if not m:
            return None
        if m.lastindex != 1:
            raise TypeError('price tier 提取失败，格式错误')
        return str(m.group(1))
    alts = []
    for ii, r in enumerate(rows[2:]):
        if not r or len(r) < 1:
            raise TypeError('价格表格式有问题，有空行')
        tier_raw = r[0]
        tier_name = extract_alt_num(tier_raw)
        if tier_name is None:
            continue
        tier_name = str(tier_name).lower()
        tier_value = ALT_PRICE_TIERS[tier_name]
        alts.append((tier_value, price_rmb[ii]))

    # 归并两种等级：以价格排序，如果价格相同，普通等级在前
    ret = []
    ii = 0
    jj = 0
    while ii < len(norm) or jj < len(alts):
        if ii >= len(norm):
            ret.append(alts[jj])
            jj += 1
            continue
        if jj >= len(alts):
            ret.append(norm[ii])
            ii += 1
            continue
        if norm[ii][1] <= alts[jj][1]:
            ret.append(norm[ii])
            ii += 1
        else:
            ret.append(alts[jj])
            jj += 1
    return ret


def calc_price_tier_ceil(price, accept_zero_price):
    tier_table = get_price_tier_table(None)
    for ii, tup in enumerate(tier_table):
        t, p = tup
        if p >= price and (t > 0 or accept_zero_price):
            return tuple(list(tup))
    return -1, -1


def calc_price_tier(price, accept_zero_price):
    return calc_price_tier_ceil(price, accept_zero_price)

if __name__ == '__main__':
    print(calc_price_tier(13))
