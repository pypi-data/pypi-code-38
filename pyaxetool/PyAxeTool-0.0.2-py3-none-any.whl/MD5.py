import glob
from PyAxe import AHash

def isGlobPattern(s):
    return ('?' in s) or ('*' in s)

def initArgs(subparsers):
    subparser = subparsers.add_parser('MD5OfFile', help='显示文件MD5')
    subparser.add_argument('Pattern', help='通配符')

    subparser = subparsers.add_parser('MD5OfDir', help='显示目录MD5')
    subparser.add_argument('DirPath', help='目录路径')

    subparser = subparsers.add_parser('MD5OfStr', help='显示字符串MD5')
    subparser.add_argument('Str', help='字符串')

def MD5OfFile(pattern):
    if isGlobPattern(pattern):
        for filePath in glob.glob(pattern):
            print(filePath + ': ' + AHash.getMD5OfFile(filePath))
    else:
        print(AHash.getMD5OfFile(pattern))

def MD5OfDir(dirPath):
        print(AHash.getMD5OfDir(dirPath))

def MD5OfStr(s):
        print(AHash.getMD5OfStr(s))

def main(args):
    if args.SubCommand == 'MD5OfFile':
        MD5OfFile(args.Pattern)
    elif args.SubCommand == 'MD5OfDir':
        MD5OfDir(args.DirPath)
    elif args.SubCommand == 'MD5OfStr':
        MD5OfStr(args.Str)
    else:
        return False
    return True