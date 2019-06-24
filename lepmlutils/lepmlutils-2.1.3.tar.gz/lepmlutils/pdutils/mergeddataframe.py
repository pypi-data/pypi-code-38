import pandas as pd
from typing import List, Tuple

# MergedDataFrame contains a DataFrame which is train and test
# data frames stacked vertically on top of each other. 
# MergedDataFrame keeps track of Which indices belong to which
# original frame, and each original frame can be reconstructed
# on if needed.
class MergedDataFrame(pd.DataFrame):

    # normal properties
    _metadata = ['train_i', 'test_i', 'train_targets']

    def __init__(self, *args, **kw):
        super(MergedDataFrame, self).__init__(*args, **kw)

    @property
    def _constructor(self):
        return MergedDataFrame

    def extract_train(self) -> pd.DataFrame:
        return self.filter(self.train_i, axis=0)

    def extract_test(self) -> pd.DataFrame:
        return self.filter(self.test_i, axis=0)

# merged_data takes train and test dataframes. It creates a new dataframe 
# with both stacked vertically and loads this into a MergedDataFrame, which
# is then returned. The MergedDataFrame tracks which row indices belong
# to which original frame. The target column is dropped from the merged
# DataFrame, and stored in a seprate Series on the MergedDataFrame.
def merged_data(traindf: pd.DataFrame, testdf: pd.DataFrame, target_cols: List[str]) -> MergedDataFrame:
        frame = merged_data_no_target(traindf, testdf)
        targets = traindf[target_cols]
        frame.drop(target_cols, axis=1, inplace=True)

        frame.train_targets = targets
        return frame


# merged_data_no_target does exactly the same thing as merged_data except
# it is assumed that neither dataframe has any targets.
def merged_data_no_target(traindf: pd.DataFrame, testdf: pd.DataFrame) -> MergedDataFrame:
        all_data = pd.concat((traindf, testdf), sort=False).reset_index(drop=True)

        frame = MergedDataFrame(all_data)
        frame.train_i = range(0, traindf.shape[0])
        frame.test_i = range(traindf.shape[0], all_data.shape[0])
        return frame