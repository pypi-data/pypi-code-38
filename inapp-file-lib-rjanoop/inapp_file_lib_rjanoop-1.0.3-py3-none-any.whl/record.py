class Record:
    vdict = dict()
    count = 0
    record = dict()
    reclen = 0
    fd = None

    # The constructor opens the Record Defenition File and sets
    # the record defenition
    def __init__(self, recName, fileName, mode="r", encoding="Latin-1"):
        defstr = self.recordDef(recName)
        self.vdict = self.vardict(defstr)
        self.fd = self.openfile(fileName, mode, encoding)

    def getreclen(self, add = 0):
        if self.reclen==int(0):
            here = self.fd.tell()
            try:
                reclen = len(self.fd.readline()) + add
            except:
                reclen = 0
            self.reclen = reclen
            # self.fd.seek(here, 0)
            # self.fd.seek(here, 0)
            self.rewind()
            return reclen
        else:
            return self.reclen

    def Change_fielddef(self, recName):
        defstr = self.recordDef(recName)
        self.vdict = self.vardict(defstr)
        try:
            self.reclen = len(self.fd.readline()) + 1
        except:
            self.reclen = 0
        return self.vdict

    def openfile(self, fileName, mode, encoding):
        try:
            fd = open(fileName, mode, encoding="Latin-1")
        except Exception as e:
            print(e)
            quit()
        else:
            return fd

    # Read the record defenition from "field.def" file
    def recordDef(self, recName):
        fx = open("Input/field.def", "r", encoding="Latin-1")
        line = fx.readline()
        while line:
            line = line.split("#", 1)[0]
            line.lstrip()
            if (len(line) < 3):
                line = fx.readline()
                continue

            name, defstr = line.split("=")
            if (name.strip() == recName.strip()):
                return(defstr)
            line = fx.readline()
        print(recName, ": Record Definition not found");
        quit()

    # Create a dict with each name="field Name"
    # and Value = a list consiting of two elements
    # 1) The Start Character Position and 2) End Char position
    def vardict(self, defstr):
        col = 0
        recdict = dict()
        nv = (item.split(" AS ") for item in defstr.split(","))
        for item in nv:
            num = int(item[0].strip())
            recdict[(item[1]).strip()[0:-1]] = [col, col + num]
            col = col + num
        return(recdict)

    def getline(self):
        try:
            line = self.fd.readline()
        except Exception as e:
            print("Error Reading Line", self.count)
        finally:
            return(line)

    # Parse a line of data using the record defenition
    # and create an easily accessible record.
    def parseline(self, line):
        recdef = self.vdict
        recdict = {}
        for name in recdef:
            recdict[name] = line[recdef[name][0]:recdef[name][1]]
        return(recdict)

    # Reading each line and call Parse Rec
    def readrec(self):
        line = self.getline()
        line = line.rstrip("\r\n")
        line = line.rstrip("\n")
        line = line.rstrip("\r")
        if not line:
            return False
        rec = self.parseline(line)
        self.count = self.count + 1
        self.setrec(rec)
        return(rec)

    # Copy a record to this Object (self.record)
    def setrec(self, rec):
        for item in rec:
            self.record[item] = rec[item]

    # Write a Record as an output line
    def writerec(self, rec):
        self.setrec(rec)
        line = ""
        for field in self.vdict:
            self.sizeadjust(field, self.record)
            line = line + self.record[field]
        line = line + "\r";
        self.fd.write(line)

    # Some fields in the record my be longer or shorter
    # The size is adjusted to the correct size
    def sizeadjust(self, field, rec):
        length = self.vdict[field][1] - self.vdict[field][0]
        length = 0 if (length < 0) else length
        if (len(str(rec[field])) == length):
            return
        elif (length > len(str(rec[field]))):
            while (length > len(str(rec[field]))):
                rec[field] = str(rec[field]) + ' '
        else:
            rec[field] = rec[field][:length]

    # Rewind takes to the begining of the file

    def rewind(self):
        self.fd.seek(0)

    # Get a specific record
    def getrec(self, rec_no):
        # print(rec_no)
        self.fd.seek(rec_no * self.reclen)
        rec = self.readrec()
        return(rec)

    # Put a specific record
    def putrec(self, rec, rec_no):
        self.fd.seek(rec_no * self.reclen)
        self.writerec(rec)

    # Get maximum number of records in an open file
    def getmaxrecs(self):
        here = self.fd.tell()
        last = self.fd.seek(0, 2)
        nos = self.fd.tell() / self.reclen
        self.fd.seek(here, 0)
        return(nos)
