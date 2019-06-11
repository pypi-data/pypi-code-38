#!/usr/bin/env python
import sys
import argparse

import npu_compiler.compiler
from npu_compiler.config import Config
from npu_compiler.ops_dict import OpsDict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="gxnpuc", description="NPU Compiler")
    parser.add_argument("-V", "--version", action="version", version="gxnpuc %s" % Config.VERSION)
    parser.add_argument("-L", "--list", action="store_true", help="list supported ops")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbosely list the processed ops")
    parser.add_argument("-m", "--meminfo", action="store_true", help="verbosely list memory info of ops")
    parser.add_argument("-c", "--cmd", nargs="+", help="use command line configuration")
    parser.add_argument("config_filename", nargs="?", default=sys.stdin, help="config file")
    args = parser.parse_args()
    if args.list:
        print("Supported OPs:")
        ops = OpsDict.get_tf_ops()
        ops.sort()
        for op in ops:
            print("\t -  %s" % op)
        sys.exit()
    if args.cmd:
        config_para = {"VERBOSE": args.verbose, "MEMINFO": args.meminfo}
        Config.config_from_cmd(args.cmd[0], config_para)
        npu_compiler.compiler.run()
        sys.exit()
    elif args.config_filename:
        config_para = {"VERBOSE": args.verbose, "MEMINFO": args.meminfo}
        Config.config_from_file(args.config_filename, config_para)
        npu_compiler.compiler.run()
        sys.exit()
    else:
        parser.print_help()

