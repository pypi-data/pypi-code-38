import io
import os
import shutil
import requests
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
import numpy as np
from datasetmaker.entity import Country
from datasetmaker import indicator
from datasetmaker.indicator import concepts


class WorldBank():
    @property
    def indicators(self):
        return concepts[(concepts.concept_type == 'measure') &
                        (concepts.source == 'wb')].concept.tolist()

    def get(self, indicators, **kwargs):
        data = []
        for ind in indicators:
            print(kwargs)
            data.append(get_wbi(ind, **kwargs))
        df = pd.concat(data, sort=True)
        df = df[df.countryiso3code != ""]
        df = df.drop(["decimal", "obs_status", "unit",
                    "country.id", "indicator.value"], axis=1)

        # Standardize country identifiers
        iso3_to_id = Country.iso3_to_id()
        name_to_id = Country.name_to_id()
        df["country"] = df.countryiso3code.str.lower().map(iso3_to_id)
        df["country"] = df.country.fillna(df["country.value"].map(name_to_id))
        df = df.drop(["country.value", "countryiso3code"], axis=1)

        df = df.rename(columns={"indicator.id": "indicator", "date": "year"})

        # Standardize indicator identifiers
        df.indicator = df.indicator.map(indicator.sid_to_id('wb'))

        return df


def to_ddf(df, path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

    df[["country"]].to_csv(
        os.path.join(path, "ddf--entities--country.csv"), index=False
    )

    concepts = (
        "concept,concept_type,name\n"
        "country,entity_domain,Country ID\n"
        "name,string,"
    )
    concepts = pd.read_csv(io.StringIO(concepts))

    for indicator in df.indicator.unique():
        fname = f'ddf--datapoints--{indicator}--by--country--year.csv'
        (df
            .filter(['value', 'country', 'year'])
            .rename(columns={'value': indicator})
            .to_csv(os.path.join(path, fname), index=False))

        concepts = concepts.append({
            'concept': indicator,
            'concept_type': 'measure',
            'name': indicator.id_to_name(source='wb').get(indicator)
        }, ignore_index=True)

    concepts.to_csv(os.path.join(path, "ddf--concepts.csv"), index=False)

    meta = package.create_datapackage(path)
    dump_json(os.path.join(path, "datapackage.json"), meta)

    return


def get_wbi(code, **kwargs):
    """Get a World Bank indicator for all countries."""

    url = f"http://api.worldbank.org/v2/country/all/indicator/{code}"
    kwargs.update({"format": "json", "page": 1})
    last_page = -1
    data = []

    while last_page != kwargs["page"]:
        resp = requests.get(url, kwargs).json()
        meta, page_data = resp
        last_page = meta["pages"]
        kwargs["page"] = kwargs["page"] + 1
        data.extend(page_data)

    df = pd.DataFrame(data)

    # Expand all dict columns
    for col in df.columns.copy():
        try:
            expanded = pd.io.json.json_normalize(df[col], record_prefix=True)
            expanded.columns = [f"{col}.{x}" for x in expanded.columns]
            df = pd.concat([df, expanded], axis=1)
            df = df.drop(col, axis=1)
        except AttributeError:
            continue

    return df
