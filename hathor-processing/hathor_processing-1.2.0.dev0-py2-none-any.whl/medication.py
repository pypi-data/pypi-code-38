import hathorprocessing

table = 'medication'

columns = (
    "medicationid",
    "patientunitstayid",
    "drugorderoffset",
    "drugstartoffset",
    "drugivadmixture",
    "drugordercancelled",
    "drugname",
    "drughiclseqno",
    "dosage",
    "routeadmin",
    "frequency",
    "loadingdose",
    "prn",
    "drugstopoffset",
    "gtc"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
