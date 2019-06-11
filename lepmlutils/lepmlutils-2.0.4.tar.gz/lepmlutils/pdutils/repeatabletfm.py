from .transform import Transform
from .taggeddataframe import TaggedDataFrame


# RepeatableTfm ensures that re_operate is simply an alias
# for operate.
class RepeatableTfm(Transform):
    def operate(self, df: TaggedDataFrame) -> None:
        raise(NotImplementedError)
    
    # alias for operate
    def re_operate(self, new_df: TaggedDataFrame) -> None:
        self.operate(new_df)

