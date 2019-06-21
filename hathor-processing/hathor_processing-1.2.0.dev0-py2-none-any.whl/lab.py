import hathorprocessing

table = 'lab'

columns = (
    "labid",
    "patientunitstayid",
    "labresultoffset",
    "labtypeid",
    "labname",
    "labresult",
    "labresulttext",
    "labmeasurenamesystem",
    "labmeasurenameinterface",
    "labresultrevisedoffset"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
