#!/usr/bin/python3

import sys
from Modules.Azure import Azure
from Modules.GCP import GCP

def usage():
    print("Project made to study Python")

def switch(position):
    az = Azure()
    gcp = GCP()
    try:
        functions = {"-gcp":gcp.create_vm,
                    "-az":az.create_vm,
                    "-h":usage}
        return functions[position]
    except Exception as e:
        print("Invalid argument: {0}".format(e))
try:
    switch(sys.argv[1])()
except Exception as e:
    print("The quantity of arguments is invalid.")


# if len(sys.argv) == 1 or sys.argv[1] == "-h":
#     usage()
# elif sys.argv[1] == "-gcp":
#     gcp()
# elif sys.argv[1] == "-az":
#     azure()
# else:
#     print("Invalid argument!")

