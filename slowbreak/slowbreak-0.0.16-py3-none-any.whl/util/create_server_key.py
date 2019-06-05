import sys
import subprocess

from argparse import ArgumentParser

def arg_parser():
    p = ArgumentParser(description="Invoke openssl to generate selfsigned SSL keys for server")
    p.add_argument("-k", "--key", default="key.pem", help="File name of the generated key (default: %(default)s)")
    p.add_argument("-c", "--cert", default="cert.pem", help="File name of the generated certificate (default: %(default)s)")

    return p

def run_openssl(key, cert):
    return subprocess.call(
        "openssl req -new -x509 -days 3650 -nodes -keyout".split() + 
        [key, "-out", cert]
    )

# openssl req -new -x509 -days 3650 -nodes -keyout key.pem -out cert.pem
def main(argv):
    args = arg_parser().parse_args(argv[1:])
    return run_openssl(args.key, args.cert)

if __name__ == '__main__':
    sys.exit( main(sys.argv) )