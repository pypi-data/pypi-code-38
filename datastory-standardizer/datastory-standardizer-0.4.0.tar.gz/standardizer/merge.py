import os
import shutil
from functools import lru_cache
import ddf_utils
import pandas as pd


def filter_items(items, include):
    """
    Filter items by include.

    Parameters
    ----------
    items : list or DataFrame, sequence to be filtered. If DataFrame,
        assumed to be a DDF concepts file filtered by concept column.
    include : sequence of labels to include in items
    """
    if not include:
        return items
    if type(items) is list:
        if "--" not in items[0]:  # not datapoints
            return filter(lambda x: x in include, items)
        out = []
        for item in items:
            name = name.split("--")[2:]
            name.pop(1)
            if all([x in include for x in name]):
                out.append(item)
        return out
    if type(items) is pd.DataFrame:
        return items[items.concept.isin(include)]


class DDFPackage:
    """
    Thin wrapper for DDF datapackages.

    Parameters
    ----------
    path : string, path to package directory
    """

    def __init__(self, path):
        self.path = path
        self.meta = ddf_utils.package.get_datapackage(path)

    @lru_cache()
    def read_concepts(self):
        path = os.path.join(self.path, "ddf--concepts.csv")
        return pd.read_csv(path)

    def list_entities(self):
        entities = self.meta["ddfSchema"]["entities"]
        return [x["primaryKey"][0] for x in entities]

    def list_datafiles(self):
        datapoints = self.meta["ddfSchema"]["datapoints"]
        # TODO: Might be multiple resources here
        return [x["resources"][0] for x in datapoints]

    def read_datafile(self, name):
        path = os.path.join(self.path, f"ddf--datapoints--{name}.csv")
        return pd.read_csv(path)

    def read_entity(self, name):
        path = os.path.join(self.path, f"ddf--entities--{name}.csv")
        return pd.read_csv(path)

    def __contains__(self, concept):
        concepts = self.read_concepts()
        return (concepts.concept == concept).any()


class DDFPackageCollection:
    """
    Shared methods for querying and transforming a set of DDF packages.

    Parameters
    ----------
    paths : list, paths to package directories
    """

    def __init__(self, paths):
        self.paths = paths
        self.packages = [DDFPackage(x) for x in paths]

    def create_common_concepts_frame(self):
        df = pd.concat([x.read_concepts() for x in self.packages], sort=True)
        df = df.drop_duplicates(subset=["concept"])
        return df

    def list_shared_entities(self):
        entities = [set(x.list_entities()) for x in self.packages]
        return set.intersection(*entities)

    def list_distinct_entities(self):
        entities = [set(x.list_entities()) for x in self.packages]
        return set.symmetric_difference(*entities)

    def list_datafiles(self):
        datapoints = []
        for package in self.packages:
            datapoints.extend(package.list_datafiles())
        return datapoints

    def create_entity_frame(self, name):
        frames = []
        for package in self.packages:
            if name not in package.list_entities():
                continue
            frames.append(package.read_entity(name))
        return pd.concat(frames, sort=True)

    def create_datapoint_frame(self, name):
        frames = []
        for package in self.packages:
            if name not in package.list_datafiles():
                continue
            frames.append(package.read_datafile(name))
        return pd.concat(frames, sort=True)

    def to_package(self, dest, include=[]):
        shutil.rmtree(dest, ignore_errors=True)
        os.mkdir(dest)

        concepts = filter_items(self.create_common_concepts_frame(), include)
        path = os.path.join(dest, "ddf--concepts.csv")
        concepts.to_csv(path, index=False)

        for se in filter_items(self.list_shared_entities(), include):
            df = self.create_entity_frame(se)
            path = os.path.join(dest, f"ddf--entities--{se}.csv")
            df.to_csv(path, index=False)

        for de in filter_items(self.list_distinct_entities(), include):
            df = self.create_entity_frame(de)
            path = os.path.join(dest, f"ddf--entities--{de}.csv")
            df.to_csv(path, index=False)

        for datafile in filter_items(self.list_datafiles(), include):
            df = self.create_datapoint_frame(datafile)
            path = os.path.join(dest, f"ddf--datapoints--{datafile}.csv")
            df.to_csv(path, index=False)

        meta = ddf_utils.package.create_datapackage(dest)
        ddf_utils.io.dump_json(os.path.join(dest, "datapackage.json"), meta)
