#

def merge_sql(table_left, table_right, condition="", how="inner"):
    '''
    Merge two datasets using database join.
    The table_left is joined with table_right using the method `how` (inner, left inner/outer, right inner/outer).
    The parameter `condition` is appended to the query, specify the join keys (example using ("index")).

    Parameters
    ----------
    table_left :
        left input table to join
    table_right :
        right input table to join
    condition :
        join condition, example "using (index)"
    how :
        join type inner, left, right

    Returns
    -------
    str
        query the generated query

    Note
    ----
    
    '''
    query = "select * from {table_left} left_table {how} join {table_right} right_table {condition};".format(
        table_left=table_left, table_right=table_right,
        condition=condition, how=how)
    return query

