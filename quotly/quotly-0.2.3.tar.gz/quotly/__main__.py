import os
import argparse

from dotenv import load_dotenv

from quotly.QuotyBot import quoty_bot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='quotly command line interface')
    parser.add_argument('-r', '--run', action='store_true', help='Start quotly')
    parser.add_argument('-t', '--token', type=str, default=None, help='Set discord bot token')

    args = parser.parse_args()

    if args.token is not None:
        with open('.env', 'w') as cfg:
            cfg.write('TOKEN={0}'.format(args.token))

        print('> Token successfully stored!')
        exit(0)

    if args.run:
        load_dotenv('.env')

        # using token from .env file
        if os.path.exists('.env') and os.getenv('TOKEN'):
            quoty_bot.run(os.getenv('TOKEN'))
        else:
            print('> No discord bot token found!')
