import hathorprocessing

table = 'care_plan_infectious_disease'

columns = (
    "cplinfectid",
    "patientunitstayid",
    "activeupondischarge",
    "cplinfectdiseaseoffset",
    "infectdiseasesite",
    "infectdiseaseassessment",
    "responsetotherapy",
    "treatment"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
