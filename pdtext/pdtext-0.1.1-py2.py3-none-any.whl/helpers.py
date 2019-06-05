def column_swap(column):
    column = column.sort_values(ascending = False)
    return column.index
