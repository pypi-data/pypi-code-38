from .query import query
import pandas_light
import pandas_flavor as pf


def query_subject():
    """Return the subject info table.

    Returns:
        pd.DataFrame: Return as DataFrame.
    """
    sql = 'select * from view_subjects'
    return query(sql)


@pf.register_dataframe_method
def pycnet_vmap_subject(df, subj_id='subj_id'):
    """vmap subject name into a DataFrame. Key must be subject id.

    Args:
        subj_id (str, optional): The column with subject id. Defaults to 'subj_id'.
    """
    return df.vmap(query_subject(), on=subj_id, right_on='id', take='subj_name')
