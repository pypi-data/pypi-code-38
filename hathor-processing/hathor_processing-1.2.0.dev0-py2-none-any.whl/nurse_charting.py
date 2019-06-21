import hathorprocessing

table = 'nurse_charting'

columns = (
    "nursingchartid",
    "patientunitstayid",
    "nursingchartoffset",
    "nursingchartentryoffset",
    "nursingchartcelltypecat",
    "nursingchartcelltypevallabel",
    "nursingchartcelltypevalname",
    "nursingchartvalue"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
