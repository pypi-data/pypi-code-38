import hathorprocessing

table = 'care_plan_care_provider'

columns = (
    "cplcareprovderid",
    "patientunitstayid",
    "careprovidersaveoffset",
    "providertype",
    "specialty",
    "interventioncategory",
    "managingphysician",
    "activeupondischarge"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
