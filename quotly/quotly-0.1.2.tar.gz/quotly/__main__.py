import os

from quotly.QuotyBot import quoty_bot

if __name__ == "__main__":
    if os.getenv('TOKEN'):
        quoty_bot.run(os.getenv('TOKEN'))
    else:
        print('> Missing \'TOKEN\' .env!')
