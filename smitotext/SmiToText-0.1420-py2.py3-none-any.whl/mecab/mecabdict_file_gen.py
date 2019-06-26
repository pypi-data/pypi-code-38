import argparse
from SmiToText.mecab.mecabDictGenerate import mecabDictGenerate
import os
import re
import sys

def mecabdict_file_gen(input, output, posTag='NNG', kind=''):
    mecabDictGen = mecabDictGenerate()
    mecabDictGen.mecab_dict_gen_from_file(input, output, posTag=posTag, kind=kind)


if __name__ == '__main__':

    parser = argparse.ArgumentParser( description="Mecab Dict Generator")
    parser.add_argument('--input', type=str, required=True, default='', help='Input File')
    parser.add_argument('--output', type=str, required=True, default='', help='Output File')
    parser.add_argument('--posTag', type=str, required=False, default='NNG', help='postTag NNG, VV etc...')
    parser.add_argument('--kind', type=str, required=False, default='', help='file description')

    args = parser.parse_args()

    if not args.input:
        print("input file is invalid!")
        exit(1)

    if not args.output:
        print("output file is invalid!")
        exit(1)

    input = str(args.input)
    output = str(args.output)
    posTag = str(args.posTag)
    kind = str(args.kind)


    mecabdict_file_gen(input, output, posTag, kind)
