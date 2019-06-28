import os
import argparse

from quotly.QuotyBot import quoty_bot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='quotly command line interface')
    parser.add_argument('-r', '--run', action='store_true', help='Start quotly')
    parser.add_argument('-t', '--token', type=str, default=None, help='Set discord bot token')

    args = parser.parse_args()

    token = None
    if args.token is not None:
        with open('.env', 'w') as cfg:
            cfg.write('TOKEN={0}'.format(args.token))

        print('> Token successfully stored!')
        exit(0)

    if args.run:

        # using token from .env file
        if os.path.exists('.env') and os.getenv('TOKEN') and token is None:
            token = os.getenv('TOKEN')

        if token is not None:
            quoty_bot.run(token)
        else:
            print('> No discord bot token found!')
