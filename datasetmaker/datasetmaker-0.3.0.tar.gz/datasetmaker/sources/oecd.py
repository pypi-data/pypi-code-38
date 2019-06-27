import io
import os
import shutil
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
import numpy as np
from datasetmaker.entity import Country
from datasetmaker import indicator
from datasetmaker.models import Client
from datasetmaker.utils import SDMXHandler

pd.options.mode.chained_assignment = None


class OECD(Client):
    def load(dataset, loc=[], subject=[], **kwargs):
        sdmx = SDMXHandler(dataset, loc, subject, **kwargs)
        df = pd.DataFrame(sdmx.data)

        # Standardize data
        df['country'] = df.Country.str.lower().map(
            Country.iso3_to_id())
        df['indicator'] = df.Subject.map(indicator.sid_to_id(source='oecd'))

        df = df.drop(['Country', 'Subject', 'Time Format', 'Unit multiplier',
                      'Unit', 'reference period'], axis=1, errors='ignore')
        df.columns = [x.lower() for x in df.columns]

        return df

    def save(df, path):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        df_country = df[["country"]]
        df_country['name'] = df_country.country.map(
            Country.id_to_name())
        df_country.drop_duplicates().to_csv(
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
                .query(f'indicator == "{indicator}"')
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
