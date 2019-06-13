#!/usr/bin/env python3
# https://stackoverflow.com/questions/5709616/whats-the-difference-between-these-two-python-shebangs


import adr_func
import sys

def main(args=None):
    config = adr_func.adr_config()
    # print output if run standalone
    for key,val in config.items():
        print(key,"=\"",val,"\"", sep='')

if __name__ == "__main__":
    main(args)
