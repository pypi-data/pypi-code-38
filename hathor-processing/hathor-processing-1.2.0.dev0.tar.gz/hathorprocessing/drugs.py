import hathorprocessing

table = 'drugs'

columns = (
    "admissiondrugid",
    "patientunitstayid",
    "drugoffset",
    "drugenteredoffset",
    "drugnotetype",
    "specialtytype",
    "usertype",
    "rxincluded",
    "writtenineicu",
    "drugname",
    "drugdosage",
    "drugunit",
    "drugadmitfrequency",
    "drughiclseqno"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
