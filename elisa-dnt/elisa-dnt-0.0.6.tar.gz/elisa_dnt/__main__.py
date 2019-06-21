# encoding: utf-8
# Created by chenghaomou at 2019-06-11
import argparse
import regex as re
from elisa_dnt.utils import *

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='DNT process script')

    parser.add_argument('p_step', type=str, choices=['pre', 'post'],
                        help="Parameter for choosing between preprocess or postprocess")
    parser.add_argument('p_scheme', type=str, choices=['del', 'sub'],
                        help="Parameter for scheme")

    parser.add_argument('--fa_dnt_src', type=str,
                        help='[Post]File path to the dnt source file')
    parser.add_argument('--fa_dnt_ini', type=str,
                        help="[Post]File path to the dnt conf file")
    parser.add_argument('--fa_output', type=str,
                        help="[Post]File path to the output file")

    parser.add_argument('--fb_src', type=str,
                        help='[Pre]File path to the source file')
    parser.add_argument('--fb_src_output', type=str,
                        help='[Pre]File path to the source output file')
    parser.add_argument('--fb_ini_output', type=str,
                        help='[Pre]File path to the source ini file')
    parser.add_argument('--fb_tgt', type=str, required=False,
                        help='[Pre]File path to the target file')
    parser.add_argument('--pb_cross', dest='pb_cross', default=False, action='store_true',
                        help='[Pre]Parameter for whether use reference target file for regex extraction')
    parser.add_argument('--fb_visual', type=str,
                        help="[Pre]File path to visualization html file")

    args = parser.parse_args()
    print(args)

    scheme = args.p_scheme

    if args.p_step == "post":
        restore(args.fa_dnt_src, args.fa_dnt_ini, args.fa_output, args.p_scheme)
        exit(0)

    RULES = {key: re.compile(value) for key, value in rules[args.p_scheme].items()}
    RULES["comb"] = re.compile("(" + "|".join(rules[args.p_scheme].values()) + ")+")

    if args.fb_visual:
        with open(args.fb_visual, "w") as o:
            o.write("""
                <link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro&display=swap&subset=cyrillic,cyrillic-ext,greek,greek-ext,latin-ext,vietnamese" rel="stylesheet">
                <style>
                    html,body{
                        font-family: 'Source Sans Pro', sans-serif;
                    }
                    """ + "\n".join([".%s {%s}" % (key, value) for key, value in options["colors"].items()]) + """
                </style>
                """)

    path = args.fb_src

    split(args.fb_src, args.fb_src_output, args.fb_ini_output, scheme=args.p_scheme,
          ref=args.fb_tgt if args.p_scheme == "sub" and args.pb_cross else "", RULES=RULES)

    if args.fb_visual:
        if args.fb_tgt == "":
            for line in open(path):
                matches = find(line, RULES)
                if matches:
                    res = visual(line, matches, options, RULES)
                    with open(args.fb_visual[0], "a+") as o:
                        o.write(f"<p>{res}</p>" + "\n")
        else:
            src_lines, tgt_lines = open(path).readlines(), open(args.fb_tgt).readlines()
            assert len(src_lines) == len(tgt_lines)
            for src_line, tgt_line in zip(src_lines, tgt_lines):
                src_matches = find(src_line, RULES)
                tgt_matches = find(tgt_line, RULES)

                src_matches_text = [src_line[m.start(0):m.end(0)] for m in src_matches]
                tgt_matches_text = [tgt_line[m.start(0):m.end(0)] for m in tgt_matches]

                x_matches = list(set(src_matches_text).intersection(set(tgt_matches_text)))

                x_src_matches = [m for m in src_matches if
                                 src_line[m.start(0):m.end(0)] in x_matches] if args.pb_cross else src_matches
                x_tgt_matches = [m for m in tgt_matches if
                                 tgt_line[m.start(0):m.end(0)] in x_matches] if args.pb_cross else tgt_matches

                if x_matches:
                    res = visual(src_line, x_src_matches, options, RULES)
                    with open(args.fb_visual[0], "a+") as o:
                        o.write(f"<p>{res}</p>" + "\n")

                    res = visual(tgt_line, x_tgt_matches, options, RULES)
                    with open(args.fb_visual[0], "a+") as o:
                        o.write(f"<p>{res}</p>" + "\n")
