import os

from quotly.QuotyBot import quoty_bot

if __name__ == "__main__":
    quoty_bot.run(os.getenv('TOKEN'))
