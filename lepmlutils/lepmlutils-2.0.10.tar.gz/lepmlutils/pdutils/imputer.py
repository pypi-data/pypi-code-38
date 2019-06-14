from .help import *
import pandas as pd
from scipy import stats
from scipy.special import boxcox1p
from sklearn import neighbors
from typing import List


class Imputer():
    def __init__(
        self, 
        df: pd.DataFrame, 
        true_nas: List[str],
        int_ord_cats: List[str],
        int_unord_cats: List[str],
        str_ord_cats: List[str],
        str_unord_cats: List[str],
        manual_enc: Dict[str, Dict[str, int]]
    ): 
        str_dups = set(str_ord_cats) & set(str_unord_cats)
        assert len(str_dups) == 0, f"string columns {str_dups} are duplicated"

        int_dups = set(int_ord_cats) & set(int_unord_cats)
        assert len(int_dups) == 0, f"integer columns {int_dups} are duplicated"

        all_str_cats = str_ord_cats + str_unord_cats

        unshared = set(all_str_cats) ^ set(str_cols(df))
        assert  len(unshared) == 0, f"all categoricals did not match all string columns from dataframe, these columns were not shared {unshared}"

        unshared = set(str_ord_cats) ^ set(manual_enc.keys())
        assert len(unshared) == 0, f"expected manual encoding to contain an entry for each ordered string categorical. The following columns were not shared: {unshared}"

        all_int_cats = int_ord_cats + int_unord_cats

        introduced = set(all_int_cats) - set(int_cols(df))
        assert len(introduced) == 0, f"expected integer catgoricals to all be listed in dataframe, the following columns were not: {introduced}"

        self.df = df
        self.true_nas = true_nas
        self.int_ord_cats = int_ord_cats
        self.int_unord_cats = int_unord_cats
        self.str_ord_cats = str_ord_cats
        self.str_unord_cats = str_unord_cats
        self.manual_enc = manual_enc
        self.ord_cats = int_ord_cats + str_ord_cats
        self.unord_cats = int_unord_cats + str_unord_cats
        self.all_cats = self.ord_cats + self.unord_cats
        self.conts = all_cols_except(self.df, self.all_cats)
        self.auto_enc_cats = self.unord_cats + self.int_ord_cats

    def knn_impute(self):
        self.encode_categoricals_and_flat_impute()
        self.cls_impute()
        self.finalize()

    # all string columns are encoded to integer values and
    # all bad values are replaced with an outlier integer
    # value.
    def encode_categoricals_and_flat_impute(self):
        set_true_na(self.df, self.true_nas)
        encode_to_int(self.df, self.manual_enc)
        convert_to_cat_codes(self.df, self.auto_enc_cats)
        fill_ordinal_na(self.df, self.conts)

    def cls_impute(self):
        cls_impute(
            neighbors.KNeighborsClassifier(),
            self.df,
            self.all_cats,
        )

        reg_impute(
            neighbors.KNeighborsRegressor(),
            self.df,
            self.conts,
        )

    def finalize(self):
        self.one_hot_encode()
        self.skew()

    def one_hot_encode(self):
        for col in self.unord_cats:
            self.df[col] = self.df[col].astype("category")
            
        dummify(self.df, self.unord_cats)

    def skew(self):
        for col in self.conts:
            if np.abs(stats.skew(self.df[col])) > 0.75:
                self.df[col] = boxcox1p(
                    self.df[col], 
                    stats.boxcox_normmax(self.df[col] + 1)
                )