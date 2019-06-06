import os

import requests
from bs4 import BeautifulSoup


class InstaScrape(object):

    def __init__(self, user):
        self.user = user
        url = f"https://www.instagram.com/{user}/"

        html = requests.get(url).text

        self.soup = BeautifulSoup(html, features="html.parser")

    def save_prof_pic(self, output_dir=""):
        img = self.soup.find('meta', property="og:image")

        image = requests.get(img["content"]).content

        with open(os.path.join(output_dir, f"{self.user}.jpg"), "wb") as f:
            f.write(image)
