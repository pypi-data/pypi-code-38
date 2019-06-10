#!/usr/bin/env python

__author__ = 'david.johnnes@gmail.com'


class APGenRobot(object):

    def __init__(self, filename, parent_name):
        """ """
        self.filename = filename  # filename must be a .txt file
        self.parent_name = parent_name
        self.base_list = []
        self.splited_list = []
        self.clean_interfaces = []

    def string_cleaner(self):
        with open(self.filename) as file:
            for line in file:
                line = line.strip()

                if "-AP-" in line:
                    line = line.replace("|", "")  # remove the |
                    self.base_list.append(line)

    def file_spliter(self):
        for line in self.base_list:
            splited_line = line.split()

            if len(splited_line) == 3:
                self.splited_list.append(splited_line)

    def make_strings(self):
        for line in self.splited_list:
            hostname = line[1]
            local_port = "interface G0"
            parent_port = line[0]
            interface = [hostname, "config t", local_port,
                         "description {0}({1})".format(self.parent_name, parent_port), "end", "wr me", "exit"]
            self.clean_interfaces.append(interface)

    def show_interfaces(self):
        for line in self.clean_interfaces:
            print(line)

    def generator(self):
        self.string_cleaner()
        self.file_spliter()
        self.make_strings()
        return self.clean_interfaces
