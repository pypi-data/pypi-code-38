import os
import shutil
import requests


def mkdir(path, rm_if_exists=False):
    if os.path.exists(path):
        if rm_if_exists:
            shutil.rmtree(path)
    else:
        os.mkdir(path)
    return path


def pluck(seq, name):
    """Extracts a list of property values from list of dicts"""
    return [x[name] for x in seq]


def flatten(seq):
    """Perform shallow flattening operation (one level) of seq"""
    out = []
    for item in seq:
        for subitem in item:
            out.append(subitem)
    return out


class SDMXHandler:
    """
    Requesting and transforming SDMX-json data.

    Parameters
    ----------
    dataset : str, dataset identifier
    loc : list, list of countries
    subject : list, list of subjects
    """

    # TODO: URL should not be hardcoded
    base_url = "https://stats.oecd.org/sdmx-json/data"

    def __init__(self, dataset, loc=[], subject=[], **kwargs):
        loc = "+".join(loc)
        subject = "+".join(subject)
        filters = f"/{subject}.{loc}" if loc or subject else ''
        url = f"{self.base_url}/{dataset}{filters}/all"
        r = requests.get(url, params=kwargs)
        self.resp = r.json()

    def _map_dataset_key(self, key):
        key = [int(x) for x in key.split(":")]
        return {y["name"]: y["values"][x]["id"] for
                x, y in zip(key, self.dimensions)}

    def _map_attributes(self, attrs):
        attrs = [x for x in attrs if x is not None]
        return {y["name"]: y["values"][x]["id"] for
                x, y in zip(attrs, self.attributes)}

    @property
    def periods(self):
        return self.resp["structure"]["dimensions"]["observation"][0]

    @property
    def dimensions(self):
        return self.resp["structure"]["dimensions"]["series"]

    @property
    def attributes(self):
        return self.resp["structure"]["attributes"]["series"]

    @property
    def data(self):
        observations = []
        for key, unit in self.resp["dataSets"][0]["series"].items():
            dimensions = self._map_dataset_key(key)
            attributes = self._map_attributes(unit["attributes"])
            z = zip(self.periods["values"], unit["observations"].items())
            for period, (_, observation) in z:
                data = {"Value": observation[0]}
                data[self.periods["name"]] = period["id"]
                data.update(dimensions)
                data.update(attributes)
                observations.append(data)
        return observations
