#!/usr/bin/env python3
import argparse
import shlex
from .prepuller import Prepuller


def standalone():
    args = parse_args()
    prepuller = Prepuller(args=args)
    prepuller.update_images_from_repo()
    prepuller.build_nodelist()
    prepuller.build_pod_specs()
    prepuller.clean_completed_pods()
    prepuller.run_pods()


def parse_args():
    """Parse command-line arguments"""
    desc = "Set up DaemonSets to prepull."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-d", "--debug", action="store_true",
                        help="enable debugging")
    parser.add_argument("-r", "--repo", "--repository",
                        help="Docker repository host")
    parser.add_argument("-o", "--owner", "--organization", "--org",
                        help="repository owner [lsstsqre]",
                        default="lsstsqre")
    parser.add_argument("-n", "--name",
                        help="repository name [sciplat-lab]",
                        default="sciplat-lab")
    parser.add_argument("-q", "--dailies", "--daily", "--quotidian", type=int,
                        help="# of daily builds to keep [3]",
                        default=3)
    parser.add_argument("-w", "--weeklies", "--weekly", type=int,
                        help="# of weekly builds to keep [2]",
                        default=2)
    parser.add_argument("-b", "--releases", "--release", type=int,
                        help="# of release builds to keep [1]",
                        default=1)
    parser.add_argument("-i", "--insecure", "--no-tls", "--no-ssl",
                        help="Do not use TLS to connect [False]",
                        action='store_true',
                        default=False)
    parser.add_argument("-l", "--list", "--list-images", "--image-list",
                        help=("Use supplied comma-separated list in" +
                              " addition to repo scan"))
    parser.add_argument("-p", "--port", help="Repository port [443 for" +
                        " secure, 80 for insecure]",
                        default=None)
    parser.add_argument("-s", "--sort", "--sort-field", "--sort-by",
                        help="Field to sort results by [name]",
                        default="name")
    parser.add_argument("--no-scan", action="store_true",
                        help="Do not do repo scan (only useful in" +
                        " conjunction with --list)")
    cmdstr = ("/bin/sh -c \"echo Prepuller run for $(hostname) complete at" +
              " $(date)\"")
    parser.add_argument("-c", "--command", help="Command to run when image" +
                        " is run as prepuller [%s]" % cmdstr, default=cmdstr)
    parser.add_argument("-t", "--timeout",
                        help=("Seconds allowed for process to complete " +
                              "(-1 for no timeout) [3300]"),
                        type=int,
                        default=3300)
    parser.add_argument("-u", "--uid",
                        help=("UID to run as [769]"),
                        type=int,
                        default=769)
    parser.add_argument("--namespace",
                        help=("Kubernetes namespace [namespace" +
                              " of container, or 'default' if not run " +
                              " inside kubernetes]"))
    parser.add_argument("--recommended",
                        help=("Pull image with tag 'recommended' [True]"),
                        type=bool,
                        default=True)
    results = parser.parse_args()
    results.path = ("/v2/repositories/" + results.owner + "/" +
                    results.name + "/tags/")
    if results.list:
        results.list = list(set(results.list.split(',')))
    if results.command:
        results.command = shlex.split(results.command)
    return results


if __name__ == "__main__":
    standalone()
