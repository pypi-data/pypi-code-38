def top_catg(x, col):
    count = x.groupby(col).size()
    sorted_count = count.sort_values(ascending=False)
    return sorted_count.first_valid_index()


def top_value(x, col):
    count = x.groupby(col).size()
    sorted_count = count.sort_values(ascending=False)
    return sorted_count.iloc[0]