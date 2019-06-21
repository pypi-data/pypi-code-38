import hathorprocessing

table = 'care_plan_eol'

columns = (
    "cpleolid",
    "patientunitstayid",
    "cpleolsaveoffset",
    "cpleoldiscussionoffset",
    "activeupondischarge"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
