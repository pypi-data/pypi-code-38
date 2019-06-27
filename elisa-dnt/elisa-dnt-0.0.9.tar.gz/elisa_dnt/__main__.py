# encoding: utf-8
# Created by chenghaomou at 2019-06-11
import argparse
import regex as re
from elisa_dnt.utils import *

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='DNT process script')

    parser.add_argument('step', type=str, choices=['pre', 'post'],
                        help="Parameter for choosing between preprocess or postprocess")
    parser.add_argument('scheme', type=str, choices=['del', 'sub'],
                        help="Parameter for scheme")

    parser.add_argument('--dnt_src', type=str,
                        help='[Post]File path to the dnt source file')
    parser.add_argument('--dnt_ini', type=str,
                        help="[Post]File path to the dnt conf file")
    parser.add_argument('--output', type=str,
                        help="[Post]File path to the output file")

    parser.add_argument('--src', type=str,
                        help='[Pre]File path to the source file')
    parser.add_argument('--src_output', type=str,
                        help='[Pre]File path to the source output file')
    parser.add_argument('--ini_output', type=str,
                        help='[Pre]File path to the source ini file')
    parser.add_argument('--tgt', type=str, required=False,
                        help='[Pre]File path to the target file')
    parser.add_argument('--cross', dest='pb_cross', default=False, action='store_true',
                        help='[Pre]Parameter for whether use reference target file for regex extraction')
    parser.add_argument('--visual', type=str,
                        help="[Pre]File path to visualization html file")

    args = parser.parse_args()
    print(args)

    scheme = args.scheme
    
    rules = load_rules(scheme=scheme)
    options = generate_options()

    if args.step == "post":
        restore(args.dnt_src, args.dnt_ini, args.output, args.scheme)
        exit(0)

    if args.visual:
        with open(args.visual, "w") as o:
            o.write("""
            <html>
                <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                <link href="https://fonts.googleapis.com/css?family=Open+Sans&display=swap&subset=cyrillic,cyrillic-ext,greek,greek-ext,latin-ext,vietnamese" rel="stylesheet">
                <style>
                    html,body{
                        font-family: 'Open Sans', sans-serif;
                    }
                    """ + "\n".join([".%s {%s}" % (key, value) for key, value in options["colors"].items()]) + """
                </style>
                <head>
                <body>
                """)

    path = args.src

    split(args.src, args.src_output, args.ini_output, scheme=args.scheme,
          ref=args.tgt if args.scheme == "sub" and args.pb_cross else "", rules=rules)

    if args.visual:
        if args.tgt == "":
            for line in open(path):
                matches = find(line, rules)
                if matches:
                    res = visual(line, matches, options, rules)
                    with open(args.visual, "a+") as o:
                        o.write(f"<p>{res}</p>" + "\n")
        else:
            src_lines, tgt_lines = open(path).readlines(), open(args.tgt).readlines()
            assert len(src_lines) == len(tgt_lines)
            for src_line, tgt_line in zip(src_lines, tgt_lines):
                src_matches = find(src_line, rules)
                tgt_matches = find(tgt_line, rules)

                src_matches_text = [src_line[m.start:m.end] for m in src_matches]
                tgt_matches_text = [tgt_line[m.start:m.end] for m in tgt_matches]

                x_matches = list(set(src_matches_text).intersection(set(tgt_matches_text)))

                x_src_matches = [m for m in src_matches if
                                 src_line[m.start:m.end] in x_matches] if args.pb_cross else src_matches
                x_tgt_matches = [m for m in tgt_matches if
                                 tgt_line[m.start:m.end] in x_matches] if args.pb_cross else tgt_matches

                if x_matches:
                    res = visual(src_line, x_src_matches, options, rules)
                    with open(args.visual, "a+") as o:
                        o.write(f"<p>{res}</p>" + "\n")

                    res = visual(tgt_line, x_tgt_matches, options, rules)
                    with open(args.visual, "a+") as o:
                        o.write(f"<p>{res}</p>" + "\n")

            with open(args.visual, "a+") as o:
                o.write('</body></html>')