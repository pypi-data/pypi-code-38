import os


class ZoKrates:
    def __init__(self, instructions, inputs_and_outputs):
        self.code = []
        self.input_assignments = []
        self.outputs = []

        for ins in instructions:
            # Add indentation and newline to each line in the code block
            self.code.append("\t{}\n".format(ins.to_zokrates()))

        self.header = ["def main("]
        # Array for storing the parameters of the main method
        parameters = []
        for entry in inputs_and_outputs:
            if entry["is_input"]:
                self.input_assignments.append(entry["value"])

                if entry["is_public"]:
                    parameters.append("field v{}".format(entry["index"]))
                else:  # private
                    parameters.append("private field v{}".format(entry["index"]))
            else:
                self.outputs.append("v{}".format(entry["index"]))

        self.header.append(", ".join(parameters))
        self.header.append(") -> (field): \n\n")
        self.header = "".join(self.header)

        # Return the outputs
        if self.outputs:
            self.code.append("\treturn {}\n".format(",".join(self.outputs)))
        else:
            # Return 0 if no outputs are specified, as ZoKrates requires a
            # return statement
            self.code.append("\treturn 0\n")

    def compile(self, path):
        self.__write_code_file(path)
        self.path = path

    def synthesize(self):
        cmd = "zokrates compile -i {}".format(self.path)
        status = os.system(cmd)
        if __debug__:
            print(status)

    def setup(self):
        cmd = "zokrates setup"
        status = os.system(cmd)
        if __debug__:
            print(status)

    def compute_witness(self):
        # TODO: read args from file
        args = " ".join(self.input_assignments)
        cmd = "zokrates compute-witness -a {}".format(args)
        status = os.system(cmd)
        if __debug__:
            print(status)

    def generate_proof(self):
        cmd = "zokrates generate-proof"
        status = os.system(cmd)
        if __debug__:
            print(status)

    def run(self, path):
        self.compile(path)
        self.synthesize()
        self.setup()
        self.compute_witness()
        self.generate_proof()

    def __write_code_file(self, path):
        with open(path, "w+") as f:
            f.write(self.header)
            for l in self.code:
                f.write(l)
