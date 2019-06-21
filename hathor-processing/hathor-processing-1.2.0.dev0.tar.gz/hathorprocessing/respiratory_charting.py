import hathorprocessing

table = 'respiratory_charting'

columns = (
    "respchartid",
    "patientunitstayid",
    "respchartoffset",
    "respchartentryoffset",
    "respcharttypecat",
    "respchartvaluelabel",
    "respchartvalue"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
