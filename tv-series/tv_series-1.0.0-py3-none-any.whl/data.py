import json
import logging
import os
import re
import shutil
from datetime import date, datetime

import xdg

from .tvdb import tvdb

logger = logging.getLogger(__name__)

DATABASE_PATH = f"{xdg.XDG_DATA_HOME}/tv.series.json"


class Series:
    CATEGORIES = ["active", "waiting", "default", "archived"]

    def __init__(self, id, name, status, episodes, seen, category, language):
        self.id = id
        self.name = name
        self.status = status
        self.episodes = episodes
        self.seen = seen
        self.category = category
        self.language = language

    def __lt__(self, other):
        if not isinstance(other, Series):
            raise TypeError()

        if self.category == other.category:
            return self.name < other.name
        else:
            return Series.CATEGORIES.index(self.category) < Series.CATEGORIES.index(
                other.category
            )

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if value not in Series.CATEGORIES:
            raise ValueError()
        self._category = value

    def synchronize(self, output_diff=True):
        series, episodes = tvdb.query_series(self.id, self.language)
        new_episodes = sorted(
            [
                Episode(
                    season=int(episode["airedSeason"]),
                    episode=int(episode["airedEpisodeNumber"]),
                    aired=datetime.strptime(episode["firstAired"], "%Y-%m-%d").date()
                    if episode["firstAired"]
                    else None,
                )
                for episode in episodes
            ]
        )

        if series["seriesName"] is None:
            raise ValueError(
                "Series name is None, expected string. Perhaps wrong language?"
            )

        if output_diff:
            if self.id != series["id"]:
                print(f"  ID changed from '{self.id}' to '{series['id']}'")
            if self.name != series["seriesName"]:
                print(f"  Name changed from '{self.name}' to '{series['seriesName']}'")
            if self.status != series["status"]:
                print(f"  Status changed from '{self.status}' to '{series['status']}'")
            for episode in self.episodes:
                for new_episode in new_episodes:
                    if episode == new_episode:
                        if episode.aired != new_episode.aired:
                            print(
                                f"  {episode} air date changed from {episode.aired} to "
                                f"{new_episode.aired}"
                            )
                        break
                else:
                    print(f"  {episode} ({episode.aired}) removed")
            for new_episode in new_episodes:
                if new_episode not in self.episodes:
                    print(f"  {new_episode} ({new_episode.aired}) added")

        self.id = series["id"]
        self.name = series["seriesName"]
        self.status = series["status"]
        self.episodes = new_episodes

    def find_available(self):
        if self.seen is None:
            seen_episode = Episode(0, 0)
        else:
            seen_episode = Episode(*parse_episode(self.seen))
        available = [
            e
            for e in self.episodes
            if e > seen_episode and e.aired and e.aired <= date.today()
        ]
        if not available:
            return "-"
        else:
            return f"{available[0]} ({len(available)} total)"

    def next_on_air(self):
        for e in self.episodes:
            if e.aired and e.aired >= date.today():
                return f"{e} ({e.aired})"
        return "-"

    @staticmethod
    def new(id, language):
        series = Series(id, "", "", [], None, "default", language)
        series.synchronize(output_diff=False)
        return series


class Episode:
    def __init__(self, season, episode, aired=None):
        if not isinstance(season, int):
            raise TypeError()
        if not isinstance(episode, int):
            raise TypeError()
        if aired is not None and not isinstance(aired, date):
            raise TypeError()

        self.season = season
        self.episode = episode
        self.aired = aired

    def __str__(self):
        return f"S{self.season:02d}E{self.episode:02d}"

    def __eq__(self, other):
        if not isinstance(other, Episode):
            return False

        return self.season == other.season and self.episode == other.episode

    def __lt__(self, other):
        if not isinstance(other, Episode):
            raise TypeError()

        if self.season == other.season:
            return self.episode < other.episode
        else:
            return self.season < other.season


def initialize():
    if os.path.exists(DATABASE_PATH):
        logger.warning(f"{DATABASE_PATH} already exists, not overwriting")
        return
    with open(DATABASE_PATH, "w") as f:
        json.dump([], f)


def load():
    with open(DATABASE_PATH) as f:
        return [
            Series(
                s["id"],
                s["name"],
                s["status"],
                [
                    Episode(
                        season=parse_episode(e["episode"])[0],
                        episode=parse_episode(e["episode"])[1],
                        aired=datetime.strptime(e["aired"], "%Y-%m-%d").date()
                        if e["aired"]
                        else None,
                    )
                    for e in s["episodes"]
                ],
                s["seen"],
                s["category"],
                s["language"],
            )
            for s in json.loads(f.read())
        ]


def save(series_list):
    series_list = sorted(series_list)
    series_dict = [
        {
            "id": s.id,
            "name": s.name,
            "status": s.status,
            "episodes": [
                {
                    "episode": str(e),
                    "aired": e.aired.strftime("%Y-%m-%d") if e.aired else None,
                }
                for e in s.episodes
            ],
            "seen": s.seen,
            "category": s.category,
            "language": s.language,
        }
        for s in series_list
    ]
    series_serialized = json.dumps(series_dict, indent=4, sort_keys=True)
    shutil.copyfile(DATABASE_PATH, f"{DATABASE_PATH}.backup")
    with open(DATABASE_PATH, "w") as f:
        f.write(series_serialized)


def parse_episode(episode_number):
    m = re.match(r"S(\d+)E(\d+)", episode_number.upper())
    return int(m.group(1)), int(m.group(2))
