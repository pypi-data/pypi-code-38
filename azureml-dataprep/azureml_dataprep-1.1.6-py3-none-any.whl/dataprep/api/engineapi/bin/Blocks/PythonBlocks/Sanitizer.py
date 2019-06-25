class Sanitizer():
    @classmethod
    def makeNamesUnique(cls, names: []) -> []:
        # We don't want to use any existing names as new unique names
        # and then rename a column that is not duplicated. e.g.
        #  X, X, X_1 
        # should result in:
        #  X, X_2, X_1
        # not:
        #  X, X_1, X_1_1  <- renamed something that is not duplicated breaking references to X_1
        takenNames = set(names)
        seenNames = set()
        unames = []
        baseNameCounters = {}
        for name in names:
            if name in seenNames:
                name = Sanitizer._makeUnique(baseNameCounters, takenNames, name)
                takenNames.add(name)
            else:
                seenNames.add(name)
            unames.append(name)

        return unames

    @classmethod
    def _makeUnique(cls, baseNameCounters, nameSet, name: str) -> str:
        uniqueName = name
        if name in nameSet:
            suffix = baseNameCounters[name] if name in baseNameCounters else 1
            while True:
                uniqueName = name + "_" + str(suffix)
                suffix += 1
                if uniqueName not in nameSet:
                    break
            baseNameCounters[name] = suffix
        return uniqueName

    @classmethod
    def makeUnique(cls, nameSet, name: str) -> str:
        return Sanitizer._makeUnique({}, nameSet, name)

    @classmethod
    def validateUnique(cls, name: str, existingNames: []):
        if not Sanitizer.makeUnique(existingNames, name) == name:
            raise ValueError('Column name "{0}" already exists.'.format(name), 'InvalidColumnName')