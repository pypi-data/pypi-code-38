from .block import Block
import argparse
import sys

sys.argv[0] = 'blockcard'

parser = argparse.ArgumentParser(description='Blockcard tools')
parser.add_argument('-d', '--display', action='store_true', help='Display the .blk file specified by FILE')
parser.add_argument('-g', '--generate', action='store_true', help='Generate new block as child of FILE. If no FILE is specified, then starts a new chain.')
parser.add_argument('-c', '--check', action='store_true', help='Check that FILE\'s content hash and header hash are valid.')
parser.add_argument('-C', '--deep-check', action='store_true', help='Validate entire chain starting with FILE and working backwords.')
parser.add_argument('FILE', type=str, help='Target .blk file', nargs='?', default='')

args = parser.parse_args()

flags = [args.check, args.deep_check, args.display, args.generate]
if sum(flags) != 1:
    raise ValueError("Please specify exactly one option. Use blockcard -h for more details")

if args.display:
    if not args.FILE:
        raise ValueError("FILE required for --display")
    Block(block_path=args.FILE).print()
if args.generate:
    b = Block(parent_path=args.FILE)
    b.print()
    print('Saving block...')
    b.save()
if args.check:
    if not args.FILE:
        raise ValueError("FILE required for --check")
    b = Block(block_path=args.FILE)
    b.check(verbose=True)
    print("Block is valid.")
if args.deep_check:
    if not args.FILE:
        raise ValueError("FILE required for --deep-check")
    b = Block(block_path=args.FILE)
    b.deep_check(verbose=True)

