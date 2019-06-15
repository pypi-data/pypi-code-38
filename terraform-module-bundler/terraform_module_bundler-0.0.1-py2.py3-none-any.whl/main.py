import argparse
from terraform_module_bundler.bundle import Bundle


def __get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "bundle"
    )
    parser.add_argument(
        "--directory_path",
        required=False
    )
    return parser.parse_args()


def main():
    parser = __get_args()
    bundle = Bundle(
        directory_path=parser.directory_path
    )
    bundle.zip()




