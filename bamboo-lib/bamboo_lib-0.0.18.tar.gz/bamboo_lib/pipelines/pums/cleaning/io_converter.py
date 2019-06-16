import os
import pandas as pd
import numpy as np
from numpy.random import choice

COL_RATE = "Total Conversion Rate"
SOC_00 = "socp00"
SOC_10 = "socp10"
SOC_12 = "socp12"

MALE_VAL = 1
FEMALE_VAL = 2

DEGREE = 'schl'
SEX = 'sex'
ESTIMATE = 'estimate'
YEAR = 'year'

data_dir = os.path.dirname(__file__)


def get_path(target):
    return os.path.join(data_dir, target)


def index(df, idx):
    return df.set_index(idx)


soc_direct_map = pd.read_csv(get_path('data/SOC_00_to_10_direct.csv'), converters={"socp00": str, "socp10": str})
soc_direct_map = soc_direct_map.to_dict(orient="records")
soc_direct_map = {x[SOC_00]: x[SOC_10] for x in soc_direct_map}

soc12_direct_map = pd.read_csv(get_path('data/SOC_10_to_12_direct.csv'), converters={"socp12": str, "socp10": str})
soc12_direct_map = soc12_direct_map.to_dict(orient="records")
soc12_direct_map = {x[SOC_10]: x[SOC_12] for x in soc12_direct_map}

soc_hs_m_map = pd.read_csv(get_path('data/SOC_00_to_10_HS_M.csv'), converters={"socp00": str, "socp10": str})
soc_hs_f_map = pd.read_csv(get_path('data/SOC_00_to_10_HS_F.csv'), converters={"socp00": str, "socp10": str})
soc_ba_m_map = pd.read_csv(get_path('data/SOC_00_to_10_BA_M.csv'), converters={"socp00": str, "socp10": str})
soc_ba_f_map = pd.read_csv(get_path('data/SOC_00_to_10_BA_F.csv'), converters={"socp00": str, "socp10": str})
soc_adv_m_map = pd.read_csv(get_path('data/SOC_00_to_10_ADV_M.csv'), converters={"socp00": str, "socp10": str})
soc_adv_f_map = pd.read_csv(get_path('data/SOC_00_to_10_ADV_F.csv'), converters={"socp00": str, "socp10": str})
to_index = [soc_hs_m_map, soc_hs_f_map, soc_ba_m_map, soc_ba_f_map, soc_adv_m_map, soc_adv_f_map]
soc_hs_m_map, soc_hs_f_map, soc_ba_m_map, soc_ba_f_map, soc_adv_m_map, soc_adv_f_map = map(lambda x: index(x, SOC_00), to_index)

soc12_hs_m_map = pd.read_csv(get_path('data/SOC_10_to_12_HS_M.csv'), converters={"socp12": str, "socp10": str})
soc12_hs_f_map = pd.read_csv(get_path('data/SOC_10_to_12_HS_F.csv'), converters={"socp12": str, "socp10": str})
soc12_ba_m_map = pd.read_csv(get_path('data/SOC_10_to_12_BA_M.csv'), converters={"socp12": str, "socp10": str})
soc12_ba_f_map = pd.read_csv(get_path('data/SOC_10_to_12_BA_F.csv'), converters={"socp12": str, "socp10": str})
soc12_adv_m_map = pd.read_csv(get_path('data/SOC_10_to_12_ADV_M.csv'), converters={"socp12": str, "socp10": str})
soc12_adv_f_map = pd.read_csv(get_path('data/SOC_10_to_12_ADV_F.csv'), converters={"socp12": str, "socp10": str})
to_index = [soc12_hs_m_map, soc12_hs_f_map, soc12_ba_m_map, soc12_ba_f_map, soc12_adv_m_map, soc12_adv_f_map]
soc12_hs_m_map, soc12_hs_f_map, soc12_ba_m_map, soc12_ba_f_map, soc12_adv_m_map, soc12_adv_f_map = map(lambda x: index(x, SOC_10), to_index)

xforms = {SOC_00: SOC_10, SOC_10: SOC_12}


def get_soc_mode(var_map):
    year, est = map(int, [var_map[YEAR], var_map[ESTIMATE]])
    if year >= 2012:
        return SOC_12
    elif year >= 2009:
        return SOC_10
    else:
        return SOC_00


def is_old_school(var_map):
    return (int(var_map[YEAR]) - int(var_map[ESTIMATE]) + 1) <= 2007


def randomizer(code, rule_map, start_col):
    if code not in rule_map.index:
        return code

    tmpdf = rule_map.ix[code]

    if tmpdf.empty:
        return code

    if isinstance(tmpdf, pd.Series):
        return tmpdf[xforms[start_col]]

    idx = choice(range(len(tmpdf)), p=tmpdf[COL_RATE].values)

    return tmpdf.iloc[idx][xforms[start_col]]


def _convert(df, start_col, is_oldschool_mode):
    ''' Use conversion tables to transform across classifications '''
    if is_oldschool_mode:
        raise NotImplementedError("Requires additional processing...")
    HS_VAL, BA_VAL, ADV_VAL = [20, 21, 22]

    if start_col not in df.columns:
        raise Exception(start_col, "Not in", df.columns)
        return df

    if start_col == SOC_10:
        direct_map = soc12_direct_map
        hs_m_map = soc12_hs_m_map
        hs_f_map = soc12_hs_f_map
        ba_m_map = soc12_ba_m_map
        ba_f_map = soc12_ba_f_map
        adv_m_map = soc12_adv_m_map
        adv_f_map = soc12_adv_f_map
    elif start_col == SOC_00:
        direct_map = soc_direct_map
        hs_m_map = soc_hs_m_map
        hs_f_map = soc_hs_f_map
        ba_m_map = soc_ba_m_map
        ba_f_map = soc_ba_f_map
        adv_m_map = soc_adv_m_map
        adv_f_map = soc_adv_f_map
    else:
        raise Exception("BAD START COLUMN")
    # -- First apply direct transformation then split into groups
    tmpcond = df[start_col].isin(direct_map.keys())
    df.loc[tmpcond, start_col] = df[tmpcond][start_col].map(direct_map)
    # df.loc[df[start_col].isin(direct_map.keys()), start_col] = df[start_col].map(direct_map)

    # print(direct_map)
    # print(df.head())
    # print(start_col)
    # print(df[start_col])
    # print(df[start_col].isin(direct_map.keys()))

    # print("HEL" , df.loc[df[start_col].isin(direct_map.keys())])
    # -- Intelligently split the dataframe into six parts based on gender & edu
    HS = (df[DEGREE].astype(float) <= HS_VAL)
    BA = (df[DEGREE].astype(float) == BA_VAL)
    ADV = (df[DEGREE].astype(float) >= ADV_VAL)
    MALE = (df[SEX].astype(int) == MALE_VAL)
    FEMALE = (df[SEX].astype(int) == FEMALE_VAL)

    HS_MALE = HS & MALE
    HS_FEMALE = HS & FEMALE
    BA_MALE = BA & MALE
    BA_FEMALE = BA & FEMALE
    ADV_MALE = ADV & MALE
    ADV_FEMALE = ADV & FEMALE
    IS_VALID_ESR = df.esr.notnull()
    EVERYTHING_ELSE = (~HS_MALE & ~HS_FEMALE & ~BA_MALE & ~BA_FEMALE & ~ADV_MALE & ~ADV_FEMALE) & IS_VALID_ESR

    if not df[EVERYTHING_ELSE][start_col].empty:
        print(df[EVERYTHING_ELSE])
        print(len(df[EVERYTHING_ELSE]))
        print(df[EVERYTHING_ELSE].schl.unique())
        raise Exception("*** ERROR! Unaccounted for people")

    rules = [(HS_MALE, hs_m_map), (HS_FEMALE, hs_f_map), (BA_MALE, ba_m_map), (BA_FEMALE, ba_f_map), (ADV_MALE, adv_m_map), (ADV_FEMALE, adv_f_map)]
    rule_num = 0
    for (rule, rule_map) in rules:
        print("Applying rule {},".format(rule_num))
        rule = rule & df[start_col].notnull()
        df.loc[rule & IS_VALID_ESR, xforms[start_col]] = df.loc[rule & IS_VALID_ESR, start_col].apply(lambda x: randomizer(x, rule_map, start_col))
        rule_num += 1
    return df


def occ_convert(df, var_map):
    '''
    PUMS occupational crosswalking
    There is data in PUMS 5-year files with both SOCP00 and SOCP10 formats.
    To deal with this, we must first crosswalk SOCP00 codes to SOCP10 codes,
    then we take all SOCP10 codes and walk them over to SOCP12 codes. So We end
    up with a SOCP12 column with the crosswalked codes.
    '''
    is_oldschool_mode = is_old_school(var_map)
    soc_mode = get_soc_mode(var_map)

    if SOC_00 in df.columns:
        print("Spotted socp00 in columns...first convert this.")

        df = _convert(df, SOC_00, is_oldschool_mode)
        df = _convert(df, SOC_10, is_oldschool_mode)
    elif SOC_10 in df.columns:
        print("Spotted socp10 in columns...first convert this.")
        print(df, "HERE!!!")
        df = _convert(df, SOC_10, is_oldschool_mode)
    else:
        print("*** single socp ****")
        print("RENAMING TO", soc_mode)
        print("SOC cols 1:", [x for x in df.columns if "soc" in x.lower()])
        df.rename(columns={"socp": soc_mode}, inplace=True)
        print("SOC cols 2:", [x for x in df.columns if "soc" in x.lower()])

        if soc_mode == SOC_00:
            print("****** PART I")
            df = _convert(df, SOC_00, is_oldschool_mode)
            print("****** PART II")
            df = _convert(df, SOC_10, is_oldschool_mode)
        elif soc_mode == SOC_10:
            df = _convert(df, SOC_10, is_oldschool_mode)
        elif soc_mode == SOC_12:
            pass  # Nothing to do!

    df.rename(columns={SOC_12: "socp"}, inplace=True)
    return df


if __name__ == '__main__':
    moi = pd.DataFrame({"x": [100, 44], "socp00": [np.nan, "472020"], "socp10": ["472XXX", np.nan], "sex": [2, 2], "degree": [10, 10]})
    print("Starting with")
    print(moi)
    print("####")
    res = occ_convert(moi, {YEAR: 2006, ESTIMATE: 3})
    print("CONVERTED TO")
    print(res)
