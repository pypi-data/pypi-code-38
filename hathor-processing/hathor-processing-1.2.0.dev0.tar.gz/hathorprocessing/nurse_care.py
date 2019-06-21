import hathorprocessing

table = 'nurse_care'

columns = (
    "nursecareid",
    "patientunitstayid",
    "celllabel",
    "nursecareoffset",
    "nursecareentryoffset",
    "cellattributepath",
    "cellattribute",
    "cellattributevalue"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
