import hathorprocessing

table = 'note'

columns = (
    "noteid",
    "patientunitstayid",
    "noteoffset",
    "noteenteredoffset",
    "notetype",
    "notepath",
    "notevalue",
    "notetext"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
