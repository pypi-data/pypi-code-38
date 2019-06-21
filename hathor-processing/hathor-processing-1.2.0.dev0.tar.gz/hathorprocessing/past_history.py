import hathorprocessing

table = 'past_history'

columns = (
    "pasthistoryid",
    "patientunitstayid",
    "pasthistoryoffset",
    "pasthistoryenteredoffset",
    "pasthistorynotetype",
    "pasthistorypath",
    "pasthistoryvalue",
    "pasthistoryvaluetext"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
