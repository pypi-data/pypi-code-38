import sys
from multiprocessing import Pool

import argparse

from ucca.ioutil import get_passages_with_progress_bar, external_write_mode
from ucca.normalization import normalize
from ucca.validation import validate


class Validator:
    def __init__(self, normalization=False, extra=False, linkage=True, multigraph=False, strict=False):
        self.normalization = normalization
        self.extra = extra
        self.linkage = linkage
        self.multigraph = multigraph
        self.strict = strict

    def validate_passage(self, passage):
        if self.normalization:
            normalize(passage, extra=self.extra)
        errors = list(validate(passage, linkage=self.linkage, multigraph=self.multigraph))
        passage_id = passage.ID
        user_id = passage.attrib.get("userID")
        if user_id:
            passage_id += " " + user_id
        task_id = passage.attrib.get("annotationID")
        if task_id:
            passage_id += " " + task_id
        if self.strict:
            print_errors(passage_id, errors)
        return passage_id, errors


def main(args):
    validator = Validator(args.normalize, args.extra, linkage=args.linkage, multigraph=args.multigraph,
                          strict=args.strict)
    with Pool(10) as pool:
        errors = pool.map(validator.validate_passage,
                          get_passages_with_progress_bar(args.filenames, desc="Validating", converters={}))
    errors = dict((k, v) for k, v in errors if v)
    if errors:
        if not args.strict:
            id_len = max(map(len, errors))
            for passage_id, es in sorted(errors.items()):
                print_errors(passage_id, es, id_len)
        sys.exit(1)
    else:
        print("No errors found.")


def print_errors(passage_id, errors, id_len=None):
    for i, e in enumerate(errors):
        with external_write_mode():
            print("%-*s|%s" % (id_len or len(passage_id), "" if i else passage_id, e), flush=True)


def check_args(parser, args):
    if args.extra and not args.normalize:
        parser.error("Cannot specify --extra without --normalize")
    return args


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Validate UCCA passages")
    argparser.add_argument("filenames", nargs="+", help="files or directories to validate")
    argparser.add_argument("-S", "--strict", action="store_true", help="fail as soon as a violation is found")
    argparser.add_argument("-n", "--normalize", action="store_true", help="normalize before validation")
    argparser.add_argument("-e", "--extra", action="store_true", help="extra normalization rules")
    argparser.add_argument("--no-linkage", dest="linkage", action="store_false", help="skip linkage validations")
    argparser.add_argument("--multigraph", action="store_true", help="allow multiple edges with the same parent+child")
    main(check_args(argparser, argparser.parse_args()))
