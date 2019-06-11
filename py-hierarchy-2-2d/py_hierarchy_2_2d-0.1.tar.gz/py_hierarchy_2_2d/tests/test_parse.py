#!/usr/bin/env python
from py_hierarchy_2_2d import *
from py_hierarchy_2_2d import __version__ as v
from py_hierarchy_2_2d.tests.utils import my_tabulate, get_project_dir, slurp
import xmltodict
import json
from os import path

# dev dependency only
import toml

# save some keystrokes
mt = my_tabulate


def test_version():
    "Tests the verion in __init__ against the version in pyproject.toml."
    pyproject = toml.load(path.join(get_project_dir(), "pyproject.toml"))
    pyproject_version = pyproject["tool"]["poetry"]["version"]
    assert v == pyproject_version, "version doesn't match pyproject verison?"


def test_airplanes():
    xml = slurp(path.join(get_project_dir(), "sample-data/airplanes.xml"))

    actual = mt(parse(xml), no_print=True)
    expected = """
parent_path    path              tag     attributes    value
-------------  ----------------  ------  ------------  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
/              /planes/          planes  {}            {}
/planes/       /planes/plane/0/  plane   {}            {'make': 'Cessna', 'year': '1977', 'model': 'MoonDart', 'at-color': 'blue', 'owner': ['mitch', 'glen', 'paulie'], 'action': ['sample text - landed the plane and it was windy.', 'sample text - landed the plane and it was sunny.'], '@action.type': ['landing', 'landing'], '@action.weather': ['windy', 'sunny'], '@action.whitespace_attribute': 'whitespace     '}
/planes/       /planes/plane/1/  plane   {}            {'make': 'Cessna', 'year': '1933', 'model': 'Skyhawk', '@model.color': 'blue', 'owner': 'jim', 'action': 'text!', '@action.type': 'takeoff', '@action.weather': 'windy'}
/planes/       /planes/plane/2/  plane   {}            {'make': 'whitespace->>', 'year': '1833', 'model': 'puppy', '@model.color': 'blue', 'owner': 'hal', 'action': 'more with whitespace', '@action.type': 'takeoff', '@action.weather': 'blowy'}
""".strip()

    assert actual == expected, "Small xml didn't work?"


def test_airplanes_nested_maps():
    xml = slurp(path.join(get_project_dir(), "sample-data/airplanes-nested-maps.xml"))
    actual = mt(parse(xml), no_print=True)
    expected = """
parent_path                   path                               tag          attributes    value
----------------------------  ---------------------------------  -----------  ------------  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
/                             /planes/                           planes       {}            {}
/planes/                      /planes/plane/0/                   plane        {}            {'make': 'Cessna', 'year': '1977', 'model': 'MoonDart', 'at-color': 'blue', 'owner': ['mitch', 'glen', 'paulie'], 'action': ['sample text - landed the plane and it was windy.', 'sample text - landed the plane and it was sunny.'], '@action.type': ['landing', 'landing'], '@action.weather': ['windy', 'sunny'], '@action.whitespace_attribute': 'whitespace     '}
/planes/plane/0/              /planes/plane/0/plane_trips/       plane_trips  {}            {'trip': ['Mexico', 'Dallas', 'Far Far Away']}
/planes/plane/0/              /planes/plane/0/maintenance/       maintenance  {}            {}
/planes/plane/0/maintenance/  /planes/plane/0/maintenance/fuel/  fuel         {}            {'when': 'monday', 'type': 'gas', 'station': 'shell'}
/planes/                      /planes/plane/1/                   plane        {}            {'make': 'Cessna', 'year': '1933', 'model': 'Skyhawk', '@model.color': 'blue', 'owner': 'jim', 'action': 'text!', '@action.type': 'takeoff', '@action.weather': 'windy'}
/planes/                      /planes/plane/2/                   plane        {}            {'make': 'whitespace->>', 'year': '1833', 'model': 'puppy', '@model.color': 'blue', 'owner': 'hal', 'action': 'more with whitespace', '@action.type': 'takeoff', '@action.weather': 'blowy'}
""".strip()
    assert actual == expected, "Nested maps issues?"


def test_gross_tag_mid_text():
    "TODO"
    tucker_x = """<a>gross-text
                    <b grossAttrib="ugh">gross tag mid-text</b>
                </a>"""

    actual = mt(parse(tucker_x), no_print=True)
    # TODO - decide how to handle this.
    expected = """
parent_path    path    tag    attributes              value
-------------  ------  -----  ----------------------  -----------------------
/              /a/     a      {}                      {'#text': 'gross-text'}
/a/            /a/b/   b      {'grossAttrib': 'ugh'}  gross tag mid-text
""".strip()

    assert actual == expected, "Problem with tags inside text?"


def test_dispatch():
    xml = "<foo><bar>100</bar></foo>"
    a_dict = xmltodict.parse(xml)
    js = json.dumps(a_dict)

    expected = """
parent_path    path    tag    attributes    value
-------------  ------  -----  ------------  --------------
/              /foo/   foo    {}            {'bar': '100'}
""".strip()

    assert expected == mt(parse(xml), no_print=True), "XML dispatch didn't work?"
    assert expected == mt(parse(a_dict), no_print=True), "Dict dispatch didn't work?"
    assert expected == mt(parse(js), no_print=True), "JSON dispatch didn't work?"


def test_nhl():
    teams = {
        "compile-day": "monday",
        "compile-secret": "SECRET!",
        "nhl": [
            {"team": "stars", "players": 10, "pos": ["l", "r", "c"]},
            {"team": "bruins", "players": 30},
            {"team": "preds", "players": 90},
        ],
        "nba": [
            {
                "team": "mavs",
                "players": -9,
                "details": [
                    {"who": "bill", "pos": ["r", "c", "l"]},
                    {"who": "ted", "pos": ["d"]},
                    {"who": "fred"},
                ],
            },
            {"team": "bucks", "players": 3, "details": [{"who": "ken", "pos": ["c"]}]},
        ],
    }

    expected = """
parent_path    path               tag             attributes    value
-------------  -----------------  --------------  ------------  --------------------------------------------------------
/              /compile-day/      compile-day     {}            {'#text': 'monday'}
/              /compile-secret/   compile-secret  {}            SECRET!
/              /nhl/0/            nhl             {}            {'team': 'stars', 'players': 10, 'pos': ['l', 'r', 'c']}
/              /nhl/1/            nhl             {}            {'team': 'bruins', 'players': 30}
/              /nhl/2/            nhl             {}            {'team': 'preds', 'players': 90}
/              /nba/0/            nba             {}            {'team': 'mavs', 'players': -9}
/nba/0/        /nba/0/details/0/  details         {}            {'who': 'bill', 'pos': ['r', 'c', 'l']}
/nba/0/        /nba/0/details/1/  details         {}            {'who': 'ted', 'pos': 'd'}
/nba/0/        /nba/0/details/2/  details         {}            {'who': 'fred'}
/              /nba/1/            nba             {}            {'team': 'bucks', 'players': 3}
/nba/1/        /nba/1/details/0/  details         {}            {'who': 'ken', 'pos': 'c'}
""".strip()
    assert mt(parse(teams), no_print=True) == expected


def test_more_fake_data():
    more = {
        "Coach": {
            "Name": {"Title": "Mr", "Surname": "one", "GivenName": "person"},
            "DOB": "1984-01-01",
            "Gender": "F",
        },
        "TeamPlayers": [
            {
                "Name": {"Title": "Mr", "Surname": "one", "GivenName": "person"},
                "DOB": "1984-01-01",
                "jerseyDetails": [
                    {"JerseyNumber": "#1", "Size": "Large"},
                    {"JerseyNumber": "1", "Size": "Small"},
                ],
                "Gender": "M",
            },
            {
                "Name": {"Title": "Mr", "Surname": "two", "GivenName": "person"},
                "DOB": "1901-01-01",
                "jerseyDetails": [{"JerseyNumber": "ID2", "Size": "Large"}],
                "Gender": "F",
            },
        ],
        "ExtraData": [
            {"Name": "LikesCake", "Value": "true"},
            {"Name": "HasTwin", "Value": "true"},
            {"Name": "EnjoysTwin", "Value": "false"},
            {"Name": "FavCity", "Value": "Dallas"},
            {"Name": "HasChildren", "Value": "false"},
            {"Name": "MathGrade", "Value": "A"},
            {"Name": "US-State", "Value": "CT"},
            {"Name": "Date", "Value": "2019-01-01"},
        ],
    }
    expected = """
parent_path      path                             tag            attributes    value
---------------  -------------------------------  -------------  ------------  --------------------------------------------------------------------------------------------
/                /Coach/                          Coach          {}            {}
/Coach/          /Coach/Name/                     Name           {}            {'Title': 'Mr', 'Surname': 'one', 'GivenName': 'person', 'DOB': '1984-01-01', 'Gender': 'F'}
/                /TeamPlayers/0/                  TeamPlayers    {}            {}
/TeamPlayers/0/  /TeamPlayers/0/Name/             Name           {}            {'Title': 'Mr', 'Surname': 'one', 'GivenName': 'person', 'DOB': '1984-01-01'}
/TeamPlayers/0/  /TeamPlayers/0/jerseyDetails/0/  jerseyDetails  {}            {'JerseyNumber': '#1', 'Size': 'Large'}
/TeamPlayers/0/  /TeamPlayers/0/jerseyDetails/1/  jerseyDetails  {}            {'JerseyNumber': '1', 'Size': 'Small', 'Gender': 'M'}
/                /TeamPlayers/1/                  TeamPlayers    {}            {}
/TeamPlayers/1/  /TeamPlayers/1/Name/             Name           {}            {'Title': 'Mr', 'Surname': 'two', 'GivenName': 'person', 'DOB': '1901-01-01'}
/TeamPlayers/1/  /TeamPlayers/1/jerseyDetails/0/  jerseyDetails  {}            {'JerseyNumber': 'ID2', 'Size': 'Large', 'Gender': 'F'}
/                /ExtraData/0/                    ExtraData      {}            {'Name': 'LikesCake', 'Value': 'true'}
/                /ExtraData/1/                    ExtraData      {}            {'Name': 'HasTwin', 'Value': 'true'}
/                /ExtraData/2/                    ExtraData      {}            {'Name': 'EnjoysTwin', 'Value': 'false'}
/                /ExtraData/3/                    ExtraData      {}            {'Name': 'FavCity', 'Value': 'Dallas'}
/                /ExtraData/4/                    ExtraData      {}            {'Name': 'HasChildren', 'Value': 'false'}
/                /ExtraData/5/                    ExtraData      {}            {'Name': 'MathGrade', 'Value': 'A'}
/                /ExtraData/6/                    ExtraData      {}            {'Name': 'US-State', 'Value': 'CT'}
/                /ExtraData/7/                    ExtraData      {}            {'Name': 'Date', 'Value': '2019-01-01'}
""".strip()

    assert mt(parse(more), no_print=True) != ""
