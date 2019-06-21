import hathorprocessing

table = 'dx'

columns = (
    "admissiondxid",
    "patientunitstayid",
    "admitdxenteredoffset",
    "admitdxpath",
    "admitdxname",
    "admitdxtext"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
