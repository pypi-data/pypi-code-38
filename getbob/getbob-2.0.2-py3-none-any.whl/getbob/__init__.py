import requests
import json
import sys
import os
import argparse
from html.parser import HTMLParser

stable_url = "http://d.defold.com/stable/"
__version__ = "2.0.2"


def log(string, verbose=False):
    if verbose:
        print(string)


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stdout.write('Error: {}'.format(message))
        self.print_help()
        sys.exit(2)


class MyHTMLParser(HTMLParser):
    version_data = {}

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, raw_data):
        if "var model" in raw_data[:100]:
            data = raw_data[raw_data.find("{"):]
            data = data[:data.find(r"\n")]
            json_data = json.loads(data)
            for version in json_data["releases"]:
                self.version_data[version["tag"]] = version["sha1"]


def _get_version_map(url=stable_url, verbose=False):
    response = requests.get(url)
    if response.status_code == 200:
        parser = MyHTMLParser()
        parser.feed(str(response.content))
        return parser.version_data
    else:
        log("ERROR: Couldn't fetch version map HTML code: {}".format(response.status_code), verbose)
        return {}


def _get_latest_beta_sha():
    info = requests.get("http://d.defold.com/beta/info.json").json()
    return info["sha1"], info["version"]


def _get_latest_stable():
    info = requests.get("http://d.defold.com/stable/info.json").json()
    return info["sha1"], info["version"]


def download(version, output, verbose=False, overwrite=False, progress=False):
    sha = version

    if not output:
        print("ERROR: Output file required\n")
        return False
    elif not version:
        sha, version = _get_latest_beta_sha()
        log("INFO: Getting latest stable version: {}".format(version), verbose)

    elif len(version.split(".")) == 3:
        version_map = _get_version_map()
        try:
            sha = version_map[version]
        except KeyError:
            print("ERROR: Can't find version {} of bob, supply valid version\n".format(version))
            return False
    elif version == "beta":
        sha, version = _get_latest_beta_sha()
        log("INFO: Getting latest beta version: {}".format(version), verbose)

    return _download(sha, output, verbose, overwrite, progress)


def _download(sha, output, verbose=False, overwrite=False, progress=False):
    bob_url = "http://d.defold.com/archive/{}/bob/bob.jar".format(sha)
    if requests.head(bob_url).status_code > 400:
        print("ERROR: Can't find version {} of bob, supply valid version\n".format(sha), verbose)
        return False

    target_folder = os.path.dirname(os.path.realpath(output))
    log("INFO: Downloading to: {}".format(target_folder))
    if overwrite and os.path.exists(output):
        log("INFO: Overwriting file: {}".format(output), verbose)
        os.remove(output)
    elif not overwrite and os.path.exists(output):
        log("INFO: Bob already downloaded: {}".format(output), verbose)
        sys.exit(1)

    if not os.path.exists(target_folder):
        log("INFO: Creating directories: {}".format(target_folder), verbose)
        os.makedirs(target_folder, exist_ok=True)

    r = requests.get(bob_url, stream=True)
    with open(output, "wb") as f:
        log("INFO: Downloading new bob: {}".format(sha), verbose)
        total_size = int(r.headers.get('content-length', 0))
        if total_size:
            dl = 0
            for data in r.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)

                if progress:
                    # Progressbar
                    done = int(50 * dl / total_size)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
            if progress:
                sys.stdout.write("\n")
        else:
            f.write(r.content)
        log("INFO: Download completed", verbose)
    return True


def _cli_options():
    parser = MyParser(description="Commandline tool to download Defold's Bob")
    optional = parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")
    required.add_argument('-o', '--output', dest='output', help="File name of the output")
    optional.add_argument('-d', '--defold', dest='defold', nargs="?",
                          help="Which version to download, if not provided the latest stable will be used. "
                          "Either: sha1 string, version string (1.2.152) or 'beta'")
    optional.add_argument('-f', '--force', action='store_true', dest="force", help="Overwrite already downloaded bob")
    optional.add_argument('-np', '--no-progress', action='store_true', dest='no_progress', help="Print verbose output")
    optional.add_argument('--verbose', action='store_true', dest='verbose', help="Print verbose output")
    optional.add_argument('--version', action='version', version="getbob {}".format(__version__), help="Print getbob's version")
    parser._action_groups.append(optional)

    return parser


def _run_cli():
    parser = _cli_options()
    options = parser.parse_args()
    if not download(options.defold, options.output, options.verbose, options.force, not options.no_progress):
        parser.print_help()


def main():
    try:
        _run_cli()
    except KeyboardInterrupt:
        sys.exit()
    except:
        raise


if __name__ == '__main__':
    main()
