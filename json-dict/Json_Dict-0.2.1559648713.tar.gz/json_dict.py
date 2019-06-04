import json
import os


class JsonDict:
    def __init__(self, file=None, data=None, createfile=True, autosave=True):
        self.file = None
        self.autosave = autosave
        if data is not None:
            if isinstance(data, str):
                data = json.loads(data)
            elif isinstance(data, JsonDict):
                data = data.data
        else:
            data = {}
        self.data = data
        if file is not None:
            self.read(file, createfile=createfile)

    def get(self, *args, default=None, autosave=True):
        d = self.data
        args = [str(arg) for arg in args]
        for arg in args[:-1]:
            arg = str(arg)
            if arg not in d:
                d[arg] = {}
            d = d[arg]

        if args[-1] not in d:
            self.put(*args, value=default, autosave=autosave)

        return d[args[-1]]

    def read(self, file, createfile=False):
        try:
            with open(file) as f:
                self.file = os.path.abspath(file)
                self.data = json.loads(f.read())
        except Exception as e:
            if createfile:
                with open(file, "w+") as f:
                    self.save(file=file)
                self.read(file, createfile=False)

    def stringify_keys(self, diction=None):
        if diction is None:
            diction = self.data
        for k in list(diction.keys()):
            if isinstance(diction[k], dict):
                self.stringify_keys(diction=diction[k])
            diction[str(k)] = diction.pop(k)

    def save(self, file=None):
        if file is not None:
            self.file = os.path.abspath(file)
        if self.file is not None:
            with open(self.file, "w+") as outfile:
                self.stringify_keys()
                json.dump(self.data, outfile, indent=4, sort_keys=True)

    def to_json(self):
        return json.dumps(self.data)

    def put(self, *args, value, autosave=True):
        d = self.data
        for arg in args[:-1]:
            arg = str(arg)
            if arg not in d:
                d[arg] = {}
            d = d[arg]

        new = False
        if args[-1] not in d:
            new = True
            d[args[-1]] = None
        elif d[args[-1]] != value:
            new = True
        preval = d[args[-1]]
        d[args[-1]] = value

        if new or (preval != value):
            if self.autosave and autosave:
                self.save()

        return value, new

    def __getitem__(self, key):
        return self.data.get(key)

    def getsubdict(self, preamble=None):
        if preamble is None:
            preamble = []
        return JsonSubDict(parent=self,preamble=preamble)


class JsonSubDict():
    def __init__(self,parent,preamble):
        self.preamble = preamble
        self.parent = parent
        self.parent.get(*self.preamble,default={})
        self.save = self.parent.save

    def get(self, *args, default=None, autosave=True):
        self.parent.get(*(self.preamble+list(args)),default=default,autosave=autosave)

    def put(self, *args, value, autosave=True):
        self.parent.put(*(self.preamble+list(args)),value=value,autosave=autosave)

    def to_json(self):
        d = self.parent.data
        for p in self.preamble:
            d=d[p]
        return json.dumps(d)

    def __getitem__(self, key):
        d = self.parent.data
        for p in self.preamble:
            d=d[p]
        return d.get(key)

    def getsubdict(self, preamble=None):
        if preamble is None:
            preamble = []
        preamble = self.preamble + preamble
        return JsonSubDict(parent=self.parent,preamble=preamble)

