
from collections import Counter
import pandas as pd

def counter(counter_list):
    counter_dict = dict(Counter(counter_list))
    return counter_dict

def counter_df(counter_list):
    counter_dict = counter(counter_list)
    counter_df = pd.Series(counter_dict).to_frame('Count').reset_index()
    counter_df = counter_df.sort_values(['Count'], ascending=[False])
    return counter_df


if __name__ == '__main__':
    counter_list = [1,1,1,1,2,2,2,3,3,3]
    counter_dict = counter(counter_list)
    print(counter_dict)
