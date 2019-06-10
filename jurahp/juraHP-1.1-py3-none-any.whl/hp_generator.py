#!/usr/bin/env python

__author__ = 'david.johnnes@gmail.com'


class HPGenRobot(object):
    """"""

    def __init__(self, filename):
        """ """
        self.filename = filename  # filename must be a .txt file
        self.base_lines = []
        self.splited_list = []
        self.clean_interfaces = ["conf t"]

    def string_cleaner(self):
        with open(self.filename) as file:
            for line in file:
                line = line.strip()

                if "-AP-" in line:
                    line = line.replace("|", "")  # remove the |
                    self.base_lines.append(line)

    def file_spliter(self):
        for line in self.base_lines:
            splited_line = line.split()

            if len(splited_line) == 3:
                self.splited_list.append(splited_line)
            else:
                print("Bad data passed to the file_spliter() !!\n")
                break

    def make_strings(self):
        for line in self.splited_list:
            local_port = line[0]
            remote_host = line[1]

            new_interfaces = "interface {0} name {1}(G0)".format(local_port, remote_host)
            self.clean_interfaces.append(new_interfaces)

    def add_commands(self):
        self.clean_interfaces.append("end")
        self.clean_interfaces.append("wr me")
        self.clean_interfaces.append("logo")
        self.clean_interfaces.append("y")

    def show_interfaces(self):
        for line in self.clean_interfaces:
            print(line)

    def generator(self):
        self.string_cleaner()
        self.file_spliter()
        self.make_strings()
        self.add_commands()
        return self.clean_interfaces
