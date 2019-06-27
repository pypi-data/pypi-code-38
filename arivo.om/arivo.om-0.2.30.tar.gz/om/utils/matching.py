# coding=utf-8
from __future__ import unicode_literals

import codecs
import glob
import logging
import os
import sys

import editdistance
import yaml

SEPARATOR_CHARS = " -_.:"
LEGACY_YAML_STRING = """
allowed: "0123456789ABCDEFGHIJKLMNPRSTUVWXYZ"
kept_separators: NONE
replacements:
  - from: "O"
    to: "0"
  - from: "Q"
    to: "0"
  - from: "Ä"
    to: "A"
  - from: "Ö"
    to: "0"
  - from: "Ü"
    to: "U"
exactitude: 0.0
"""

if sys.version_info < (3, 0):
    def ucode(txt):
        return unicode(txt)
else:
    def ucode(txt):
        return str(txt)


class PlateYaml(object):
    def __init__(self, filename):
        self.scheme = ""
        self.version = -1
        self.exactitude = 0.0
        self.filename = filename
        with codecs.open(filename, 'r', encoding="utf8") as f:
            try:
                self.settings = yaml.load(f)
                self.valid_chars = self.settings["allowed"]
                self.exactitude = self.settings["exactitude"]
                self.kept_separators = self.settings.get("kept_separators", "NONE").upper()
                self.replacements = []
                for r in self.settings.get("replacements", []):
                    if r.get("from", "") != "" and "to" in r:
                        self.replacements.append((ucode(r.get("from")), ucode(r.get("to"))))
            except:
                logging.error("Error loading Plate Yaml %s, will be ignored", filename)
                return

        try:
            self.scheme, tmp = os.path.basename(filename).replace(".", "-").split("-")[:2]
            self.version = int(tmp)
        except Exception as e:
            logging.exception(e)
            logging.error("Invalid Plate Yaml filename %s, will be ignored", filename)
            return

    def convert(self, plate):
        plate = plate.upper()
        for r in self.replacements:
            plate = plate.replace(r[0], r[1])
        tmp = plate
        for c in tmp:
            if c not in self.valid_chars:
                plate = plate.replace(c, "")

        if self.kept_separators != "ALL":
            plate_stripped = plate
            for c in list(SEPARATOR_CHARS):
                plate_stripped = plate_stripped.replace(c, "")
            if self.kept_separators == "FIRST":
                for i, c in enumerate(list(plate)):
                    if c in SEPARATOR_CHARS:
                        plate = plate[:i + 1] + plate_stripped[i:]
                        break
            elif self.kept_separators == "LAST":
                for i, c in enumerate(reversed(list(plate))):
                    if c in SEPARATOR_CHARS:
                        plate = plate_stripped[:-i] + plate[-1 - i:]
                        break
            else:
                plate = plate_stripped

        return plate


class PlateYamlSelector(object):
    def __init__(self, yaml_dir, revision_file="", default_country_order=[], legacy_in_default_country_order=False):
        self.yaml_dir = yaml_dir
        self.default_country_order = default_country_order
        self.legacy_in_default_country_order = legacy_in_default_country_order
        self.schemes = {}
        self.revision_file = revision_file
        self.revision = ""
        self.reload_yamls()

    def reload_yamls(self):
        if self.revision_file != "":
            with open(self.revision_file) as f:
                new_revision = f.read()
        else:
            new_revision = "LOADED"

        if new_revision != self.revision:
            yaml_filenames = glob.glob(os.path.join(self.yaml_dir, "*.yml"))
            self.schemes.clear()
            for fn in yaml_filenames:
                plate_yaml = PlateYaml(fn)
                if plate_yaml.version >= 0:  # check, if loading was successful
                    if plate_yaml.scheme in self.schemes:
                        self.schemes[plate_yaml.scheme][plate_yaml.version] = plate_yaml
                    else:
                        self.schemes[plate_yaml.scheme] = {plate_yaml.version: plate_yaml}
            if self.schemes.get("LEGACY", {}).get(0, None) is None:
                with codecs.open("/tmp/LEGACY-0.yml", 'w', encoding="utf8") as f:
                    f.write(LEGACY_YAML_STRING)
                legacy_yaml = PlateYaml("/tmp/LEGACY-0.yml")
                if legacy_yaml.version < 0:
                    raise Exception("NO LEGACY YAML COULD BE LOADED / CREATED")
            else:
                legacy_yaml = self.schemes["LEGACY"][0]
                del self.schemes["LEGACY"]
            if "DEFAULT" not in self.schemes:
                self.schemes["DEFAULT"] = {}

            for key in self.schemes.keys():
                self.schemes[key][0] = legacy_yaml

            self.revision = new_revision

    def get_scheme_versions_decreasing(self, country):
        if country not in self.schemes:
            country = "DEFAULT"
        return sorted(self.schemes[country].keys(), key=lambda x: self.schemes[country][x].exactitude, reverse=True)

    def get_all_exactitudes_decreasing(self):
        exactitudes = set([])
        for s in self.schemes.keys():
            for v in self.schemes[s].keys():
                exactitudes.add(self.schemes[s][v].exactitude)
        return sorted(exactitudes, reverse=True)

    def get_best_yaml(self, scheme, version):
        if scheme not in self.schemes:
            scheme = "DEFAULT"

        versions = sorted(self.schemes.get(scheme, {}).keys(), reverse=True)
        for v in versions:
            if v <= version:
                return self.schemes[scheme][v]

        raise Exception("NO YAML FOUND! THIS SHOULD NOT HAPPEN!")

    def convert(self, plate, scheme, version, return_matched_yaml=False):
        if return_matched_yaml:
            best_yaml = self.get_best_yaml(scheme, version)
            return {"plate": best_yaml.convert(plate), "scheme": best_yaml.scheme, "version": best_yaml.version,
                    "exactitude": best_yaml.exactitude}
        else:
            return self.get_best_yaml(scheme, version).convert(plate)

    def check_ed0(self, db_cv, plate, matches, num_alt, return_only_best=True):
        if db_cv and "plate_scheme" in db_cv[0]:
            p_conv = self.convert(plate, db_cv[0]["used_scheme"], db_cv[0]["used_version"])
            for db_entry in db_cv:
                if p_conv == db_entry["plate_conv"]:
                    matches[num_alt].append(db_entry)
                    if return_only_best:
                        return db_entry, matches
        return None, matches

    def check_edx(self, db_cv, plate, max_ed, matches, return_only_best=True):
        if db_cv and "plate_scheme" in db_cv[0]:
            p_conv = self.convert(plate, db_cv[0]["used_scheme"], db_cv[0]["used_version"])
            for db_entry in db_cv:
                ed = editdistance.eval(p_conv, db_entry["plate_conv"])
                if ed <= max_ed:
                    matches[ed].append(db_entry)
                if ed == 0 and return_only_best:
                    return db_entry, matches
        return None, matches

    def match_plate(self, plate, db, use_alternatives=True, max_ed=0, return_only_best=True):
        """
        Expected format of plate: {"plate": {"plate": <plate>, ...},
                                       "country": [{"country": <A/D/...>, "confidence": <0.0-1.0>}],
                                       "alternatives": [{"plate": <alt_plate1>, "confidence": <0.0-1.0>},...]}
        Expected format of db: {<Country1>: {<Version1>: [<plate1>, <plate2>,...]}}
            plates in converted form (converted using the best matching yaml, sorted into convert scheme and version,
                                                                                not db entry scheme and version)
        ED0 if use_alternatives (ed1 and alternatives does not make much sense)
        if return_only_best, matching will be stopped if ED0 match was found
        """
        self.reload_yamls()

        if use_alternatives:
            max_ed = 0
            plates = plate.get("alternatives", [])
            matches = [[]] * len(plates)
        else:
            plates = plate.get("alternatives", [])[:1]
            matches = [[]] * (max_ed + 1)
        for num_alt, p in enumerate(plates):
            check_other = False
            # first check based on countries given in plate
            checked_countries = []
            for c in plate.get("country", []):
                country = c["country"]
                if country == "OTHER":
                    check_other = True
                    break
                if country not in db:
                    continue
                for version in self.get_scheme_versions_decreasing(country):
                    if max_ed == 0:
                        res, matches = self.check_ed0(db[country].get(version, []), p["plate"], matches, num_alt,
                                                      return_only_best)
                    else:
                        res, matches = self.check_edx(db[country].get(version, []), p["plate"], max_ed, matches,
                                                      return_only_best)
                    if res is not None:
                        return [[res]]
                checked_countries.append(country)

            # if other specified, check other contries
            if check_other:
                no_legacy_checked_countries = []
                # first check in order given in config, but ignoring legacy (if not legacy_in_default_country_order)
                for country in self.default_country_order:
                    if country in checked_countries or country not in db:
                        continue
                    versions = self.get_scheme_versions_decreasing(country)
                    if not self.legacy_in_default_country_order:
                        versions = versions[:-1]
                    for version in versions:
                        if max_ed == 0:
                            res, matches = self.check_ed0(db[country].get(version, []), p["plate"], matches, num_alt,
                                                          return_only_best)
                        else:
                            res, matches = self.check_edx(db[country].get(version, []), p["plate"], max_ed, matches,
                                                          return_only_best)
                        if res is not None:
                            return [[res]]
                    if self.legacy_in_default_country_order:
                        checked_countries.append(country)
                    else:
                        no_legacy_checked_countries.append(country)

                # rest is checked in decreasing version order
                for exactitude in self.get_all_exactitudes_decreasing():
                    for country, db_country in db.items():
                        if country in checked_countries or exactitude != 0 and country in no_legacy_checked_countries:
                            continue
                        for version, db_cv in db_country.items():
                            if db_cv and db_cv[0]["exactitude"] == exactitude:
                                if max_ed == 0:
                                    res, matches = self.check_ed0(db[country].get(version, []), p["plate"], matches,
                                                                  num_alt, return_only_best)
                                else:
                                    res, matches = self.check_edx(db[country].get(version, []), p["plate"], max_ed,
                                                                  matches, return_only_best)
                                if res is not None:
                                    return [[res]]

            if return_only_best:
                for edm in matches:
                    if len(edm) > 0:
                        return [[edm[0]]]

        return matches
