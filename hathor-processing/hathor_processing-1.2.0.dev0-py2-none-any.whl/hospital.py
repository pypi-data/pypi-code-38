import hathorprocessing

table = 'hospital'

columns = (
    "hospitalid",
    "numbedscategory",
    "teachingstatus",
    "region"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
