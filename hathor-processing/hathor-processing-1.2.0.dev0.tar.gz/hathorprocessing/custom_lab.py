import hathorprocessing

table = 'custom_lab'

columns = (
    "customlabid",
    "patientunitstayid",
    "labotheroffset",
    "labothertypeid",
    "labothername",
    "labotherresult",
    "labothervaluetext"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
