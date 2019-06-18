from .help import *
from .partition import Partition
import pandas as pd
from scipy import stats
from scipy.special import boxcox1p
from sklearn import neighbors
from typing import List


class Imputer(Partition):
    def __init__(
        self, 
        df: pd.DataFrame, 
        true_nas: List[str],
        int_ord_cats: List[str],
        int_unord_cats: List[str],
        str_ord_cats: List[str],
        str_unord_cats: List[str],
        manual_enc: Dict[str, Dict[str, int]]={}
    ):  
        super().__init__(
            df, 
            int_ord_cats, 
            int_unord_cats, 
            str_ord_cats,
            str_unord_cats,
            manual_enc,
        )
        self.true_nas = true_nas

    def knn_impute(self):
        self.encode_categoricals_and_flat_impute()
        self.cls_impute()

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