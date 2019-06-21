import hathorprocessing

table = 'care_plan_goal'

columns = (
    "cplgoalid",
    "patientunitstayid",
    "cplgoaloffset",
    "cplgoalcategory",
    "cplgoalvalue",
    "cplgoalstatus",
    "activeupondischarge"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
