class InoCreator:
    def __init__(self, board):
        self.creators = []
        self.board = board
        self.data = dict(
            definitions={},
            global_vars={},
            includes=set([]),
            functions={},
            setup="",
            loop="",
            dataloop="",
        )

    def add(
        self,
        definitions=None,
        global_vars=None,
        includes=None,
        functions=None,
        setup=None,
        loop=None,
        dataloop=None,
    ):
        if definitions is not None:
            self.add_definitions(definitions)
        if global_vars is not None:
            self.add_global_vars(global_vars)
        if includes is not None:
            self.add_includes(includes)
        if functions is not None:
            self.add_functions(functions)
        if setup is not None:
            self.add_setup(setup)
        if loop is not None:
            self.add_loop(loop)
        if dataloop is not None:
            self.add_dataloop(dataloop)

    def add_definitions(self, definitions):
        for name, value in definitions.items():
            self.add_definition(name, value)

    def add_definition(self, name, value):
        if name in self.data["definitions"]:
            raise ValueError(name + " already defined")
        self.data["definitions"][name] = value

    def add_global_vars(self, vars):
        for name, value in vars.items():
            self.add_global_var(name, value)

    def add_global_var(self, name, value):
        if name in self.data["global_vars"]:
            raise ValueError(name + " already defined")
        self.data["global_vars"][name] = value

    def add_includes(self, includes):
        self.data["includes"].update(includes)

    def add_functions(self, functions):
        for name, value in functions.items():
            self.add_function(name, value)

    def add_function(self, name, value):
        if name in self.data["functions"]:
            raise ValueError(name + " already defined")
        self.data["functions"][name] = value

    def add_setup(self, setup):
        self.data["setup"] = self.data["setup"] + setup

    def add_loop(self, loop):
        self.data["loop"] = self.data["loop"] + loop

    def add_dataloop(self, dataloop):
        self.data["dataloop"] = self.data["dataloop"] + dataloop

    def create(self):
        for creator in self.creators:
            self.add(**creator(self.board))
        text = ""
        for name, value in self.data["definitions"].items():
            text += "#define " + name + " " + str(value) + "\n"
        for inc in self.data["includes"]:
            text += "#include " + inc + "\n"
        for name, value in self.data["global_vars"].items():
            text += (
                value[0]
                + " "
                + name
                + (" = " + str(value[1]) if value[1] is not None else "")
                + ";\n"
            )
        for name, value in self.data["functions"].items():
            text += (
                value[0]
                + " "
                + name
                + "("
                + ", ".join([arg[0] + " " + arg[1] for arg in value[1]])
                + "){\n"
                + value[2]
                + "}\n"
            )

        text += "\nvoid dataloop(){\n" + self.data["dataloop"] + "\n}\n"
        text += "\nvoid loop(){\n" + self.data["loop"] + "\n}\n"
        text += "\nvoid setup(){\n" + self.data["setup"] + "\n}\n"
        return text

    def add_creator(self, creator):
        self.creators.append(creator)
