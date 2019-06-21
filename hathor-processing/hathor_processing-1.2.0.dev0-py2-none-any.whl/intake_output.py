import hathorprocessing

table = 'intake_output'

columns = (
    "intakeoutputid",
    "patientunitstayid",
    "intakeoutputoffset",
    "intaketotal",
    "outputtotal",
    "dialysistotal",
    "nettotal",
    "intakeoutputentryoffset",
    "cellpath",
    "celllabel",
    "cellvaluenumeric",
    "cellvaluetext"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
