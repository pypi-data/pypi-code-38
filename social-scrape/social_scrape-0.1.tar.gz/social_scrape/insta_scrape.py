import re
import os

import requests
from bs4 import BeautifulSoup


class InstaScrape(object):

    def __init__(self, user):
        self.user = user
        url = f"https://www.instagram.com/{user}/"

        html = requests.get(url).text

        self.soup = BeautifulSoup(html, features="html.parser")

    def get_insta_info(self):
        desc = self.soup.find('meta', property="og:description")
        # you may need to change the regex pattern to deal with 1000 = 1k or, 1m etc
        return re.findall(pattern="([0-9]+)\sFollowers,\s([0-9]+)\sFollowing,\s([0-9]+)\sPosts", string=desc["content"])[0]

    def save_prof_pic(self, output_dir=""):
        img = self.soup.find('meta', property="og:image")

        image = requests.get(img["content"]).content

        with open(os.path.join(output_dir, f"{self.user}.jpg"), "wb") as f:
            f.write(image)


