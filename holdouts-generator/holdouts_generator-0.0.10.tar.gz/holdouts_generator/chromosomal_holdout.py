from typing import Callable, List, Tuple
import pandas as pd
import numpy as np

def chromosomal_holdout(chromosomes:List[int])->Callable:
    """Return a function to create an holdout with given chromosomes."""
    formatted_chromosomes = ["chr{c}".format(c=c) for c in chromosomes]
    def holdout(dataset:List[pd.DataFrame])->List[pd.DataFrame]:
        """
            dataset:List[pd.DataFrame], the dataset to split. The index is expected to be of the format chr19.70741698
        """
        test_mask = np.array([i.split(".")[0] in formatted_chromosomes for i in dataset[0].index])
        train_mask = np.bitwise_not(test_mask)
        return [
            d[mask] for i, d in enumerate(dataset) for mask in [train_mask, test_mask]
        ]

    return holdout, "chromosomal_holdout_{chromosomes}".format(
        chromosomes="+".join(formatted_chromosomes)
    )

def chromosomal_holdouts(chromosomes_lists:List[Tuple[List[int], List[Tuple]]])->List[Tuple[Callable, str, List]]:
    """Return a Generator of functions to create an holdouts with given chromosomes.
        chromosomes_lists:List[List], list of arbitrary depth of chromosomal holdouts.
    """
    for chromosomes, sub_lists in chromosomes_lists:
        if sub_lists is None:
            yield (*chromosomal_holdout(chromosomes), None)
        else:
            yield (*chromosomal_holdout(chromosomes), chromosomal_holdouts(sub_lists))