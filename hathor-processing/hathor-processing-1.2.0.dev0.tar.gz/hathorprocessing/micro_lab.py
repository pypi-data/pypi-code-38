import hathorprocessing

table = 'micro_lab'

columns = (
    "microlabid",
    "patientunitstayid",
    "culturetakenoffset",
    "culturesite",
    "organism",
    "antibiotic",
    "sensitivitylevel"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
