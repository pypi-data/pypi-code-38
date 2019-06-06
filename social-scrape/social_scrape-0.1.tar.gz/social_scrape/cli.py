import argparse

from . import InstaScrape, TwitScrape


def get_args():

    parser = argparse.ArgumentParser(description="Commandline tool for scraping Instagram and twitter")

    subparsers = parser.add_subparsers(help="Submodule of scraping to use", dest="mode")

    insta_parser = subparsers.add_parser('insta', help="Mode Insta: Scrapes Instagram for a given user")
    insta_parser.add_argument('-u', '--user', required=True, type=str, help="Instagram username to get information from")
    insta_parser.add_argument('-o', '--output-dir', required=True, type=str, help="Output directory to save profile picture to")

    twitter_parser = subparsers.add_parser('twit', help="Mode Twit: Scrapes Twitter for a given user")
    twitter_parser.add_argument('-u', '--user', required=True, type=str, help="Twitter handle to get information from")
    twitter_parser.add_argument('-o', '--output-dir', required=True, type=str, help="Output directory to save profile picture to")
    twitter_parser.add_argument('-f', '--followers', required=False, action='store_true', help="Whether to print the follower count")

    return parser.parse_args()


def main():
    args = get_args()

    if args.mode == 'twit':
        twitter = TwitScrape(args.user)
        twitter.save_prof_pic(args.output_dir)
        if args.followers:
            print(f"{args.user} has {twitter.followers} followers")

    elif args.mode == 'insta':
        insta = InstaScrape(args.user)
        insta.save_prof_pic(args.output_dir)

    else:
        raise Exception('Unsupported mode')


if __name__ == "__main__":
    main()
