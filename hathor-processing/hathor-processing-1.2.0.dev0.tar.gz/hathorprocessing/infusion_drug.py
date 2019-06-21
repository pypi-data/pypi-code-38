import hathorprocessing

table = 'infusion_drug'

columns = (
    "infusiondrugid",
    "patientunitstayid",
    "infusionoffset",
    "drugname",
    "drugrate",
    "infusionrate",
    "drugamount",
    "volumeoffluid",
    "patientweight"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
