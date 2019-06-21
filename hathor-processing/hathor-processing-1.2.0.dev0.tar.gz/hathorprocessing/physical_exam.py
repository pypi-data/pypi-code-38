import hathorprocessing

table = 'physical_exam'

columns = (
    "physicalexamid",
    "patientunitstayid",
    "physicalexamoffset",
    "physicalexampath",
    "physicalexamvalue",
    "physicalexamtext"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
