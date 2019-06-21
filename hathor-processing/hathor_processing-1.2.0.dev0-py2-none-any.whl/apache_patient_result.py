import hathorprocessing

table = 'apache_patient_result'

columns = (
    "apachepatientresultsid",
    "patientunitstayid",
    "physicianspeciality",
    "physicianinterventioncategory",
    "acutephysiologyscore",
    "apachescore",
    "apacheversion",
    "predictedicumortality",
    "actualicumortality",
    "predictediculos",
    "actualiculos",
    "predictedhospitalmortality",
    "actualhospitalmortality",
    "predictedhospitallos",
    "actualhospitallos",
    "preopmi",
    "preopcardiaccath",
    "ptcawithin24h",
    "unabridgedunitlos",
    "unabridgedhosplos",
    "actualventdays",
    "predventdays",
    "unabridgedactualventdays"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
