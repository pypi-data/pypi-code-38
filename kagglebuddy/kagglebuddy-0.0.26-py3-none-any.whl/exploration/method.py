import numpy as np
from ..preprocessing.new_features import create_groupby_features


def compute_iv(data, feature, target):
    """Compute information gain

        < 0.02    : useless for prediction
        0.02 - 1  : weak predictor
        0.1 - 0.3 : medium predictor
        0.3 - 0.5 : strong predictor
        > 0.5     : suspicious or too good to be true

        https://medium.com/@sundarstyles89/weight-of-evidence-and-information-value-using-python-6f05072e83eb

    Parameters
    ----------
    data: pandas dataframe
    feature: str
    target: str

    Returns
    -------
    [woe, iv]

    Examples
    --------

    """
    # Category
    group = create_groupby_features(data, feature, {target: ["count", "sum"]}, verbose=False)
    group.columns = [group.columns[0], "count_all", "count_1"]
    group["count_0"] = group["count_all"] - group["count_1"]
    group["count_1_ratio"] = group["count_1"] / group["count_1"].sum()
    group["count_0_ratio"] = group["count_0"] / group["count_0"].sum()
    group.loc[np.isinf(group["count_1_ratio"]), "count_1_ratio"] = 0
    group.loc[np.isinf(group["count_0_ratio"]), "count_0_ratio"] = 0
    group["woe"] = group.apply(lambda row: np.log(row["count_1_ratio"] / row["count_0_ratio"]), axis=1)
    if group["count_1_ratio"].max() == 1:
        pass
    else:
        group.loc[np.isinf(group["woe"]), "woe"] = 0
    group["iv"] = group.apply(lambda row: (row["count_1_ratio"] - row["count_0_ratio"]) * row["woe"], axis=1)
    group["iv"] = group["iv"].sum()
    return group[feature + ["woe"]], group["iv"].values[0]
