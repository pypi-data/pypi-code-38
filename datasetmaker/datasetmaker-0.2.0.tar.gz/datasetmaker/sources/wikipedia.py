import io
import json
import shutil
import pathlib
import calendar
from functools import reduce
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
import numpy as np
from datasetmaker.entity import Country
from datasetmaker.models import Client
from datasetmaker.indicator import concepts


base_url = "https://en.wikipedia.org/wiki"


class Wikipedia(Client):
    @property
    def indicators(self):
        global concepts
        return concepts[concepts.source == 'wp'].concept.tolist()   

    def _map_pages(self, concept_names):
        pages = []
        for name in concept_names:
            if name == 'country':
                continue
            page = concepts[concepts.concept == name].context.iloc[0]
            page = json.loads(page).get('page')
            pages.append(page)
        return set(pages)

    def get(self, indicators, years=None):
        pages = self._map_pages(indicators)
        frames = []
        for page in pages:
            frame = scrapers[page]()
            frames.append(frame)
        df = reduce(lambda l, r: pd.merge(
            l, r, on='country', how='outer'), frames)
        df = df[indicators]
        df = df.dropna(subset=['country'])
        df = df.drop_duplicates(subset=['country'])
        self.data = df
        return df

    def save(self, path, **kwargs):
        global concepts

        path = pathlib.Path(path)
        if path.exists():
            shutil.rmtree(path)
        path.mkdir()

        self.data.to_csv(path / 'ddf--entities--country.csv', index=False)

        concepts_ = concepts[concepts.concept.isin(self.data.columns)]
        concepts_ = concepts_[['concept', 'concept_type', 'name']]
        concepts_.to_csv(path / 'ddf--concepts.csv', index=False)

        meta = package.create_datapackage(path, **kwargs)
        dump_json(path / 'datapackage.json', meta)

        return self


def scrape_elections():
    url = f'{base_url}/List_of_next_general_elections'
    tables = pd.read_html(url, match="Parliamentary")
    df = pd.concat(tables, sort=True)

    cols = [
        "country",
        "wp_fair",
        "wp_gdp",
        "wp_ihdi",
        "wp_power",
        "wp_parl_prev",
        "wp_parl_next",
        "wp_parl_term",
        "wp_pop",
        "wp_pres_prev",
        "wp_pres_next",
        "wp_pres_term",
        "wp_status",
    ]

    keep_cols = [
        "country",
        "wp_parl_prev",
        "wp_parl_next",
        "wp_parl_term",
        "wp_pres_prev",
        "wp_pres_next",
        "wp_pres_term",
    ]

    df.columns = cols
    df = df[keep_cols]

    # Remove countries with no next election info
    df = df[df.wp_parl_next.notnull()]

    # Convert previous election to datetime
    df["wp_parl_prev"] = pd.to_datetime(df.wp_parl_prev)

    # Remove footnotes
    df.wp_parl_term = df.wp_parl_term.str.split("[", expand=True)[0]
    df.wp_pres_term = df.wp_pres_term.str.split("[", expand=True)[0]

    df.wp_parl_next = parse_wp_time(df.wp_parl_next)
    df.wp_pres_next = parse_wp_time(df.wp_pres_next)

    df.wp_parl_term = df.wp_parl_term.str.split(" ", expand=True)[0]
    df.country = df.country.replace("Korea", "South Korea")
    df["iso_3"] = df.country.map(Country.name_to_id())

    df = df.drop('country', axis=1).rename(columns={'iso_3': 'country'})
    df = df.dropna(subset=["country"])

    return df


def parse_wp_time(ser):
    year = ser.str[-4:]
    month = ser.str.extract("(\D+)")[0]
    month = month.str.strip()
    day = ser.str.extract("(\d{1,2}) ")[0]

    month_names = list(calendar.month_name)

    month = month.apply(
        lambda x: str(month_names.index(x)).zfill(
            2) if x in month_names else np.nan
    )

    month = month.astype(str).str.replace("nan", "")
    day = day.astype(str).str.zfill(2).str.replace("nan", "")

    ser = year + '-' + month + '-' + day

    ser = ser.str.replace("-nan", "")
    ser = ser.str.replace('-+$', '', regex=True)
    return ser


def scrape_heads_of_state_and_government():
    url = f'{base_url}/List_of_current_heads_of_state_and_government'
    tables = pd.read_html(url)
    df = pd.concat(tables[1:4], sort=True)
    df = df.drop('Also claimed by', axis=1)
    df['State'] = df['State'].fillna(df['State/Government'])
    df = df.drop('State/Government', axis=1)
    df.columns = ['wp_head_gov', 'wp_head_state', 'country']
    df['country'] = df.country.map(Country.name_to_id())

    head_state = (df
                  .wp_head_state
                  .str.replace('\xa0', ' ')
                  .str.split('\[α\]', expand=True)[0]
                  .str.split('\[δ\]', expand=True)[0]
                  .str.split('\[γ\]', expand=True)[0]
                  .str.split('\[κ\]', expand=True)[0]
                  .str.split(' – ', n=-1, expand=True))

    df['wp_head_state_title'] = head_state[0].str.strip()
    df['wp_head_state_name'] = head_state[1].str.strip()

    head_gov = (df
                .wp_head_gov
                .str.replace('\xa0', ' ')
                .str.split('\[α\]', expand=True)[0]
                .str.split('\[δ\]', expand=True)[0]
                .str.split('\[γ\]', expand=True)[0]
                .str.split('\[κ\]', expand=True)[0]
                .str.split(' – ', n=-1, expand=True))

    df['wp_head_gov_title'] = head_gov[0].str.strip()
    df['wp_head_gov_name'] = head_gov[1].str.strip()

    df = df.drop(['wp_head_state', 'wp_head_gov'], axis=1)

    return df


scrapers = {
    'List_of_next_general_elections': scrape_elections,
    'List_of_current_heads_of_state_and_government': scrape_heads_of_state_and_government
}
