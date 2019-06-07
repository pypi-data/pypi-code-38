import pandas as pd
from pandas._libs.parsers import pandas_dtype
import logging


def input_df_contract(contract_params: dict, df_param=None):
    """
    This decorator allow to check properties of a df transformation
    Args:
        df_param: name of the param of the function that is the input df
        contract_params: dict defining the contract of the function in the following format:
                            contract_dict = {
                                "col_additions": {
                                    "col_a": "int",
                                    "col_b": "float"
                                },
                                "col_deletions": {
                                    "col_c",
                                    "col_d"
                                },
                                "col_editions": {
                                    "col_e",
                                    "col_f"
                                },
                                "allow_index_edition": False,
                                "allow_drop_record": True
                            }
                        which means that the function must create "col_a", "col_b", delete "col_c", "col_d", must
                        not modify any column data except "col_e", "col_f", and must not edit the index

            here is the list of keys allowed in this dict:
            col_additions: dict where keys are column names and values are dtypes (string)
            col_deletions: set of str representing the deleted columns
            col_editions: set of str representing the modified columns
            allow_index_edition: bool indicating if the function modify the index
            allow_add_drop_record (bool): indicate if the function can drop some records (ex. when dropna is used)

    usage:
        when you have a function that takes a df as input:
        ```
        def super_func(df_input):
            ...
        ```
        just add the annotation to automatically check properties
        ```
        @input_df_contract(df_param="df_input", contract_dict={"col_editions": {"col_e","col_f"}})
        def super_func(df_input):
            ...
        ```

    """
    contract = DataframeContract(**contract_params)

    def func_decorator(func):
        # we need to get the name of the param and it position
        # if df_param is not set the first positional argument will be assumed
        if df_param is not None:
            # as df_param can be passed as args or kwargs, we need to know it's position in *args
            df_param_name = df_param
            df_param_idx = func.__code__.co_varnames.index(df_param)
            # func.__code__.co_varnames : tuple of func's params name ordered
            # .index(df_param) location of df_param in this tuple
        else:
            df_param_name = func.__code__.co_varnames[0]
            df_param_idx = 0

        def func_wrapper(*args, **kwargs):
            # check if df_param is passed as *args or **kwargs
            if df_param_name in kwargs.keys():
                df_in = kwargs[df_param_name]  # passed as kwargs
            else:
                df_in = args[df_param_idx]  # passed as args
            # call the function
            df_out = func(*args, **kwargs)
            # check the contract
            contract.check_contract(df_in, df_out)
            return df_out

        return func_wrapper

    return func_decorator


class DataframeContract:

    def __init__(self, col_additions: dict = None, col_deletions: {str} = None, col_editions: {str} = None,
                 allow_index_edition: bool = False, allow_add_drop_record: bool = True):
        """
        Define a DataFrame transform contract.
        Args:
            col_additions: dict where keys are column names and values are dtypes (string)
            col_deletions: set of str representing the deleted columns
            col_editions: set of str representing the modified columns
            allow_index_edition: bool indicating if the function modify the index
            allow_add_drop_record (bool): indicate if the function can drop some records (ex. when dropna is used)
        """
        self.col_additions = col_additions if (col_additions is not None) else dict()
        for (key, value) in self.col_additions.items():
            self.col_additions[key] = pandas_dtype(value)
        self.col_deletions = col_deletions if (col_deletions is not None) else set()
        self.col_editions = col_editions if (col_editions is not None) else set()
        self.allow_index_edition = allow_index_edition
        self.allow_add_drop_record = allow_add_drop_record

    def check_contract(self, df_in: pd.DataFrame, df_out: pd.DataFrame):
        """
        Check if the two dataFrame respect the contract
        Args:
            df_in: input of the Transform
            df_out: result of the transformation

        Returns: None

        Raises: an error if one of the conditions of the contract if violated

        """
        logger = logging.getLogger(__name__)
        dtypes = df_out.dtypes
        # check additions
        success = self.check_values(expected=set(self.col_additions.keys()),
                                    real=(set(df_out.columns) - set(df_in.columns)),
                                    message="columns addition")
        # check additions dtypes
        success = success and self.check_values(real=list(dtypes.loc[self.col_additions.keys()]),
                                                expected=list(self.col_additions.values()),
                                                message="column addition dtypes")
        # check deletions
        success = success and self.check_values(real=(set(df_in.columns) - set(df_out.columns)),
                                                expected=self.col_deletions,
                                                message="columns deletion")
        # check index edition
        if not self.allow_index_edition:
            try:
                pd.testing.assert_index_equal(df_in.index, df_out.index)
            except AssertionError as e:
                logger.error("contract verification failed on index edition:\t %s" % e)
                success = False
        if not self.allow_add_drop_record:
            success = success and self.check_values(len(df_in), len(df_out), message="record count")
        # this check is supposed to always pass ( if previous checks are ok )
        assert ((set(df_in.columns) | set(self.col_additions.keys())) - self.col_deletions) == set(df_out.columns) or not success
        # check columns modifications
        unmodifiable_cols = set(df_in.columns) - (self.col_deletions | self.col_editions)
        if not self.allow_index_edition:
            try:
                pd.testing.assert_frame_equal(df_in[unmodifiable_cols].loc[df_out.index], df_out[unmodifiable_cols])
            except AssertionError as e:
                logger.error("contract verification failed on index edition:\t %s" % e)
                success = False
        if not success:
            raise RuntimeError("contract check failure")

    @staticmethod
    def check_values(expected, real, message):
        logger = logging.getLogger(__name__)
        try:
            assert expected == real
            ok = True
        except AssertionError as e:
            logger.error("contract verification failed on " + message + ":\t expected: %s, but got %s" % (expected, real))
            ok = False
        return ok
