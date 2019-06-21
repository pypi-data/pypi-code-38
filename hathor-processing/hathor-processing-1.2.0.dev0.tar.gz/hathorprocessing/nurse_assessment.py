import hathorprocessing

table = 'nurse_assessment'

columns = (
    "nurseassessid",
    "patientunitstayid",
    "nurseassessoffset",
    "nurseassessentryoffset",
    "cellattributepath",
    "celllabel",
    "cellattribute",
    "cellattributevalue"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
