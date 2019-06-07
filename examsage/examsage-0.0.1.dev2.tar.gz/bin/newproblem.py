#!/usr/bin/env python3

from examsage import Problem
from pathlib import Path
import sys, getopt

try:
    opts, args = getopt.getopt(sys.argv[1:],'hw',['overwrite'])
except getopt.GetoptError:
    print(r"new-problem.py [overwrite] <relative_path\name_of_problem>")
    print("getopt failed")
    sys.exit(2)

overwrite = False
for opt, arg in opts:
    if opt == '-h':
        print(r"new-problem.py [--overwrite] <relative_path\name_of_problem>")
        sys.exit()
    elif opt in ("-w", "--overwrite"):
        overwrite = True

try:
    problem_name = args[0]
except Exception:
    print(r"new-problem.py [--overwrite] <relative_path\name_of_problem>")
    sys.exit("Problem name required")

path  = Path.cwd() / problem_name
Problem.new(path, overwrite=overwrite)
