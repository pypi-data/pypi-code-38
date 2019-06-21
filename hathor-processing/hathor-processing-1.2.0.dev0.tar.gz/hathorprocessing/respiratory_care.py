import hathorprocessing

table = 'respiratory_care'

columns = (
    "respcareid",
    "patientunitstayid",
    "respcarestatusoffset",
    "currenthistoryseqnum",
    "airwaytype",
    "airwaysize",
    "airwayposition",
    "cuffpressure",
    "ventstartoffset",
    "ventendoffset",
    "priorventstartoffset",
    "priorventendoffset",
    "apneaparms",
    "lowexhmvlimit",
    "hiexhmvlimit",
    "lowexhtvlimit",
    "hipeakpreslimit",
    "lowpeakpreslimit",
    "hirespratelimit",
    "lowrespratelimit",
    "sighpreslimit",
    "lowironoxlimit",
    "highironoxlimit",
    "meanairwaypreslimit",
    "peeplimit",
    "cpaplimit",
    "setapneainterval",
    "setapneatv",
    "setapneaippeephigh",
    "setapnearr",
    "setapneapeakflow",
    "setapneainsptime",
    "setapneaie",
    "setapneafio2"
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
