import hathorprocessing

table = 'treatment'

columns = (
    "treatmentid",
    "patientunitstayid",
    "treatmentoffset",
    "treatmentstring",
    "activeupondischarge"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
