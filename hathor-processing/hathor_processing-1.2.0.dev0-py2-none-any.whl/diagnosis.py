import hathorprocessing

table = 'diagnosis'

columns = (
    "diagnosisid",
    "patientunitstayid",
    "activeupondischarge",
    "diagnosisoffset",
    "diagnosisstring",
    "icd9code",
    "diagnosispriority"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
