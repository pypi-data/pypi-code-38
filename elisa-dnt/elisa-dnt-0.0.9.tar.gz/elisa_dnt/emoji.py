# encoding: utf-8
# Created by chenghaomou at 2019-06-27

from bs4 import BeautifulSoup
import urllib3
import argparse


def get_emojis(url: str = "http://unicode.org/emoji/charts-12.0/full-emoji-list.html",
               output: str = "emojis.ini") -> None:
    """
    Parse the official website for all emojis and write them to a file.

    :param url: Official unicode website for emoji list.

    :param output: Output file for the list of emojis.

    :return: None.

    """
    req = urllib3.PoolManager()
    res = req.request('GET', url)
    soup = BeautifulSoup(res.data, "html.parser")
    emojis = set('🦰🦱🦳🦲🏻🏼🏽🏾🏿')
    for img in soup.findAll('img', alt=True):
        if len(img['alt']) == 1:
            emojis.add('{}'.format(img['alt']))

    with open(output, "w") as output:
        output.write('\n'.join(emojis))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Emoji list retriever from unicode website')

    parser.add_argument('--url', type=str, default="http://unicode.org/emoji/charts-12.0/full-emoji-list.html",
                        help='Unicode website for emoji')
    parser.add_argument('--output', type=str, default='emojis.ini',
                        help='Output file')

    args = parser.parse_args()

    get_emojis(args.url, args.output)