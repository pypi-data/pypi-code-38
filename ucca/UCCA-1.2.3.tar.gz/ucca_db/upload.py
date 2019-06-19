from argparse import ArgumentParser
from xml.etree.ElementTree import tostring

from ucca import convert
from ucca.ioutil import get_passages_with_progress_bar
from ucca_db.api import CONNECTION, write_to_db

desc = "Upload passages to old UCCA annotation app"


def upload_passage(xml_root, site_filename=None, verbose=False, **kwargs):
    decoded = tostring(xml_root).decode()
    if site_filename:
        with open(site_filename, "w", encoding="utf-8") as f:
            print(decoded, file=f)
        if verbose:
            print("Wrote '%s'" % site_filename)
    return write_to_db(xml=decoded, **kwargs)


def main(args):
    filenames = list(args.passages)
    if args.filenames:
        with open(args.filenames, encoding="utf-8") as f:
            filenames += list(filter(None, map(str.strip, f)))
    with open(args.out, "w", encoding="utf-8") as f:
        for passage in get_passages_with_progress_bar(filenames):
            out = upload_passage(convert.to_site(passage), verbose=args.verbose,
                                 site_filename=passage.ID + "_site_upload.xml" if args.write_site else None,
                                 db_name=args.db_name, host_name=args.host_name,
                                 new_pid=passage.ID, new_prid=args.project_id, username=args.username)
            print(passage.ID, out, file=f)
            if args.verbose:
                print("Uploaded passage %s with xid=%s" % (passage.ID, out))
    if CONNECTION is not None:
        CONNECTION.commit()
    print("Wrote '%s'" % args.out)


if __name__ == "__main__":
    argparser = ArgumentParser(description=desc)
    argparser.add_argument("passages", nargs="*", help="the corpus, given as xml/pickle file names")
    argparser.add_argument("-f", "--filenames", help="read input passages filenames from file rather than command line")
    argparser.add_argument("-d", "--db-name", default="work", help="database name")
    argparser.add_argument("-H", "--host-name", default="pgserver", help="host name")
    argparser.add_argument("-p", "--project-id", default="63", help="project ID")
    argparser.add_argument("-u", "--username", default="danielh", help="username")
    argparser.add_argument("-o", "--out", default="xids.txt", help="file to write created XML IDs to")
    argparser.add_argument("--write-site", action="store_true", help="write site format for debugging before upload")
    argparser.add_argument("-v", "--verbose", action="store_true", help="print tagged text for each passage")
    main(argparser.parse_args())
