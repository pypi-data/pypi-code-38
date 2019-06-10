SETTINGS_VERSION = 2  # YAML settings file version

# Default values for all
DEFAULTGEN = {
    "TITLE": "Project Title",
    "LSAV": False,
    "ITEST": 1,
    "LREC": False,
    "LCPUTM": False,
    "TSOS": 5,
    "TMAX": 3600,
}

DEFAULTTIME = {"MT": 3, "NSHOT": 5, "TPS": None}

DEFAULTMESH = {
    "DDR": 0.001,
    "DDZ": 0.001,
    "NR": None,
    "NZ": None,
    "RMARK": None,
    "RZ": None,
}

DEFAULTBEAM = {
    "MROT": 0,
    "SIG": None,
    "ISIG": 5,
    "RDRIVE": None,
    "NBUNCH": 1,
    "BSEP": 0,
}

DEFAULTWAKE = {
    "UBT": None,
    "LCFRON": True,
    "LCBACK": True,
    "LCHIN": True,
    "LNAPOLY": False,
    "LNONAP": False,
    "LCRBW": False,
    "ZCF": None,
    "ZCT": None,
    "ZSEP": 0,
    "RWAK": None,
}

DEFAULTPLOT = {
    "LCAVIN": True,
    "LCAVUS": False,
    "LPATH": False,
    "LPLW": False,
    "LPLWL": False,
    "LPLWA": False,
    "LPLWT": False,
    "LFFT": False,
    "LFFTL": False,
    "LFFTA": False,
    "LFFTT": False,
    "LINTZ": False,
    "LSPEC": False,
    "LWNDW": False,
    "NWFUN": 1,
    "ALPHA": 3,
    "CUTOFF": 0,
    "EXPFAC": 20,
    "LPLE": False,
    "LPLC": False,
    "NPLOT": 10,
    "LPALL": False,
}

DEFAULTPRINT = {
    "LPRW": False,
    "LMATPR": False,
    "LSVW": False,
    "LSVWL": False,
    "LSVWA": False,
    "LSVWT": False,
    "LSVF": False,
}


class JOB:
    """JOB object holds a named configuration and its index in GUI list of jobs"""

    def __init__(self, name=None, index=None, settings=None):
        """Init with name, index and settings"""
        self.__name = name
        self.__index = index
        self.__settings = settings

    def name(self, name=None):
        """Get/set name"""
        if name is not None:
            self.__name = name
        else:
            return self.__name

    def index(self, index=None):
        """Get/set index"""
        if index is not None:
            self.__index = index
        else:
            return self.__index

    def settings(self, settings=None):
        """Get/set settings"""
        if settings is not None:
            self.__settings = settings
        else:
            return self.__settings


class JobList:
    """Job list holds list of JOB objects and some common settings"""

    def __init__(self):
        """"""
        self.__VERSION = SETTINGS_VERSION
        self.__common = {"gensec": DEFAULTGEN, "timesec": DEFAULTTIME}

        self.__anonym = {
            "meshsec": DEFAULTMESH,
            "beamsec": DEFAULTBEAM,
            "wakesec": DEFAULTWAKE,
            "plotsec": DEFAULTPLOT,
            "printsec": DEFAULTPRINT,
        }

        self.__list = []

    def add(self, name, index, settings):
        """Create job and add it to list"""
        self.pop(index)
        j = JOB(name=name, index=index, settings=settings)
        self.__list.append(j)
        self.__list.sort(key=lambda x: x.index())

    def push(self, obj):
        """Push job to list"""
        self.__list.append(obj)
        self.__list.sort(key=lambda x: x.index())

    def pop(self, index):
        """Pop job from list"""
        try:
            i = [i.index() for i in self.__list].index(index)
            return self.__list.pop(i)
        except ValueError:
            return None

    def get(self, index):
        """Get job with index"""
        try:
            i = [i.index() for i in self.__list].index(index)
            return self.__list[i]
        except ValueError:
            return None

    def set_anonym(self, settings):
        """Set other settings"""
        self.__anonym = settings

    def get_anonym(self):
        """Get other settings"""
        return self.__anonym

    def set_common(self, settings):
        """Set common settings"""
        self.__common = settings

    def get_common(self):
        """Get common settings"""
        return self.__common

    def dump_settings(self):
        """dump all settings"""
        if len(self.__list) == 0:
            return [self.get_anonym()]
        else:
            return [i.settings() for i in self.__list]

    def iterate_list(self):
        """Iterate over job list"""
        for i in self.__list:
            yield i

    def version(self):
        """Get settings version"""
        return self.__VERSION


def generate_file(file, geomtype, geom, commsec, jobsec):
    """Construct input file from options of all jobs.
    file: input file path
    geomtype: absolute or incremental
    geom: geometry points
    commsec: common section settings
    jobsec: list of job settings"""
    # map of some string patterns
    B = {True: ".T.", False: ".F.", None: "", "Absolute": "##", "Incremental": "@@"}
    try:
        with open(file, "w") as f:
            # General options
            f.write(
                f""" &FILE LSAV={B[commsec["gensec"]["LSAV"]]}, \
ITEST={commsec["gensec"]["ITEST"]}, LREC={B[commsec["gensec"]["LSAV"]]}, \
LCPUTM={B[commsec["gensec"]["LSAV"]]}, TSOS={commsec["gensec"]["TSOS"]}, \
TMAX={commsec["gensec"]["TMAX"]} &END\n"""
            )
            # Title
            f.write(f""" {commsec["gensec"]["TITLE"]}\n""")
            # Dummy
            f.write(" &BOUN IZL=3, IZR=3 &END\n")
            # Mesh
            f.write(f""" &MESH DDZ={jobsec[0]["meshsec"]["DDZ"]}""")
            if jobsec[0]["meshsec"]["DDR"] is not None:
                f.write(f""", DDR={jobsec[0]["meshsec"]["DDR"]}""")
            if jobsec[0]["meshsec"]["NR"] is not None:
                f.write(f""", NR={jobsec[0]["meshsec"]["NR"]}""")
            if jobsec[0]["meshsec"]["NZ"] is not None:
                f.write(f""", NZ={jobsec[0]["meshsec"]["NZ"]}""")
            if jobsec[0]["meshsec"]["RMARK"] is not None:
                f.write(f""", RMARK={jobsec[0]["meshsec"]["RMARK"]}""")
            if jobsec[0]["meshsec"]["RZ"] is not None:
                f.write(f""", RZ={jobsec[0]["meshsec"]["RZ"]}""")
            f.write(" &END\n")
            # Geometry points
            f.write(f""" {B[geomtype]}CAVITYSHAPE\n""")
            f.write("0.\n")
            for r, z in geom:
                f.write(f"{r} {z}\n")
            f.write("9999. 9999.\n")
            firstpass = True  # flag indicating that it is a first iteration
            for j in jobsec:
                if not firstpass:
                    f.write("CONTINUE\n")
                    # Mesh
                    f.write(f""" &MESH""")
                    if j["meshsec"]["DDZ"] is not None:
                        f.write(f""" DDZ={j["meshsec"]["DDZ"]}""")
                    else:
                        f.write(f""" DDZ=0.001""")
                    if j["meshsec"]["DDR"] is not None:
                        f.write(f""", DDR={j["meshsec"]["DDR"]}""")
                    else:
                        f.write(f""", DDR=0.001""")
                    if j["meshsec"]["NR"] is not None:
                        f.write(f""", NR={j["meshsec"]["NR"]}""")
                    if j["meshsec"]["NZ"] is not None:
                        f.write(f""", NZ={j["meshsec"]["NZ"]}""")
                    if j["meshsec"]["RMARK"] is not None:
                        f.write(f""", RMARK={j["meshsec"]["RMARK"]}""")
                    if j["meshsec"]["RZ"] is not None:
                        f.write(f""", RZ={j["meshsec"]["RZ"]}""")
                    f.write(" &END\n")
                # Beam
                f.write(
                    f""" &BEAM MROT={j["beamsec"]["MROT"]}, \
ISIG={j["beamsec"]["ISIG"]}, NBUNCH={j["beamsec"]["NBUNCH"]}, \
BSEP={j["beamsec"]["BSEP"]}"""
                )
                if j["beamsec"]["SIG"] is not None:
                    f.write(f""", SIG={j["beamsec"]["SIG"]}""")
                if j["beamsec"]["RDRIVE"] is not None:
                    f.write(f""", RDRIVE={j["beamsec"]["RDRIVE"]}""")
                f.write(" &END\n")
                if firstpass:  # only for first iteration
                    # Time
                    f.write(
                        f""" &TIME MT={commsec["timesec"]["MT"]}, \
NSHOT={commsec["timesec"]["NSHOT"]}"""
                    )
                    if commsec["timesec"]["TPS"] is not None:
                        f.write(f""", TPS={commsec["timesec"]["TSP"]}""")
                    f.write(" &END\n")
                # Wake
                f.write(
                    f""" &WAKE LCFRON={j["wakesec"]["LCFRON"]}, \
LCBACK={j["wakesec"]["LCBACK"]}, LCHIN={j["wakesec"]["LCHIN"]}, \
LNAPOLY={j["wakesec"]["LNAPOLY"]}, LNONAP={j["wakesec"]["LNONAP"]}, \
LCRBW={j["wakesec"]["LCRBW"]}, ZSEP={j["wakesec"]["ZSEP"]}"""
                )
                if j["wakesec"]["UBT"] is not None:
                    f.write(f""", UBT={j["wakesec"]["UBT"]}""")
                if j["wakesec"]["ZCF"] is not None:
                    f.write(f""", ZCF={j["wakesec"]["ZCF"]}""")
                if j["wakesec"]["ZCT"] is not None:
                    f.write(f""", ZCT={j["wakesec"]["ZCT"]}""")
                if j["wakesec"]["RWAK"] is not None:
                    f.write(f""", RWAK={j["wakesec"]["RWAK"]}""")
                f.write(" &END\n")
                # Plot
                f.write(
                    f""" &PLOT LCAVIN={j["plotsec"]["LCAVIN"]}, \
LCAVUS={j["plotsec"]["LCAVUS"]}, LPATH={j["plotsec"]["LPATH"]}, \
LPLW={j["plotsec"]["LPLW"]}, LPLWL={j["plotsec"]["LPLWL"]}, \
LPLWA={j["plotsec"]["LPLWA"]}, LPLWT={j["plotsec"]["LPLWT"]}, \
LFFT={j["plotsec"]["LFFT"]}, LFFTA={j["plotsec"]["LFFTA"]}, \
LFFTA={j["plotsec"]["LFFTA"]}, LFFTT={j["plotsec"]["LFFTT"]}, \
LINTZ={j["plotsec"]["LINTZ"]}, LWNDW={j["plotsec"]["LWNDW"]}, \
NWFUN={j["plotsec"]["NWFUN"]}, ALPHA={j["plotsec"]["ALPHA"]}, \
CUTOFF={j["plotsec"]["CUTOFF"]}, EXPFAC={j["plotsec"]["EXPFAC"]}, \
LPLE={j["plotsec"]["LPLE"]}, LPLC={j["plotsec"]["LPLC"]}, \
NPLOT={j["plotsec"]["NPLOT"]}, LPALL={j["plotsec"]["LPALL"]} &END\n"""
                )
                # Print
                f.write(
                    f""" &PRIN LPRW={j["printsec"]["LPRW"]}, \
LMATPR={j["printsec"]["LMATPR"]}, LSVW={j["printsec"]["LSVW"]}, \
LSVWL={j["printsec"]["LSVWL"]}, LSVWA={j["printsec"]["LSVWA"]}, \
LSVWT={j["printsec"]["LSVWT"]}, LSVF={j["printsec"]["LSVF"]} &END\n"""
                )
                firstpass = False
            f.write("STOP\n")
    except PermissionError:
        pass
