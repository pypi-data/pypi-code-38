import hathorprocessing

table = 'patient'

columns = (
    "patientunitstayid",
    "patienthealthsystemstayid",
    "gender",
    "age",
    "ethnicity",
    "hospitalid",
    "wardid",
    "apacheadmissiondx",
    "admissionheight",
    "hospitaladmittime24",
    "hospitaladmitoffset",
    "hospitaladmitsource",
    "hospitaldischargeyear",
    "hospitaldischargetime24",
    "hospitaldischargeoffset",
    "hospitaldischargelocation",
    "hospitaldischargestatus",
    "unittype",
    "unitadmittime24",
    "unitadmitsource",
    "unitvisitnumber",
    "unitstaytype",
    "admissionweight",
    "dischargeweight",
    "unitdischargetime24",
    "unitdischargeoffset",
    "unitdischargelocation",
    "unitdischargestatus",
    "uniquepid"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
