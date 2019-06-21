import hathorprocessing

table = 'vital_aperiodic'

columns = (
    "vitalaperiodicid",
    "patientunitstayid",
    "observationoffset",
    "noninvasivesystolic",
    "noninvasivediastolic",
    "noninvasivemean",
    "paop",
    "cardiacoutput",
    "cardiacinput",
    "svr",
    "svri",
    "pvr",
    "pvri"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
