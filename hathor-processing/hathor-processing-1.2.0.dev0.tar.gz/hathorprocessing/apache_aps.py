import hathorprocessing

table = 'apache_aps'

columns = (
    "apacheapsvarid",
    "patientunitstayid",
    "intubated",
    "vent",
    "dialysis",
    "eyes",
    "motor",
    "verbal",
    "meds",
    "urine",
    "wbc",
    "temperature",
    "respiratoryrate",
    "sodium",
    "heartrate",
    "meanbp",
    "ph",
    "hematocrit",
    "creatinine",
    "albumin",
    "pao2",
    "pco2",
    "bun",
    "glucose",
    "bilirubin",
    "fio2"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
