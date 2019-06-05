'''
Copyright 2019 Jacques Supcik

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

-----------------------------------------------------------------------------
Purpose: Dataclass for groups
Filename: groople/group.py
Created Date: 2019-03-31
Author: Jacques Supcik
-----------------------------------------------------------------------------
'''

import re
from dataclasses import dataclass, field


# pylint: disable=invalid-name
@dataclass
class Group:
    """ Group class """
    id: int
    label: str
    max_quota: int
    date_fr: str = ""
    date_de: str = ""
    order: int = 0
    attributes: dict = field(default_factory=dict)
    days: list = field(default_factory=list)
    dow_key = ['lu', 'ma', 'me', 'je', 've', 'sa', 'di']
    dow_fr = ['lundi', 'mardi', 'mercredi',
              'jeudi', 'vendredi', 'samedi', 'dimanche']
    dow_de = ['Montag', 'Dienstag', 'Mittwoch',
              'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

    @staticmethod
    def parse_day(d, schedule):
        """ Parses a day """
        res = {
            "order": 13 * 32,
            "dow": None,
            "day": None,
            "month": None,
            "schedule": schedule,
        }
        c = d.find(',')
        if c > 0:
            res["period"] = d[c + 1:].strip()
            d = d[:c].strip()
        else:
            res["period"] = None

        m = re.match(r'(\w{2})\s(\d+)[.-](\d+)(?:-\d{2,4})?$', d)
        if m:
            dow, day, month = m.group(1), m.group(2), m.group(3)
            res["dow"] = dow
            res["day"] = int(day)
            res["month"] = int(month)
            res["order"] = int(month) * 32 + int(day)
            dowi = Group.dow_key.index(dow.lower())
            if dowi >= 0:
                res["date_fr"] = f"{Group.dow_fr[dowi]} {day}.{month}"
                res["date_de"] = f"{Group.dow_de[dowi]} {day}.{month}"
            else:
                res["date_fr"] = f"{dow} {day}.{month}"
                res["date_de"] = res["date_fr"]
        else:
            res["date_fr"] = re.sub(r'\s+', ' ', d.strip())
            res["date_de"] = res["date_fr"]

        if schedule is not None:
            m = re.search(r'(\d{1,2})[h:.-](\d{1,2})', schedule)
            if m:
                res["order"] += (int(m.group(1)) * 60 +
                                 int(m.group(2))) / (24 * 60)

        return res

    @staticmethod
    def unique(l):
        """ Filters duplicate """
        seen = set()
        res = list()
        for i in l:
            if i not in seen:
                res.append(i)
                seen.add(i)
        return res

    def sanitize(self):
        """ Sanitize """
        l = self.label.strip()
        if 'schedule' in self.attributes:  # pylint: disable=unsupported-membership-test
            s = self.attributes['schedule'].strip(
            )  # pylint: disable=unsubscriptable-object
            if not l.endswith(s):
                raise Exception(
                    f"Inconsistent Label : {l} does not end with {s}")
            l = l[:-len(s)].strip()
        else:
            s = None

        days = [Group.parse_day(i, s) for i in l.split('|')]
        date_fr = " + ".join(Group.unique([i["date_fr"] for i in days]))
        date_de = " + ".join(Group.unique([i["date_de"] for i in days]))
        self.order = min([i["order"] for i in days])

        if s is not None:
            date_fr += f" {s}"
            date_de += f" {s}"

        self.days = days
        self.date_fr = date_fr
        self.date_de = date_de

    def __str__(self):
        return f'{self.label}'
