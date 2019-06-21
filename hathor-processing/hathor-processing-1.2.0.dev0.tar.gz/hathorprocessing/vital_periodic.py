import hathorprocessing

table = 'vital_periodic'

columns = (
    "vitalperiodicid",
    "patientunitstayid",
    "observationoffset",
    "temperature",
    "sao2",
    "heartrate",
    "respiration",
    "cvp",
    "etco2",
    "systemicsystolic",
    "systemicdiastolic",
    "systemicmean",
    "pasystolic",
    "padiastolic",
    "pamean",
    "st1",
    "st2",
    "st3",
    "icp"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
