import argparse
from .youtube_utilities import download
from .redirects import trace
from .ssl_utilities import check_ssl_expiry
import sys

import os

def main():
    # Setting up Main Argument Parser
    main_parser = argparse.ArgumentParser(description="A set of python web utility scripts")
    main_parser.add_argument("-v",'--version', action='version', version='kuws V0.0.1')

    # Setting up the main subparser
    subparsers = main_parser.add_subparsers(help="Available commands found below, for more info on a command use: python main.py <command> -h")


    """Code below handles 'redirects' command in the main script
    i.e. >python command_line_utility.py redirects or kuws redirects
    """
    redirects_parser = subparsers.add_parser('redirects',
        help='Allows you to trace redirects and get other information')

    redirects_parser.add_argument('-u', "--url", 
        required=True, help='usage: kuws redirects -u <url>; Lets you see the trace for a url', nargs='?', dest="trace_url")

    """Code below handles 'ssl' command in the main script
    i.e. >python command_line_utility.py ssl or kuws ssl
    """
    redirects_parser = subparsers.add_parser('ssl',
        help='Allows you to see ssl information for provided hostname')

    redirects_parser.add_argument('-u', "--hostname", type=str,
        required=True, help='usage: kuws ssl -u <url>; input hostname to use with other arguments', nargs='?', dest="ssl_url")

    redirects_parser.add_argument('-e', "--expiry", 
        required=False, nargs="?", default=False, type=bool, help='usage: kuws ssl -u <url> -e=True; input hostname to use with other arguments', dest="ssl_expiry")
        
    

    # Print help if no argument is provided
    if len(sys.argv)==1:
        main_parser.print_help()

    """
    ========================================================================
                              Argument parsing                              
    ========================================================================
    """
    # Obligatory argument parsing, setting arguments to args for later use
    args = main_parser.parse_args()

    try:
        # if args.trace_url:
        #     trace(args.trace_url, print_response=True)
        if args.ssl_expiry:
            print(check_ssl_expiry(args.ssl_url))
    except AttributeError: #For some ungodly reason argparse throws a hissy fit for daring to check namespace variables
        pass
    except Exception as identifier:
        print("Exception in URL trace with error: {}".format(identifier))


    # ================================= Commenting out youtube subparsing code until pytube is fixed on windows ================================= #

    # """Code below handles 'youtube' command in the main script
    # i.e. >python main.py youtube
    # """
    # youtube_parser = subparsers.add_parser('youtube', argument_default='-m',
    #     help='Allows you to interact with youtube videos')
    # youtube_parser.add_argument('-d', "--download", 
    #     help='usage: python main.py youtube -d <url>; Lets you download a specified youtube video', nargs='?', dest="download_url")

    # youtube_parser.add_argument('-p', "--path", default=".",
    #     help='usage: python main.py youtube -d <url> -p /downloads; Lets you set a path to download', nargs='?', dest="download_path")    

    # #TODO: Write youtube parsing download parsing properly
    # try:
    #     if (args.download_url and not args.download_path): # If no -p was specified
    #         print("video will be downloaded to script source folder: {}".format(os.getcwd()))
    #         download(args.download_url[0], '.')
    #     else:
    #         print("video will be downloaded to specified directory: {}".format(args.download_path[0]))
    #         download(args.download_url[0], args.download_path[0])
    # except AttributeError: #For some ungodly reason argparse throws a hissy fit for daring to check namespace variables
    #     pass
    # except Exception as identifier:
    #     print("exception in download path with error: {}".format(identifier))