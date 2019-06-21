import hathorprocessing

table = 'care_plan_general'

columns = (
    "cplgeneralid",
    "patientunitstayid",
    "activeupondischarge",
    "cplitemoffset",
    "cplgroup",
    "cplitemvalue"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
