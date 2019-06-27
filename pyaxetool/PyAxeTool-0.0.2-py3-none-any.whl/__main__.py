#================================================
# Parse command lines
#================================================
import argparse
from . import MD5

def parseArgs():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='SubCommand')
    MD5.initArgs(subparsers)

    args = parser.parse_args()
    if args.SubCommand is None:  # 目前的argparser不能识别子命令缺失的情况，因此需要手工判定
        parser.print_help()
        raise RuntimeError('命令行参数缺少子命令')
    return args
g_Args = parseArgs()

def main():
    if MD5.main(g_Args):
        return

main()
