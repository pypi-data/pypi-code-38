import os

import requests
from bs4 import BeautifulSoup


class TwitScrape(object):

    def __init__(self, user):
        self.user = user
        url = f"https://twitter.com/{user}/"

        html = requests.get(url).text

        self.soup = BeautifulSoup(html, features="html.parser")

    @property
    def followers(self):
        return self.soup.find(class_='ProfileNav-item--followers').find(class_="ProfileNav-value")['data-count']

    def save_prof_pic(self, output_dir=""):
        img = self.soup.find(class_="ProfileAvatar-image")['src']

        image = requests.get(img).content

        with open(os.path.join(output_dir, f"{self.user}.jpg"), "wb") as f:
            f.write(image)

