import io
import os
import json
import shutil
import logging
from glob import glob
from functools import reduce
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from multiprocessing.pool import ThreadPool

import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq  # noqa
from frame2package import Frame2Package
import requests

from datasetmaker.models import Client
from datasetmaker.utils import mkdir, pluck, flatten
from datasetmaker.path import ROOT_DIR, DDF_DIR

logger = logging.getLogger()


_base_url = 'https://siris.skolverket.se/siris/reports'
_cache_dir = os.path.join(ROOT_DIR, '.cache_dir')
_form_codes = ['11', '21']  # Grundskolan, Gymnasieskolan


class Table:
    _shape = None
    _data = None

    def __init__(self, code: str, uttag: str, year_code: list):
        self.code = code
        self.uttag = uttag
        self.year_code = year_code

    @property
    def fname(self):
        return f'{self.code}-{self.year_code}.parquet'

    @property
    def cached(self):
        return os.path.exists(os.path.join(_cache_dir, self.fname))

    @property
    def columns(self):
        return [x.name for x in self.load().columns]

    @property
    def concepts(self):
        items = []
        cols = self.columns
        for col in cols:
            item = next(filter(lambda x: x['concept'] == col, concepts))
            items.append(item)
        return items

    @property
    def entities(self):
        concepts = self.concepts
        types = ['time', 'entity_domain']
        return [x['concept'] for x in concepts if x['concept_type'] in types]

    def add_column(self, name, data):
        col = pa.column(name, data)
        pos = self._find_column_position(name)
        self._data = self._data.add_column(pos, col)
        self._write_table()
        return self

    def _find_column_position(self, col):
        cols = self.columns.copy()
        cols.append(col)
        cols = sorted(cols)
        return cols.index(col)

    def _fetch_xml(self):
        print(f'Downloading {self}')
        logger.debug(f'Downloading {self}')
        url = (f'{_base_url}/export_api/runexport/?pFormat=xml'
               f'&pExportID={self.code}&pAr={self.year_code}'
               f'&pUttag={self.uttag}&pFlikar=1')
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
        return

    def _read_table(self, columns=None):
        logger.debug('Reading table from disk')
        table = pq.read_table(os.path.join(_cache_dir, self.fname), columns)
        return table

    def _write_table(self):
        logger.debug('Writing table to disk')
        pq.write_table(self._data, os.path.join(_cache_dir, self.fname))

    def load(self, columns=None):
        if self._data:
            return self._data
        if self.cached:
            self._data = self._read_table(columns)
        else:
            xml = self._fetch_xml()
            self._data = self._xml_to_arrow(xml)
            self._write_table()
        self.shape = self._data.shape
        return self._data

    def _xml_to_arrow(self, xml):
        data = []
        tree = ET.parse(io.StringIO(xml))
        root = tree.getroot()
        for s in root.findall('skola'):
            school = s.attrib
            for prop in s:
                school[prop.tag] = prop.text
            data.append(school)
        df = pd.DataFrame(data)
        df['year'] = self.year_code
        sid_to_id = pd.DataFrame(concepts)
        alt = sid_to_id[sid_to_id.alt_spelling.notnull()].copy()
        alt.sid = alt.alt_spelling
        alt = alt.drop(['alt_spelling'], axis=1)
        sid_to_id = pd.concat([sid_to_id, alt], sort=True, axis=0)
        sid_to_id = sid_to_id[(sid_to_id.table == self.code) |
                              (sid_to_id.table.isnull())]
        sid_to_id = sid_to_id.set_index('sid').concept.to_dict()
        df.columns = sorted(df.columns.map(sid_to_id))
        arrow = pa.Table.from_pandas(df.fillna(''))
        return arrow

    def __repr__(self):
        return f'<Table code="{self.code}" year={self.year_code}>'

    def __str__(self):
        return f'<Table code="{self.code}" year={self.year_code}>'


class MultiYearTable:
    _entities = []

    def __init__(self, code: str, uttag: str, year_codes: list):
        self.code = code
        self.uttag = uttag
        self.year_codes = year_codes

    @property
    def entities(self):
        if len(self._entities) > 0:
            return self._entities
        self._entities = Table(self.code, self.uttag, self.year_codes[0]).entities
        return self._entities

    def to_parquet(self, columns=None):
        tables = [Table(self.code, self.uttag, y) for y in self.year_codes]
        all_cols = [x for t in tables for x in t.columns]
        for table in tables:
            for col in all_cols:
                if col not in table.columns:
                    table.add_column(col, [[''] * table.shape[0]])

        return pa.concat_tables([t.load(columns) for t in tables])

    def to_pandas(self, columns=None):
        return self.to_parquet(columns).to_pandas()

    def __repr__(self):
        return f'<MultiYearTable code="{self.code}" years={str(self.year_codes)}>'

    def __str__(self):
        return f'<MultiYearTable code="{self.code}" years={str(self.year_codes)}>'


class SKVClient(Client):
    _schema = None

    def __init__(self):
        mkdir(_cache_dir, rm_if_exists=False)

    @property
    def indicators(self):
        return [x['concept'] for x in concepts
                if x['concept_type'] == 'measure']

    def _validate_input(self, indicators, years):
        concept_names = pluck(concepts, 'concept')
        for indicator in indicators:
            if indicator not in concept_names:
                raise ValueError(f'{indicator} is not a valid indicator')
            available_years = pluck(self.schema, 'år')
            available_years = [x['kod'] for x in flatten(available_years)]
            for year in years:
                if year not in available_years:
                    raise ValueError(f'{year} is not available in any table')

    def get(self, indicators, years):
        years = [str(x) for x in years]

        # Validate indicators and years
        self._validate_input(indicators, years)

        # Fetch data remotely
        frames = []
        entities = set()
        schemas = self._table_schemas_from_concepts(indicators)
        for schema in schemas:
            _years = [x for x in years if str(x) in pluck(schema['år'], 'kod')]
            table = MultiYearTable(schema['kod'], schema['uttag'], _years)
            frames.append(table.to_pandas(columns=indicators))
            entities.update(table.entities)
        keys = list(entities)
        for frame in frames:
            for key in keys:
                if key not in frame:
                    frame[key] = None
        df = reduce(lambda l, r: pd.merge(l, r, on=keys, how='outer'), frames)
        df = df[indicators + keys]

        # Clean data
        df = df.pipe(self._clean_data)

        return df.set_index(keys)

    def _clean_data(self, df):
        df = df.replace(['..', '.'], [None, None])
        df = df.replace(',', '.', regex=True)
        df = df.replace('~100', '100')
        df = df.replace({'(\d) (\d)': r'\1\2'}, regex=True)

        for col in df.columns:
            if col in [x['concept'] for x in concepts if x['concept_type'] == 'measure']:
                df[col] = df[col].astype(np.float64)

        # Standardize these column names
        common = [('skolkod', 'skol_kod'), ('kommunnamn', 'kommun_namn'),
                ('skolnamn', 'skol_namn'), ('skolnamn', 'skola'),
                ('program', 'prog'), ('prov', 'provnamn')]

        for i, j in common:
            if j not in df:  # if there are no variables to replace
                continue
            if i not in df:  # if the replacement does not yet exist
                df = df.rename(columns={j: i})
            else:  # if both variables exist
                df[i] = df[i].fillna(df[j])
                df = df.drop(j, axis=1)

        return df

    def clear_cache(self):
        shutil.rmtree(_cache_dir)

    @property
    def schema(self):
        if self._schema:
            return self._schema
        _schema = []

        for form_code in _form_codes:
            areas_url = (f'{_base_url}/export_api/omrade/'
                         f'?pVerkform={form_code}&pNiva=S')
            areas = requests.get(areas_url).json()

            for area in areas:
                tables_url = (f'{_base_url}/export_api/export/?pVerkform='
                              f'{form_code}&pNiva=S&pOmrade={area["kod"]}')
                tables = requests.get(tables_url).json()

                for table in tables:
                    table['år'] = []
                    years_url = (f'{_base_url}/export_api/lasar/?pExportID='
                                f'{table["kod"]}')
                    years = requests.get(years_url).json().get('data')

                    for year in years:
                        table['år'].append(year)

                    uttag_url = (f'{_base_url}/export_api/extra/?pExportID='
                                 f'{table["kod"]}&pAr={years[0]["kod"]}')
                    uttag = requests.get(uttag_url).json()
                    if len(uttag['uttag']) == 0:
                        table['uttag'] = 'null'
                    else:
                        table['uttag'] = uttag['uttag'][0]['kod']

                    table.pop('egenskaper')
                    _schema.append(table)
        self._schema = _schema
        return _schema

    def _table_schemas_from_concepts(self, concept_names):
        schemas = []
        codes = []
        for concept in concept_names:
            table_code = [x['table'] for x in concepts if x['concept'] == concept][0]
            schema = [x for x in self.schema if x['kod'] == table_code][0].copy()
            if schema['kod'] not in codes:
                schemas.append(schema)
                codes.append(schema['kod'])
        return schemas


concepts = [{
        'concept': 'ak1_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 1',
        'sid': 'ak1_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'ak2_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 2',
        'sid': 'ak2_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'ak3_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 3',
        'sid': 'ak3_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'ak4_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 4',
        'sid': 'ak4_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'ak5_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 5',
        'sid': 'ak5_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'ak6_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 6',
        'sid': 'ak6_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'ak7_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 7',
        'sid': 'ak7_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'ak8_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 8',
        'sid': 'ak8_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'ak9_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 9',
        'sid': 'ak9_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'amne',
        'concept_type': 'entity_domain',
        'form': None,
        'name': 'Ämne',
        'sid': 'amne',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'and_ae_fli__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) med A-E, flickor',
        'sid': 'and_ae_fli',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'and_ae_poj__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) med A-E, pojkar',
        'sid': 'and_ae_poj',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'and_ae_tot__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) med A-E, totalt',
        'sid': 'and_ae_tot',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_ehs__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever (%) behöriga till Ekonomi-, humanistiska och samhällsvetenskaps- program',
        'sid': 'and_beh_ehs',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_ehs_exklok__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till Ekonomi-, humanistiska och samhällsvetenskaps- program, exklusive okänd bakgrund',
        'sid': 'and_beh_ehs_exklok',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_est__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever (%) behöriga till estetiskt program',
        'sid': 'and_beh_est',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_est_exklok__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till estetiskt program, exklusive okänd bakgrund',
        'sid': 'and_beh_est_exklok',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_nt__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever (%) behöriga till Naturvetenskapligt och tekniskt program',
        'sid': 'and_beh_nt',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_nt_exklok__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till Naturvetenskapligt och tekniskt program, exklusive okänd bakgrund',
        'sid': 'and_beh_nt_exklok',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_yrk__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram',
        'sid': 'and_beh_yrk',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_yrk__139',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram',
        'sid': 'and_beh_yrk',
        'table': '139',
        'table_name': 'Slutbetyg årskurs 9, samtliga elever',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_yrk_exklok__139',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram, exklusive okänd bakgrund',
        'sid': 'and_beh_yrk_exklok',
        'table': '139',
        'table_name': 'Slutbetyg årskurs 9, samtliga elever',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_yrk_exklok__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram, exklusive okänd bakgrund',
        'sid': 'and_beh_yrk_exklok',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_yrk_exklok_fli__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram, flickor, exklusive okänd bakgrund',
        'sid': 'and_beh_yrk_exklok_fli',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_beh_yrk_exklok_poj__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram, pojkar, exklusive okänd bakgrund',
        'sid': 'and_beh_yrk_exklok_poj',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_eftgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, föräldrar eftergymnasial utbildning',
        'sid': 'and_behorig_eftgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_f_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, utländsk bakgrund födda i Sverige',
        'sid': 'and_behorig_f_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_f_utl__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, utländsk bakgrund födda utomlands',
        'sid': 'and_behorig_f_utl',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_fli__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, flickor',
        'sid': 'and_behorig_fli',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_forgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, föräldrar förgymnasial utbildning',
        'sid': 'and_behorig_forgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_gy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, föräldrar gymnasieutbildning',
        'sid': 'and_behorig_gy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_poj__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, pojkar',
        'sid': 'and_behorig_poj',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, svensk bakgrund',
        'sid': 'and_behorig_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_tot__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, totalt',
        'sid': 'and_behorig_tot',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_yrkes_exklok__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram, exklusive okänd bakgrund',
        'sid': 'and_behorig_yrkes_exklok',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_yrkes_exl__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, exklusive nyinvandrade',
        'sid': 'and_behorig_yrkes_exl',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_yrkes_min4ar__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram, exklusive nyinvandrade och okänd bakgrund',
        'sid': 'and_behorig_yrkes_min4ar',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_yrkes_min4ar_fli__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram, exklusive nyinvandrade och okänd bakgrund, flickor',
        'sid': 'and_behorig_yrkes_min4ar_fli',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_yrkes_min4ar_poj__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram, exklusive nyinvandrade och okänd bakgrund, pojkar',
        'sid': 'and_behorig_yrkes_min4ar_poj',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_yrkes_nyinv__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) behöriga till yrkesprogram, nyinvandrade',
        'sid': 'and_behorig_yrkes_nyinv',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behorig_yrkes_samtl__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever behöriga till yrkesprogram',
        'sid': 'and_behorig_yrkes_samtl',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behoriga__102',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel lärare med lärarlegitimation och behörighet i ämnet',
        'sid': 'and_behoriga',
        'table': '102',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behoriga__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel lärare med lärarlegitimation och behörighet i minst ett ämne, alla tjänstgörande lärare',
        'sid': 'and_behoriga',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behoriga__106',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel lärare med lärarlegitimation och behörighet i ämnet',
        'sid': 'and_behoriga',
        'table': '106',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behoriga__263',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel lärare med lärarlegitimation och behörighet i ämnet',
        'sid': 'and_behoriga',
        'table': '263',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne, yrkesämnen',
        'unit': 'Prc'
    },
    {
        'concept': 'and_behoriga__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel lärare med lärarlegitimation och behörighet i minst ett ämne',
        'sid': 'and_behoriga',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_delt_fli__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel deltagande flickor',
        'sid': 'and_delt_fli',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'and_delt_poj__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel deltagande flickor',
        'sid': 'and_delt_poj',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'and_delt_tot__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel deltagande totalt',
        'sid': 'and_delt_tot',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'and_ej_beh__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever (%) ej behöriga',
        'sid': 'and_ej_beh',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_ej_beh_exklok__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever ej behöriga exklusive okänd bakgrund',
        'sid': 'and_ej_beh_exklok',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'Prc'
    },
    {
        'concept': 'and_helttj_larare_leg__102',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel med lärarlegitimation och behörighet i ämnet, heltidstjänster',
        'sid': 'and_helttj_larare_leg',
        'table': '102',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_helttj_larare_leg__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel med lärarlegitimation och behörighet i minst ett ämne, heltidstjänster',
        'sid': 'and_helttj_larare_leg',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_helttj_larare_leg__106',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel med lärarlegitimation och behörighet i ämnet, heltidstjänster',
        'sid': 'and_helttj_larare_leg',
        'table': '106',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_helttj_larare_leg__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel med lärarlegitimation och behörighet i minst ett ämne, heltidstjänster',
        'sid': 'and_helttj_larare_leg',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_helttj_larare_leg__263',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel med lärarlegitimation och behörighet i ämnet, heltidstjänster',
        'sid': 'and_helttj_larare_leg',
        'table': '263',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne, yrkesämnen',
        'unit': 'Prc'
    },
    {
        'concept': 'and_larare_pedex__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel lärare med pedagogisk högskoleexamen, alla tjänstgörande lärare',
        'sid': 'and_larare_pedex',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_larare_pedex__102',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel lärare med pedagogisk högskoleexamen, alla tjänstgörande lärare',
        'sid': 'and_larare_pedex',
        'table': '102',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_larare_pedex__106',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel lärare med pedagogisk högskoleexamen, alla tjänstgörande lärare',
        'sid': 'and_larare_pedex',
        'table': '106',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_larare_pedex__263',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel lärare med pedagogisk högskoleexamen, alla tjänstgörande lärare',
        'sid': 'and_larare_pedex',
        'table': '263',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne, yrkesämnen',
        'unit': 'Prc'
    },
    {
        'concept': 'and_larare_pedex__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel lärare med pedagogisk högskoleexamen, alla tjänstgörande lärare',
        'sid': 'and_larare_pedex',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_eftgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, föräldrar eftergymnasial utbildning',
        'sid': 'and_uppn_alla_amnen_eftgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_exklok__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, exklusive okänd bakgrund',
        'sid': 'and_uppn_alla_amnen_exklok',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_exklok_fli__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, flickor, exklusive okänd bakgrund',
        'sid': 'and_uppn_alla_amnen_exklok_fli',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_exklok_poj__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, pojkar, exklusive okänd bakgrund',
        'sid': 'and_uppn_alla_amnen_exklok_poj',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_exl__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, exklusive nyinvandrade',
        'sid': 'and_uppn_alla_amnen_exl',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_f_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, utländsk bakgrund födda i Sverige',
        'sid': 'and_uppn_alla_amnen_f_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_f_utl__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, utländsk bakgrund födda utomlands',
        'sid': 'and_uppn_alla_amnen_f_utl',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_fli__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, flickor',
        'sid': 'and_uppn_alla_amnen_fli',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_forgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, föräldrar förgymnasial utbildning',
        'sid': 'and_uppn_alla_amnen_forgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_gy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, föräldrar gymnasieutbildning',
        'sid': 'and_uppn_alla_amnen_gy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_min4ar__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever som uppnått kunskapskraven i alla ämnen, exklusive nyinvandrade och okänd bakgrund',
        'sid': 'and_uppn_alla_amnen_min4ar',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_min4ar_fli__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever som uppnått kunskapskraven i alla ämnen, exklusive nyinvandrade och okänd bakgrund, flickor',
        'sid': 'and_uppn_alla_amnen_min4ar_fli',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_min4ar_poj__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever som uppnått kunskapskraven i alla ämnen, exklusive nyinvandrade och okänd bakgrund, pojkar',
        'sid': 'and_uppn_alla_amnen_min4ar_poj',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_nyinv__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, nyinvandrade',
        'sid': 'and_uppn_alla_amnen_nyinv',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_poj__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, pojkar',
        'sid': 'and_uppn_alla_amnen_poj',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_samtl__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever som uppnått kunskapskraven i alla ämnen, exklusive nyinvandrade och okänd bakgrund, totalt',
        'sid': 'and_uppn_alla_amnen_samtl',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, svensk bakgrund',
        'sid': 'and_uppn_alla_amnen_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'and_uppn_alla_amnen_tot__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen, totalt',
        'sid': 'and_uppn_alla_amnen_tot',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'and_utl_bakgr__95',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel nyinvandrade',
        'sid': 'and_utl_bakgr',
        'table': '95',
        'table_name': 'Salsa, skolenheters resultat av slutbetygen i årskurs 9 med hänsyn till elevsammansättningen',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_a__65',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med kursprovsbetyg A',
        'sid': 'andel_a',
        'table': '65',
        'table_name': 'Kursprovsbetyg, elever som började 2011 eller senare',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ae_fli__93',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) med A-E, flickor',
        'sid': 'andel_ae_fli',
        'table': '93',
        'table_name': 'Slutbetyg per ämne årskurs 9, fr.o.m. 2013',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ae_poj__93',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) med A-E, pojkar',
        'sid': 'andel_ae_poj',
        'table': '93',
        'table_name': 'Slutbetyg per ämne årskurs 9, fr.o.m. 2013',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ae_tot__93',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) med A-E, totalt',
        'sid': 'andel_ae_tot',
        'table': '93',
        'table_name': 'Slutbetyg per ämne årskurs 9, fr.o.m. 2013',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_arbetar_ett__97',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel ungdomar som arbetar ett år efter gymnasiestudier',
        'sid': 'andel_arbetar_ett',
        'table': '97',
        'table_name': 'Vad ungdomar gör efter gymnasieskolan - ett, tre eller fem år efter gymnasiestudier',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_arbetar_ett__185',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel ungdomar som arbetar ett år efter gymnasiestudier',
        'sid': 'andel_arbetar_ett',
        'table': '185',
        'table_name': 'Vad ungdomar gör efter gymnasieskolan - ett, tre eller fem år efter gymnasiestudier, LGY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_arbetar_tre__97',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel ungdomar som arbetar tre år efter gymnasiestudier',
        'sid': 'andel_arbetar_tre',
        'table': '97',
        'table_name': 'Vad ungdomar gör efter gymnasieskolan - ett, tre eller fem år efter gymnasiestudier',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_b__65',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med kursprovsbetyg B',
        'sid': 'andel_b',
        'table': '65',
        'table_name': 'Kursprovsbetyg, elever som började 2011 eller senare',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_behoriga_hs__54',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel behöriga till högskolestudier',
        'sid': 'andel_behoriga_hs',
        'table': '54',
        'table_name': 'Slutbetyg och behörighet, per program (t.o.m. 2012/13)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_c__65',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med kursprovsbetyg C',
        'sid': 'andel_c',
        'table': '65',
        'table_name': 'Kursprovsbetyg, elever som började 2011 eller senare',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_d__65',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med kursprovsbetyg D',
        'sid': 'andel_d',
        'table': '65',
        'table_name': 'Kursprovsbetyg, elever som började 2011 eller senare',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_e__65',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med kursprovsbetyg E',
        'sid': 'andel_e',
        'table': '65',
        'table_name': 'Kursprovsbetyg, elever som började 2011 eller senare',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_eftgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever, föräldrar eftergymnasial utbildning',
        'sid': 'andel_eftgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_ett__143',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i ett ämne',
        'sid': 'andel_ej_uppnatt_ett',
        'table': '143',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), samtliga elever',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_ett_exkl__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i ett ämne, exklusive nyinvandrade och okänd bakgrund',
        'sid': 'andel_ej_uppnatt_ett_exkl',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_ett_fli__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i ett ämne, flickor',
        'sid': 'andel_ej_uppnatt_ett_fli',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_ett_poj__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i ett ämne, pojkar',
        'sid': 'andel_ej_uppnatt_ett_poj',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_ett_tot__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i ett ämne, totalt',
        'sid': 'andel_ej_uppnatt_ett_tot',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_min_tva_exkl__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i minst två ämnen, exklusive nyinvandrade och okänd bakgrund',
        'sid': 'andel_ej_uppnatt_min_tva_exkl',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_min_tva_tot__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i minst två ämnen, totalt',
        'sid': 'andel_ej_uppnatt_min_tva_tot',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_minst_tva__143',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i minst två ämnen',
        'sid': 'andel_ej_uppnatt_minst_tva',
        'table': '143',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), samtliga elever',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_minst_tva_fli__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i minst två ämnen, flickor',
        'sid': 'andel_ej_uppnatt_minst_tva_fli',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_ej_uppnatt_minst_tva_poj__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som ej uppnått kunskapskraven (A-E) i minst två ämnen, pojkar',
        'sid': 'andel_ej_uppnatt_minst_tva_poj',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_elever_exl__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever exklusive nyinvandrade',
        'sid': 'andel_elever_exl',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_elever_min4ar__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever årskurs 9, exklusive nyinvandrade och okänd bakgrund',
        'sid': 'andel_elever_min4ar',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_elever_min4ar_fli__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever årskurs 9, exklusive nyinvandrade och okänd bakgrund, flickor',
        'sid': 'andel_elever_min4ar_fli',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_elever_min4ar_poj__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever årskurs 9, exklusive nyinvandrade och okänd bakgrund, pojkar',
        'sid': 'andel_elever_min4ar_poj',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_elever_nyinv__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever nyinvandrade',
        'sid': 'andel_elever_nyinv',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_examen_inom_3__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel som slutfört med examen inom 3 år',
        'sid': 'andel_examen_inom_3',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_examen_inom_4__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel som slutfört med examen inom 4 år',
        'sid': 'andel_examen_inom_4',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_examen_inom_5__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel som slutfört med examen inom 5 år',
        'sid': 'andel_examen_inom_5',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_f__65',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med kursprovsbetyg F',
        'sid': 'andel_f',
        'table': '65',
        'table_name': 'Kursprovsbetyg, elever som började 2011 eller senare',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_f_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel utländsk bakgrund födda i Sverige',
        'sid': 'andel_f_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_f_utl__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel utländsk bakgrund födda utomlands',
        'sid': 'andel_f_utl',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_fli__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel flickor',
        'sid': 'andel_fli',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_forald_eftergymn_utb__70',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel med föräldrar med eftergymnasial utbildning',
        'sid': 'andel_forald_eftergymn_utb',
        'table': '70',
        'table_name': 'Antal elever som började 2011 eller senare, per program och inriktning',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_forald_eftergymn_utb__136',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel med föräldrar med eftergymnasial utbildning',
        'sid': 'andel_forald_eftergymn_utb',
        'table': '136',
        'table_name': 'Antal elever',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_forald_eftergymn_utb__21',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel med föräldrar med eftergymnasial utbildning',
        'sid': 'andel_forald_eftergymn_utb',
        'table': '21',
        'table_name': 'Antal elever som började 2011 eller senare, per program',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_forgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever, föräldrar förgymnasial utbildning',
        'sid': 'andel_forgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_gy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever, föräldrar gymnasieutbildning',
        'sid': 'andel_gy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_hojt__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med högre kursbetyg än provbetyg i ämnet',
        'sid': 'andel_hojt',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_hojt_kvi__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med högre kursbetyg än provbetyg i ämnet, kvinnor',
        'sid': 'andel_hojt_kvi',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_hojt_man__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med högre kursbetyg än provbetyg i ämnet, män',
        'sid': 'andel_hojt_man',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_kvi__70',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel kvinnor',
        'sid': 'andel_kvi',
        'table': '70',
        'table_name': 'Antal elever som började 2011 eller senare, per program och inriktning',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_kvi__136',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel kvinnor',
        'sid': 'andel_kvi',
        'table': '136',
        'table_name': 'Antal elever',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_kvi__21',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel kvinnor',
        'sid': 'andel_kvi',
        'table': '21',
        'table_name': 'Antal elever som började 2011 eller senare, per program',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_lika__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med lika kursbetyg som provbetyg i ämnet',
        'sid': 'andel_lika',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_lika_kvi__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med lika kursbetyg som provbetyg i ämnet, kvinnor',
        'sid': 'andel_lika_kvi',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_lika_man__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med lika kursbetyg som provbetyg i ämnet, män',
        'sid': 'andel_lika_man',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_med_examen__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med examen',
        'sid': 'andel_med_examen',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_med_gr_behorighet__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med grundläggande behörighet',
        'sid': 'andel_med_gr_behorighet',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_med_studiebevis__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med studiebevis',
        'sid': 'andel_med_studiebevis',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_med_utokat_prog__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med utökat program',
        'sid': 'andel_med_utokat_prog',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_eng5__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i Engelska 5',
        'sid': 'andel_minst_e_eng5',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_gyarb__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i gymnasiearbete',
        'sid': 'andel_minst_e_gyarb',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_hist1__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i Historia 1',
        'sid': 'andel_minst_e_hist1',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_idr1__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i Idrott 1',
        'sid': 'andel_minst_e_idr1',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_ma1__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i Matematik 1',
        'sid': 'andel_minst_e_ma1',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_na1__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i Naturkunskap 1',
        'sid': 'andel_minst_e_na1',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_re1__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i Religion 1',
        'sid': 'andel_minst_e_re1',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_sam1__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i Samhällskunskap 1',
        'sid': 'andel_minst_e_sam1',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_sv1__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i Svenska 1',
        'sid': 'andel_minst_e_sv1',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_minst_e_sva1__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel avgångselever med minst betyget E i Svenska som andraspråk 1',
        'sid': 'andel_minst_e_sva1',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_natt_malen_alla_amnen__139',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen',
        'sid': 'andel_natt_malen_alla_amnen',
        'table': '139',
        'table_name': 'Slutbetyg årskurs 9, samtliga elever',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_natt_malen_alla_exklok__139',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel som uppnått kunskapskraven i alla ämnen exklusive okänd bakgrund',
        'sid': 'andel_natt_malen_alla_exklok',
        'table': '139',
        'table_name': 'Slutbetyg årskurs 9, samtliga elever',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_poj__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel pojkar',
        'sid': 'andel_poj',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_pojkar__95',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) pojkar',
        'sid': 'andel_pojkar',
        'table': '95',
        'table_name': 'Salsa, skolenheters resultat av slutbetygen i årskurs 9 med hänsyn till elevsammansättningen',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_samma_prog_inom_3__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever som startat och slutfört utbildningen inom samma program inom 3 år',
        'sid': 'andel_samma_prog_inom_3',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_samma_prog_inom_4__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever som startat och slutfört utbildningen inom samma program inom 4 år',
        'sid': 'andel_samma_prog_inom_4',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_samma_prog_inom_5__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever som startat och slutfört utbildningen inom samma program inom 5 år',
        'sid': 'andel_samma_prog_inom_5',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_sankt__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med lägre kursbetyg än provbetyg i ämnet',
        'sid': 'andel_sankt',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_sankt_kvi__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med lägre kursbetyg än provbetyg i ämnet, kvinnor',
        'sid': 'andel_sankt_kvi',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_sankt_man__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med lägre kursbetyg än provbetyg i ämnet, män',
        'sid': 'andel_sankt_man',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_studerar_ett__185',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel ungdomar som studerar ett år efter gymnasiestudier',
        'sid': 'andel_studerar_ett',
        'table': '185',
        'table_name': 'Vad ungdomar gör efter gymnasieskolan - ett, tre eller fem år efter gymnasiestudier, LGY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_studerar_ett__97',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel ungdomar som studerar ett år efter gymnasiestudier',
        'sid': 'andel_studerar_ett',
        'table': '97',
        'table_name': 'Vad ungdomar gör efter gymnasieskolan - ett, tre eller fem år efter gymnasiestudier',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_studerar_tre__97',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel ungdomar som studerar tre år efter gymnasiestudier',
        'sid': 'andel_studerar_tre',
        'table': '97',
        'table_name': 'Vad ungdomar gör efter gymnasieskolan - ett, tre eller fem år efter gymnasiestudier',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_studiebevis_inom_3__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever som slutfört utbildningen med studiebevis om 2500 poäng inom 3 år',
        'sid': 'andel_studiebevis_inom_3',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_studiebevis_inom_4__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever som slutfört utbildningen med studiebevis om 2500 poäng inom 4 år',
        'sid': 'andel_studiebevis_inom_4',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_studiebevis_inom_5__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever som slutfört utbildningen med studiebevis om 2500 poäng inom 5 år',
        'sid': 'andel_studiebevis_inom_5',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel svensk bakgrund',
        'sid': 'andel_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_uppnatt_alla__143',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som uppnått kunskapskraven (A-E) i alla ämnen',
        'sid': 'andel_uppnatt_alla',
        'table': '143',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), samtliga elever',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_uppnatt_alla_exkl__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som uppnått kunskapskraven (A-E) i alla ämnen, exklusive nyinvandrade och okänd bakgrund',
        'sid': 'andel_uppnatt_alla_exkl',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_uppnatt_alla_fli__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som uppnått kunskapskraven (A-E) i alla ämnen, flickor',
        'sid': 'andel_uppnatt_alla_fli',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_uppnatt_alla_poj__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som uppnått kunskapskraven (A-E) i alla ämnen, pojkar',
        'sid': 'andel_uppnatt_alla_poj',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_uppnatt_alla_tot__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som uppnått kunskapskraven (A-E) i alla ämnen, totalt',
        'sid': 'andel_uppnatt_alla_tot',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_utl__70',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med utländsk bakgrund',
        'sid': 'andel_utl',
        'table': '70',
        'table_name': 'Antal elever som började 2011 eller senare, per program och inriktning',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_utl__136',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med utländsk bakgrund',
        'sid': 'andel_utl',
        'table': '136',
        'table_name': 'Antal elever',
        'unit': 'Prc'
    },
    {
        'concept': 'andel_utl__21',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Andel elever med utländsk bakgrund',
        'sid': 'andel_utl',
        'table': '21',
        'table_name': 'Antal elever som började 2011 eller senare, per program',
        'unit': 'Prc'
    },
    {
        'concept': 'ant_af_fli__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal flickor med provbetyget A-F',
        'sid': 'ant_af_fli',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'No'
    },
    {
        'concept': 'ant_af_poj__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal pojkar med provbetyget A-F',
        'sid': 'ant_af_poj',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'No'
    },
    {
        'concept': 'ant_af_tot__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever med provbetyget A-F',
        'sid': 'ant_af_tot',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'No'
    },
    {
        'concept': 'ant_amnen_medel__143',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt antal ämnesbetyg',
        'sid': 'ant_amnen_medel',
        'table': '143',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), samtliga elever',
        'unit': 'No'
    },
    {
        'concept': 'ant_amnen_medel_exkl__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt antal ämnesbetyg exklusive nyinvandrade',
        'sid': 'ant_amnen_medel_exkl',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'No'
    },
    {
        'concept': 'ant_amnen_medel_fli__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt antal ämnesbetyg, flickor',
        'sid': 'ant_amnen_medel_fli',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'No'
    },
    {
        'concept': 'ant_amnen_medel_poj__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt antal ämnesbetyg, pojkar',
        'sid': 'ant_amnen_medel_poj',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'No'
    },
    {
        'concept': 'ant_amnen_medel_tot__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt antal ämnesbetyg, totalt',
        'sid': 'ant_amnen_medel_tot',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'No'
    },
    {
        'concept': 'ant_behoriga__106',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal lärare med lärarlegitimation och behörighet i ämnet',
        'sid': 'ant_behoriga',
        'table': '106',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_behoriga__102',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal lärare med lärarlegitimation och behörighet i ämnet',
        'sid': 'ant_behoriga',
        'table': '102',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_behoriga__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal lärare med lärarlegitimation och behörighet i minst ett ämne, alla tjänstgörande lärare',
        'sid': 'ant_behoriga',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_behoriga__263',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal lärare med lärarlegitimation och behörighet i ämnet',
        'sid': 'ant_behoriga',
        'table': '263',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne, yrkesämnen',
        'unit': 'No'
    },
    {
        'concept': 'ant_behoriga__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal lärare med lärarlegitimation och behörighet i minst ett ämne',
        'sid': 'ant_behoriga',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_forstelarare__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal tjänstgörande förstelärare',
        'sid': 'ant_forstelarare',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_forstelarare__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal tjänstgörande förstelärare',
        'sid': 'ant_forstelarare',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Totalt antal tjänstgörande lärare',
        'sid': 'ant_larare',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare__106',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Totalt antal tjänstgörande lärare i ämnet',
        'sid': 'ant_larare',
        'table': '106',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare__102',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Totalt antal tjänstgörande lärare i ämnet',
        'sid': 'ant_larare',
        'table': '102',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Totalt antal tjänstgörande lärare',
        'sid': 'ant_larare',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare__263',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Totalt antal tjänstgörande lärare i ämnet',
        'sid': 'ant_larare',
        'table': '263',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne, yrkesämnen',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare_pedex__102',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal lärare med pedagogisk högskoleexamen i ämnet, alla tjänstgörande lärare',
        'sid': 'ant_larare_pedex',
        'table': '102',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare_pedex__106',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal lärare med pedagogisk högskoleexamen, alla tjänstgörande lärare',
        'sid': 'ant_larare_pedex',
        'table': '106',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare_pedex__263',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal lärare med pedagogisk högskoleexamen, alla tjänstgörande lärare',
        'sid': 'ant_larare_pedex',
        'table': '263',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne, yrkesämnen',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare_pedex__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal lärare med pedagogisk högskoleexamen, alla tjänstgörande lärare',
        'sid': 'ant_larare_pedex',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_larare_pedex__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal lärare med pedagogisk högskoleexamen, alla tjänstgörande lärare',
        'sid': 'ant_larare_pedex',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'ant_slutat__97',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal ungdomar som avslutade studierna detta år',
        'sid': 'ant_slutat',
        'table': '97',
        'table_name': 'Vad ungdomar gör efter gymnasieskolan - ett, tre eller fem år efter gymnasiestudier',
        'unit': 'No'
    },
    {
        'concept': 'ant_slutat__185',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal ungdomar som avslutade studierna detta år',
        'sid': 'ant_slutat',
        'table': '185',
        'table_name': 'Vad ungdomar gör efter gymnasieskolan - ett, tre eller fem år efter gymnasiestudier, LGY11',
        'unit': 'No'
    },
    {
        'concept': 'antal_eftgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever, föräldrar eftergymnasial utbildning',
        'sid': 'antal_eftgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever__5',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever',
        'sid': 'antal_elever',
        'table': '5',
        'table_name': 'Behörighet till gymnasieskolan, fr.o.m. 2011',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever__139',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever',
        'sid': 'antal_elever',
        'table': '139',
        'table_name': 'Slutbetyg årskurs 9, samtliga elever',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever__65',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Totalt antal elever',
        'sid': 'antal_elever',
        'table': '65',
        'table_name': 'Kursprovsbetyg, elever som började 2011 eller senare',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Totalt antal elever',
        'sid': 'antal_elever',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Totalt antal elever',
        'sid': 'antal_elever',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever_exklok__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever, exklusive okänd bakgrund',
        'sid': 'antal_elever_exklok',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever_exl__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever exklusive nyinvandrade',
        'sid': 'antal_elever_exl',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever_min4ar__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 9, exklusive nyinvandrade och okänd bakgrund',
        'sid': 'antal_elever_min4ar',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever_min4ar_fli__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 9, exklusive nyinvandrade och okänd bakgrund, flickor',
        'sid': 'antal_elever_min4ar_fli',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever_min4ar_poj__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 9, exklusive nyinvandrade och okänd bakgrund, pojkar',
        'sid': 'antal_elever_min4ar_poj',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever_nyinv__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever nyinvandrade',
        'sid': 'antal_elever_nyinv',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'No'
    },
    {
        'concept': 'antal_elever_samtl__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever, totalt',
        'sid': 'antal_elever_samtl',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'No'
    },
    {
        'concept': 'antal_f_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal utländsk bakgrund födda i Sverige',
        'sid': 'antal_f_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'No'
    },
    {
        'concept': 'antal_f_utl__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal utländsk bakgrund födda utomlands',
        'sid': 'antal_f_utl',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'No'
    },
    {
        'concept': 'antal_fli__93',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal flickor årskurs 9',
        'sid': 'antal_fli',
        'table': '93',
        'table_name': 'Slutbetyg per ämne årskurs 9, fr.o.m. 2013',
        'unit': 'No'
    },
    {
        'concept': 'antal_fli__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal flickor årskurs 9',
        'sid': 'antal_fli',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'No'
    },
    {
        'concept': 'antal_forgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever, föräldrar förgymnasial utbildning',
        'sid': 'antal_forgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'No'
    },
    {
        'concept': 'antal_gy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever, föräldrar gymnasieutbildning',
        'sid': 'antal_gy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'No'
    },
    {
        'concept': 'antal_kvi__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal kvinnor',
        'sid': 'antal_kvi',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'No'
    },
    {
        'concept': 'antal_m_betyg__143',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 6',
        'sid': 'antal_m_betyg',
        'table': '143',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), samtliga elever',
        'unit': 'No'
    },
    {
        'concept': 'antal_m_betyg_exkl__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 6, exklusive nyinvandrade och okänd bakgrund',
        'sid': 'antal_m_betyg_exkl',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'No'
    },
    {
        'concept': 'antal_m_betyg_fli__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 6, flickor',
        'sid': 'antal_m_betyg_fli',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'No'
    },
    {
        'concept': 'antal_m_betyg_poj__144',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 6, pojkar',
        'sid': 'antal_m_betyg_poj',
        'table': '144',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), per kön',
        'unit': 'No'
    },
    {
        'concept': 'antal_m_betyg_tot__145',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 6, totalt',
        'sid': 'antal_m_betyg_tot',
        'table': '145',
        'table_name': 'Betyg årskurs 6, andel som uppnått kunskapskraven (A-E), med/utan nyinvandrade och okänd bakgrund',
        'unit': 'No'
    },
    {
        'concept': 'antal_man__55',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal män',
        'sid': 'antal_man',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': 'No'
    },
    {
        'concept': 'antal_poj__93',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal pojkar i ämnet årskurs 9',
        'sid': 'antal_poj',
        'table': '93',
        'table_name': 'Slutbetyg per ämne årskurs 9, fr.o.m. 2013',
        'unit': 'No'
    },
    {
        'concept': 'antal_poj__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal pojkar årskurs 9',
        'sid': 'antal_poj',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'No'
    },
    {
        'concept': 'antal_slutbetyg__54',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever med slutbetyg',
        'sid': 'antal_slutbetyg',
        'table': '54',
        'table_name': 'Slutbetyg och behörighet, per program (t.o.m. 2012/13)',
        'unit': 'No'
    },
    {
        'concept': 'antal_startat__90',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever som startat programmet',
        'sid': 'antal_startat',
        'table': '90',
        'table_name': 'Genomströmning inom 3, 4 och 5 år, GY11',
        'unit': 'No'
    },
    {
        'concept': 'antal_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal svensk bakgrund',
        'sid': 'antal_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'No'
    },
    {
        'concept': 'antal_tot__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 9',
        'sid': 'antal_tot',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'No'
    },
    {
        'concept': 'antal_tot__93',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i ämnet årskurs 9',
        'sid': 'antal_tot',
        'table': '93',
        'table_name': 'Slutbetyg per ämne årskurs 9, fr.o.m. 2013',
        'unit': 'No'
    },
    {
        'concept': 'ar1__21',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever år 1',
        'sid': 'ar1',
        'table': '21',
        'table_name': 'Antal elever som började 2011 eller senare, per program',
        'unit': 'No'
    },
    {
        'concept': 'ar1__136',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever år 1',
        'sid': 'ar1',
        'table': '136',
        'table_name': 'Antal elever',
        'unit': 'No'
    },
    {
        'concept': 'ar1__70',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever år 1',
        'sid': 'ar1',
        'table': '70',
        'table_name': 'Antal elever som började 2011 eller senare, per program och inriktning',
        'unit': 'No'
    },
    {
        'concept': 'ar2__70',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever år 2',
        'sid': 'ar2',
        'table': '70',
        'table_name': 'Antal elever som började 2011 eller senare, per program och inriktning',
        'unit': 'No'
    },
    {
        'concept': 'ar2__21',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever år 2',
        'sid': 'ar2',
        'table': '21',
        'table_name': 'Antal elever som började 2011 eller senare, per program',
        'unit': 'No'
    },
    {
        'concept': 'ar2__136',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever år 2',
        'sid': 'ar2',
        'table': '136',
        'table_name': 'Antal elever',
        'unit': 'No'
    },
    {
        'concept': 'ar3__70',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever år 3',
        'sid': 'ar3',
        'table': '70',
        'table_name': 'Antal elever som började 2011 eller senare, per program och inriktning',
        'unit': 'No'
    },
    {
        'concept': 'ar3__136',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever år 3',
        'sid': 'ar3',
        'table': '136',
        'table_name': 'Antal elever',
        'unit': 'No'
    },
    {
        'concept': 'ar3__21',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever år 3',
        'sid': 'ar3',
        'table': '21',
        'table_name': 'Antal elever som började 2011 eller senare, per program',
        'unit': 'No'
    },
    {
        'concept': 'ber_and_uppn_malen__95',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Modell- beräknat värde (B) för andel (%) som uppnått kunskapskraven',
        'sid': 'ber_and_uppn_malen',
        'table': '95',
        'table_name': 'Salsa, skolenheters resultat av slutbetygen i årskurs 9 med hänsyn till elevsammansättningen',
        'unit': 'Prc'
    },
    {
        'concept': 'ber_meritvarde__95',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Modell- beräknat värde (B) för genomsnittligt meritvärde',
        'sid': 'ber_meritvarde',
        'table': '95',
        'table_name': 'Salsa, skolenheters resultat av slutbetygen i årskurs 9 med hänsyn till elevsammansättningen',
        'unit': 'Scale'
    },
    {
        'concept': 'betpoang_fli__93',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Betygspoäng flickor',
        'sid': 'betpoang_fli',
        'table': '93',
        'table_name': 'Slutbetyg per ämne årskurs 9, fr.o.m. 2013',
        'unit': 'Scale'
    },
    {
        'concept': 'betpoang_poj__93',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Betygspoäng pojkar',
        'sid': 'betpoang_poj',
        'table': '93',
        'table_name': 'Slutbetyg per ämne årskurs 9, fr.o.m. 2013',
        'unit': 'Scale'
    },
    {
        'concept': 'betpoang_tot__93',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Betygspoäng totalt',
        'sid': 'betpoang_tot',
        'table': '93',
        'table_name': 'Slutbetyg per ämne årskurs 9, fr.o.m. 2013',
        'unit': 'Scale'
    },
    {
        'concept': 'bi_andel_hojt__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med högre slutbetyg jämfört med provbetyget, biologi',
        'sid': 'bi_andel_hojt',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'bi_andel_lika__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lika slutbetyg jämfört med provbetyget, biologi',
        'sid': 'bi_andel_lika',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'bi_andel_sankt__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lägre slutbetyg jämfört med provbetyget, biologi',
        'sid': 'bi_andel_sankt',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'bi_antal_m_betyg__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever med provbetyg och slutbetyg, biologi',
        'sid': 'bi_antal_m_betyg',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'No'
    },
    {
        'concept': 'delprov__49',
        'concept_type': 'entity_domain',
        'form': '11',
        'name': 'Delprov',
        'sid': 'delprov',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': None
    },
    {
        'concept': 'delprovsnamn__12',
        'concept_type': 'entity_domain',
        'form': '11',
        'name': 'Delprovsnamn',
        'sid': 'delprovsnamn',
        'table': '12',
        'table_name': 'Resultat nationella prov årskurs 3',
        'unit': None
    },
    {
        'concept': 'elever_789_per_syv__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 7-9 per studie- och yrkesvägledare, heltidstjänster',
        'sid': 'elever_789_per_syv',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'Frac'
    },
    {
        'concept': 'elever_per_helttj__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever per heltidstjänst',
        'sid': 'elever_per_helttj',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': None
    },
    {
        'concept': 'elever_per_larare__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever per lärare, heltidstjänster',
        'sid': 'elever_per_larare',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'Frac'
    },
    {
        'concept': 'elever_per_syv__16',
        'concept_type': 'string',
        'form': '11',
        'name': 'Antal elever per studie- och yrkesvägledare, heltidstjänster',
        'sid': 'elever_per_syv',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'Frac'
    },
    {
        'concept': 'elever_per_syvhelttj__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal elever per studie- och yrkesvägledare',
        'sid': 'elever_per_syvhelttj',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': None
    },
    {
        'concept': 'en_andel_hojt__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med högre slutbetyg i engelska jämfört med provbetyget',
        'sid': 'en_andel_hojt',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'en_andel_hojt__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med högre slutbetyg i engelska jämfört med provbetyget',
        'sid': 'en_andel_hojt',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'en_andel_hojt__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med högre slutbetyg i engelska jämfört med provbetyget',
        'sid': 'en_andel_hojt',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'en_andel_lika__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lika slutbetyg i engelska jämfört med provbetyget',
        'sid': 'en_andel_lika',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'en_andel_lika__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lika slutbetyg i engelska jämfört med provbetyget',
        'sid': 'en_andel_lika',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'en_andel_lika__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med lika slutbetyg i engelska jämfört med provbetyget',
        'sid': 'en_andel_lika',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'en_andel_sankt__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lägre slutbetyg i engelska jämfört med provbetyget',
        'sid': 'en_andel_sankt',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'en_andel_sankt__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med lägre slutbetyg i engelska jämfört med provbetyget',
        'sid': 'en_andel_sankt',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'en_andel_sankt__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lägre slutbetyg i engelska jämfört med provbetyget',
        'sid': 'en_andel_sankt',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'en_antal_m_betyg__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 9 med provbetyg och slutbetyg i engelska',
        'sid': 'en_antal_m_betyg',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'No'
    },
    {
        'concept': 'en_antal_m_betyg__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 6 med provbetyg och slutbetyg i engelska',
        'sid': 'en_antal_m_betyg',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'No'
    },
    {
        'concept': 'en_antal_m_betyg__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 9 med provbetyg och slutbetyg i engelska',
        'sid': 'en_antal_m_betyg',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'No'
    },
    {
        'concept': 'fklass_andel_fli__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) flickor förskoleklass',
        'sid': 'fklass_andel_fli',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'Prc'
    },
    {
        'concept': 'fklass_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever förskoleklass',
        'sid': 'fklass_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'fli_andel_ae__193',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) i nationella provets delprov, flickor',
        'sid': 'fli_andel_ae',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Prc'
    },
    {
        'concept': 'fli_andel_ae__199',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) i nationella provet för ämnet, flickor',
        'sid': 'fli_andel_ae',
        'table': '199',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Biologi, Fysik och Kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'fli_andel_ae__196',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) nationella provet för ämnet, flickor',
        'sid': 'fli_andel_ae',
        'table': '196',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Prc'
    },
    {
        'concept': 'fli_andel_ae__71',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som uppnått kunskapskraven (A-E) i ämnet, flickor',
        'sid': 'fli_andel_ae',
        'table': '71',
        'table_name': 'Betyg per ämne årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'fli_andel_ae__200',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) i nationella provet för ämnet, flickor',
        'sid': 'fli_andel_ae',
        'table': '200',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Geografi, Historia, Religionskunskap, Samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'fli_gbp__196',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 9, flickor',
        'sid': 'fli_gbp',
        'table': '196',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'fli_gbp__200',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 9, flickor',
        'sid': 'fli_gbp',
        'table': '200',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Geografi, Historia, Religionskunskap, Samhällskunskap',
        'unit': 'Scale'
    },
    {
        'concept': 'fli_gbp__199',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 9, flickor',
        'sid': 'fli_gbp',
        'table': '199',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Biologi, Fysik och Kemi',
        'unit': 'Scale'
    },
    {
        'concept': 'fli_gbp__193',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provets delprov för ämnet för elever i årskurs 9, flickor',
        'sid': 'fli_gbp',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'fli_gbp__71',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i ämnet för elever i årskurs 6, flickor',
        'sid': 'fli_gbp',
        'table': '71',
        'table_name': 'Betyg per ämne årskurs 6',
        'unit': 'Scale'
    },
    {
        'concept': 'fli_m_betyg__71',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal flickor med betyg i ämnet årskurs 6',
        'sid': 'fli_m_betyg',
        'table': '71',
        'table_name': 'Betyg per ämne årskurs 6',
        'unit': 'Scale'
    },
    {
        'concept': 'fli_m_betyg__196',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal flickor som deltagit i nationella provet i ämnet årskurs 9',
        'sid': 'fli_m_betyg',
        'table': '196',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'fli_m_betyg__200',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal flickor som deltagit i nationella provet i ämnet årskurs 9',
        'sid': 'fli_m_betyg',
        'table': '200',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Geografi, Historia, Religionskunskap, Samhällskunskap',
        'unit': 'Scale'
    },
    {
        'concept': 'fli_m_betyg__199',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal flickor som deltagit i nationella provet i ämnet årskurs 9',
        'sid': 'fli_m_betyg',
        'table': '199',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Biologi, Fysik och Kemi',
        'unit': 'Scale'
    },
    {
        'concept': 'fli_m_betyg__193',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal flickor som deltagit i nationella provets delprov i ämnet årskurs 9',
        'sid': 'fli_m_betyg',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'foraldr_utb__95',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Föräldrarnas genomsnittliga utbildningsnivå',
        'sid': 'foraldr_utb',
        'table': '95',
        'table_name': 'Salsa, skolenheters resultat av slutbetygen i årskurs 9 med hänsyn till elevsammansättningen',
        'unit': 'Scale'
    },
    {
        'concept': 'fy_andel_hojt__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med högre slutbetyg jämfört med provbetyget, fysik',
        'sid': 'fy_andel_hojt',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'fy_andel_lika__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lika slutbetyg jämfört med provbetyget, fysik',
        'sid': 'fy_andel_lika',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'fy_andel_sankt__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lägre slutbetyg jämfört med provbetyget, fysik',
        'sid': 'fy_andel_sankt',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'fy_antal_m_betyg__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever med provbetyg och slutbetyg, fysik',
        'sid': 'fy_antal_m_betyg',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'No'
    },
    {
        'concept': 'gbp__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Genomsnittligt betygspoäng för elever med examen eller studiebevis',
        'sid': 'gbp',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': None
    },
    {
        'concept': 'gbp__54',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Genomsnittligt betygspoäng',
        'sid': 'gbp',
        'table': '54',
        'table_name': 'Slutbetyg och behörighet, per program (t.o.m. 2012/13)',
        'unit': None
    },
    {
        'concept': 'gbp_examen__88',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Genomsnittligt betygspoäng för elever med examen',
        'sid': 'gbp_examen',
        'table': '88',
        'table_name': 'Avgångselever, nationella program (fr.o.m. 2013/14)',
        'unit': None
    },
    {
        'concept': 'gbp_fli__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng, flickor',
        'sid': 'gbp_fli',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'Scale'
    },
    {
        'concept': 'gbp_poj__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng, pojkar',
        'sid': 'gbp_poj',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'Scale'
    },
    {
        'concept': 'gbp_tot__49',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng, totalt',
        'sid': 'gbp_tot',
        'table': '49',
        'table_name': 'Resultat nationella prov årskurs 6',
        'unit': 'Scale'
    },
    {
        'concept': 'ge_andel_hojt__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med högre slutbetyg jämfört med provbetyget, geografi',
        'sid': 'ge_andel_hojt',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'ge_andel_lika__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lika slutbetyg jämfört med provbetyget, geografi',
        'sid': 'ge_andel_lika',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'ge_andel_sankt__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lägre slutbetyg jämfört med provbetyget, geografi',
        'sid': 'ge_andel_sankt',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'ge_antal_m_betyg__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever med provbetyg och slutbetyg, geografi',
        'sid': 'ge_antal_m_betyg',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'No'
    },
    {
        'concept': 'gmv_eftgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (16), föräldrar eftergymnasial utbildning',
        'sid': 'gmv_eftgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_exklok__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde årskurs 9, exklusive nyinvandrade',
        'sid': 'gmv_exklok',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_exl__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (16), exklusive nyinvandrade',
        'sid': 'gmv_exl',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_f_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (17), utländsk bakgrund födda i Sverige',
        'sid': 'gmv_f_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_f_utl__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (17), utländsk bakgrund födda utomlands',
        'sid': 'gmv_f_utl',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_fli__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (17), flickor',
        'sid': 'gmv_fli',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_forgy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (16), föräldrar förgymnasial utbildning',
        'sid': 'gmv_forgy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_gy__26',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (16), föräldrar gymnasieutbildning',
        'sid': 'gmv_gy',
        'table': '26',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per föräldrarnas högsta utbildningsnivå',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_min4ar__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde årskurs 9, exklusive nyinvandrade och okänd bakgrund',
        'sid': 'gmv_min4ar',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_min4ar_fli__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde årskurs 9, exklusive nyinvandrade och okänd bakgrund, flickor',
        'sid': 'gmv_min4ar_fli',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_min4ar_poj__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde årskurs 9, exklusive nyinvandrade och okänd bakgrund, pojkar',
        'sid': 'gmv_min4ar_poj',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_nyinv__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (16), nyinvandrade',
        'sid': 'gmv_nyinv',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_poj__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (17), pojkar',
        'sid': 'gmv_poj',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_samtl__110',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde årskurs 9, totalt',
        'sid': 'gmv_samtl',
        'table': '110',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_sv__25',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (17), svensk bakgrund',
        'sid': 'gmv_sv',
        'table': '25',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per svensk och utländsk bakgrund',
        'unit': 'Scale'
    },
    {
        'concept': 'gmv_tot__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (17), totalt',
        'sid': 'gmv_tot',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Scale'
    },
    {
        'concept': 'gnm_betp__65',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Genomsnittligt provbetygspoäng',
        'sid': 'gnm_betp',
        'table': '65',
        'table_name': 'Kursprovsbetyg, elever som började 2011 eller senare',
        'unit': None
    },
    {
        'concept': 'gnm_meritvarde__139',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (17)',
        'sid': 'gnm_meritvarde',
        'table': '139',
        'table_name': 'Slutbetyg årskurs 9, samtliga elever',
        'unit': 'Scale'
    },
    {
        'concept': 'gnm_meritvarde_exklok__139',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde (17 exklusive okänd bakgrund',
        'sid': 'gnm_meritvarde_exklok',
        'table': '139',
        'table_name': 'Slutbetyg årskurs 9, samtliga elever',
        'unit': 'Scale'
    },
    {
        'concept': 'gnm_meritvarde_exklok_fli__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde årskurs 9, exklusive nyinvandrade, flickor',
        'sid': 'gnm_meritvarde_exklok_fli',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Scale'
    },
    {
        'concept': 'gnm_meritvarde_exklok_poj__140',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt meritvärde årskurs 9, exklusive nyinvandrade, pojkar',
        'sid': 'gnm_meritvarde_exklok_poj',
        'table': '140',
        'table_name': 'Slutbetyg årskurs 9, uppdelat per kön',
        'unit': 'Scale'
    },
    {
        'concept': 'helttj_adm__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal rektorstjänster, heltid',
        'sid': 'helttj_adm',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'No'
    },
    {
        'concept': 'helttj_adm__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal rektorer, heltidstjänster',
        'sid': 'helttj_adm',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': None
    },
    {
        'concept': 'helttj_andel_kvi__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel kvinnliga anställda, heltidstjänster',
        'sid': 'helttj_andel_kvi',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'Prc'
    },
    {
        'concept': 'helttj_andel_kvi__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster andel kvinnor',
        'sid': 'helttj_andel_kvi',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': 'Prc'
    },
    {
        'concept': 'helttj_andel_ped__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel anställda med pedagogisk högskoleexamen, heltidstjänster',
        'sid': 'helttj_andel_ped',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'Prc'
    },
    {
        'concept': 'helttj_andel_ped__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster andel med pedagogisk högskoleexamen',
        'sid': 'helttj_andel_ped',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': 'Prc'
    },
    {
        'concept': 'helttj_andel_specped__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel anställda med specialpedagogisk högskoleexamen, heltidstjänster',
        'sid': 'helttj_andel_specped',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'Prc'
    },
    {
        'concept': 'helttj_andel_specped__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster andel med specialpedagogisk högskoleexamen',
        'sid': 'helttj_andel_specped',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': 'Prc'
    },
    {
        'concept': 'helttj_andel_tillsv__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster andel tillsvidareanställda',
        'sid': 'helttj_andel_tillsv',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': 'Prc'
    },
    {
        'concept': 'helttj_andel_tillsv__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel tillsvidareanställda',
        'sid': 'helttj_andel_tillsv',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'Prc'
    },
    {
        'concept': 'helttj_forstelarare__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal förstelärare, heltidstjänster',
        'sid': 'helttj_forstelarare',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'helttj_forstelarare__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal förstelärare, heltidstjänster',
        'sid': 'helttj_forstelarare',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'helttj_larare__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal heltidsjänster lärare',
        'sid': 'helttj_larare',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'No'
    },
    {
        'concept': 'helttj_larare__106',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster lärare',
        'sid': 'helttj_larare',
        'table': '106',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': None
    },
    {
        'concept': 'helttj_larare__263',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster lärare',
        'sid': 'helttj_larare',
        'table': '263',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne, yrkesämnen',
        'unit': None
    },
    {
        'concept': 'helttj_larare__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster lärare',
        'sid': 'helttj_larare',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': None
    },
    {
        'concept': 'helttj_larare__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal heltidsjänster lärare',
        'sid': 'helttj_larare',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'helttj_larare__102',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal heltidsjänster lärare i ämnet',
        'sid': 'helttj_larare',
        'table': '102',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'No'
    },
    {
        'concept': 'helttj_larare__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster lärare',
        'sid': 'helttj_larare',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': None
    },
    {
        'concept': 'helttj_larare_leg__106',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal heltidstjänster lärare med lärarlegitimation och behörighet i minst ett ämne',
        'sid': 'helttj_larare_leg',
        'table': '106',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': None
    },
    {
        'concept': 'helttj_larare_leg__263',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal heltidstjänster lärare med lärarlegitimation och behörighet i minst ett ämne',
        'sid': 'helttj_larare_leg',
        'table': '263',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne, yrkesämnen',
        'unit': None
    },
    {
        'concept': 'helttj_larare_leg__101',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal heltidsjänster med lärarlegitimation och behörighet i minst ett ämne',
        'sid': 'helttj_larare_leg',
        'table': '101',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': 'No'
    },
    {
        'concept': 'helttj_larare_leg__105',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Antal heltidstjänster lärare med lärarlegitimation och behörighet i ämnet',
        'sid': 'helttj_larare_leg',
        'table': '105',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet i minst ett ämne',
        'unit': None
    },
    {
        'concept': 'helttj_larare_leg__102',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal heltidsjänster med lärarlegitimation och behörighet i ämnet',
        'sid': 'helttj_larare_leg',
        'table': '102',
        'table_name': 'Personalstatistik med lärarlegitimation och behörighet per ämne',
        'unit': 'No'
    },
    {
        'concept': 'helttj_larare_o_adm__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal lärar- och rektorstjänster, heltid',
        'sid': 'helttj_larare_o_adm',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'No'
    },
    {
        'concept': 'helttj_larare_o_adm__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster antal lärare och rektorer',
        'sid': 'helttj_larare_o_adm',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': None
    },
    {
        'concept': 'helttj_syv__16',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal studie- och yrkesvägledartjänster, heltid',
        'sid': 'helttj_syv',
        'table': '16',
        'table_name': 'Personalstatistik',
        'unit': 'No'
    },
    {
        'concept': 'helttj_syv__17',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Heltidstjänster antal studie- och yrkesvägledare',
        'sid': 'helttj_syv',
        'table': '17',
        'table_name': 'Personalstatistik',
        'unit': 'No'
    },
    {
        'concept': 'hi_andel_hojt__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med högre slutbetyg jämfört med provbetyget, historia',
        'sid': 'hi_andel_hojt',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'hi_andel_lika__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lika slutbetyg jämfört med provbetyget, historia',
        'sid': 'hi_andel_lika',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'hi_andel_sankt__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lägre slutbetyg jämfört med provbetyget, historia',
        'sid': 'hi_andel_sankt',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'hi_antal_m_betyg__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever med provbetyg och slutbetyg, historia',
        'sid': 'hi_antal_m_betyg',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'No'
    },
    {
        'concept': 'huvudman',
        'concept_type': 'string',
        'form': '11',
        'name': 'Huvudman',
        'sid': 'huvudman',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'huvudman__185',
        'concept_type': 'string',
        'form': '21',
        'name': 'Huvudman',
        'sid': 'huvudman',
        'table': '185',
        'table_name': 'Vad ungdomar gör efter gymnasieskolan - ett, tre eller fem år efter gymnasiestudier, LGY11',
        'unit': None
    },
    {
        'concept': 'huvudman_namn',
        'concept_type': 'string',
        'form': '11',
        'name': 'Huvudmannens namn',
        'sid': 'huvudman_namn',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'huvudman_namn__55',
        'concept_type': 'string',
        'form': '21',
        'name': 'Huvudmannens namn',
        'sid': 'huvudman_namn',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': None
    },
    {
        'concept': 'inriktning__70',
        'concept_type': 'entity_domain',
        'form': '21',
        'name': 'Inriktning',
        'sid': 'inriktning',
        'table': '70',
        'table_name': 'Antal elever som började 2011 eller senare, per program och inriktning',
        'unit': None
    },
    {
        'concept': 'ke_andel_hojt__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med högre slutbetyg jämfört med provbetyget, kemi',
        'sid': 'ke_andel_hojt',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'ke_andel_lika__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lika slutbetyg jämfört med provbetyget, kemi',
        'sid': 'ke_andel_lika',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'ke_andel_sankt__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lägre slutbetyg jämfört med provbetyget, kemi',
        'sid': 'ke_andel_sankt',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'ke_antal_m_betyg__4',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever med provbetyg och slutbetyg, kemi',
        'sid': 'ke_antal_m_betyg',
        'table': '4',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, biologi, fysik och kemi',
        'unit': 'No'
    },
    {
        'concept': 'kommun__54',
        'concept_type': 'string',
        'form': '21',
        'name': 'Kommun',
        'sid': 'kommun',
        'table': '54',
        'table_name': 'Slutbetyg och behörighet, per program (t.o.m. 2012/13)',
        'unit': None
    },
    {
        'concept': 'kommun',
        'concept_type': 'string',
        'form': '11',
        'name': 'Kommun',
        'sid': 'kommun',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'kommunnamn',
        'concept_type': 'string',
        'alt_spelling': 'kommun_namn',
        'form': '11',
        'name': 'Kommunens namn',
        'sid': 'kommunnamn',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'kon',
        'concept_type': 'entity_domain',
        'form': None,
        'name': 'Kön',
        'sid': 'kon',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'lageskommun__136',
        'concept_type': 'string',
        'form': '21',
        'name': 'Lägeskommun',
        'sid': 'lageskommun',
        'table': '136',
        'table_name': 'Antal elever',
        'unit': None
    },
    {
        'concept': 'ma_andel_hojt__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med högre slutbetyg i matematik jämfört med provbetyget',
        'sid': 'ma_andel_hojt',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'ma_andel_hojt__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med högre slutbetyg i matematik jämfört med provbetyget',
        'sid': 'ma_andel_hojt',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'ma_andel_hojt__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med högre slutbetyg i matematik jämfört med provbetyget',
        'sid': 'ma_andel_hojt',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'ma_andel_lika__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lika slutbetyg i matematik jämfört med provbetyget',
        'sid': 'ma_andel_lika',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'ma_andel_lika__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lika slutbetyg i matematik jämfört med provbetyget',
        'sid': 'ma_andel_lika',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'ma_andel_lika__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med lika slutbetyg i matematik jämfört med provbetyget',
        'sid': 'ma_andel_lika',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'ma_andel_sankt__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med lägre slutbetyg i matematik jämfört med provbetyget',
        'sid': 'ma_andel_sankt',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'ma_andel_sankt__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lägre slutbetyg i matematik jämfört med provbetyget',
        'sid': 'ma_andel_sankt',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'ma_andel_sankt__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lägre slutbetyg i matematik jämfört med provbetyget',
        'sid': 'ma_andel_sankt',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'ma_antal_m_betyg__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 9 med provbetyg och slutbetyg i matematik',
        'sid': 'ma_antal_m_betyg',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'No'
    },
    {
        'concept': 'ma_antal_m_betyg__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 6 med provbetyg och slutbetyg i matematik',
        'sid': 'ma_antal_m_betyg',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'No'
    },
    {
        'concept': 'ma_antal_m_betyg__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 9 med provbetyg och slutbetyg i matematik',
        'sid': 'ma_antal_m_betyg',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'No'
    },
    {
        'concept': 'poj_andel_ae__196',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) nationella provet för ämnet, pojkar',
        'sid': 'poj_andel_ae',
        'table': '196',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Prc'
    },
    {
        'concept': 'poj_andel_ae__71',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som uppnått kunskapskraven (A-E) i ämnet, pojkar',
        'sid': 'poj_andel_ae',
        'table': '71',
        'table_name': 'Betyg per ämne årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'poj_andel_ae__199',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) i nationella provet för ämnet, pojkar',
        'sid': 'poj_andel_ae',
        'table': '199',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Biologi, Fysik och Kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'poj_andel_ae__200',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) i nationella provet för ämnet, pojkar',
        'sid': 'poj_andel_ae',
        'table': '200',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Geografi, Historia, Religionskunskap, Samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'poj_andel_ae__193',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) i nationella provets delprov, pojkar',
        'sid': 'poj_andel_ae',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Prc'
    },
    {
        'concept': 'poj_gbp__71',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i ämnet för elever i årskurs 6, pojkar',
        'sid': 'poj_gbp',
        'table': '71',
        'table_name': 'Betyg per ämne årskurs 6',
        'unit': 'Scale'
    },
    {
        'concept': 'poj_gbp__196',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 9, pojkar',
        'sid': 'poj_gbp',
        'table': '196',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'poj_gbp__200',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 9, pojkar',
        'sid': 'poj_gbp',
        'table': '200',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Geografi, Historia, Religionskunskap, Samhällskunskap',
        'unit': 'Scale'
    },
    {
        'concept': 'poj_gbp__199',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 9, pojkar',
        'sid': 'poj_gbp',
        'table': '199',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Biologi, Fysik och Kemi',
        'unit': 'Scale'
    },
    {
        'concept': 'poj_gbp__193',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provets delprov för ämnet för elever i årskurs 9, pojkar',
        'sid': 'poj_gbp',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'poj_m_betyg__196',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal pojkar som deltagit i nationella provet i ämnet årskurs 9',
        'sid': 'poj_m_betyg',
        'table': '196',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'poj_m_betyg__200',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal pojkar som deltagit i nationella provet i ämnet årskurs 9',
        'sid': 'poj_m_betyg',
        'table': '200',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Geografi, Historia, Religionskunskap, Samhällskunskap',
        'unit': 'Scale'
    },
    {
        'concept': 'poj_m_betyg__199',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal pojkar som deltagit i nationella provet i ämnet årskurs 9',
        'sid': 'poj_m_betyg',
        'table': '199',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Biologi, Fysik och Kemi',
        'unit': 'Scale'
    },
    {
        'concept': 'poj_m_betyg__193',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal pojkar som deltagit i nationella provets delprov i ämnet årskurs 9',
        'sid': 'poj_m_betyg',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'poj_m_betyg__71',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal pojkar med betyg i ämnet årskurs 6',
        'sid': 'poj_m_betyg',
        'table': '71',
        'table_name': 'Betyg per ämne årskurs 6',
        'unit': 'Scale'
    },
    {
        'concept': 'program',
        'concept_type': 'entity_domain',
        'form': '21',
        'name': 'Program',
        'sid': 'program',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'prov__55',
        'concept_type': 'entity_domain',
        'form': '21',
        'name': 'Prov',
        'sid': 'prov',
        'table': '55',
        'table_name': 'Relationen mellan kursbetyg och kursprovsbetyg',
        'unit': None
    },
    {
        'concept': 'provkod__193',
        'concept_type': 'entity_domain',
        'form': '11',
        'name': 'Provkod',
        'sid': 'provkod',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': None
    },
    {
        'concept': 'provnamn__12',
        'concept_type': 'entity_domain',
        'form': '11',
        'name': 'Provnamn',
        'sid': 'provnamn',
        'table': '12',
        'table_name': 'Resultat nationella prov årskurs 3',
        'unit': None
    },
    {
        'concept': 'provnamn__193',
        'concept_type': 'entity_domain',
        'form': '11',
        'name': 'Delprovsnamn',
        'sid': 'provnamn',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': None
    },
    {
        'concept': 'provnamn__65',
        'concept_type': 'entity_domain',
        'form': '21',
        'name': 'Provnamn',
        'sid': 'provnamn',
        'table': '65',
        'table_name': 'Kursprovsbetyg, elever som började 2011 eller senare',
        'unit': None
    },
    {
        'concept': 're_andel_hojt__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med högre slutbetyg jämfört med provbetyget, religion',
        'sid': 're_andel_hojt',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 're_andel_lika__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lika slutbetyg jämfört med provbetyget, religion',
        'sid': 're_andel_lika',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 're_andel_sankt__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lägre slutbetyg jämfört med provbetyget, religion',
        'sid': 're_andel_sankt',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 're_antal_m_betyg__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever med provbetyg och slutbetyg, religion',
        'sid': 're_antal_m_betyg',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'No'
    },
    {
        'concept': 'riket_and_natt__12',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 3 i riket som nått kravnivån i nationella provet i ämnet',
        'sid': 'riket_and_natt',
        'table': '12',
        'table_name': 'Resultat nationella prov årskurs 3',
        'unit': 'Prc'
    },
    {
        'concept': 'sa_andel_hojt__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med högre slutbetyg jämfört med provbetyget, samhällskunskap',
        'sid': 'sa_andel_hojt',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'sa_andel_lika__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lika slutbetyg jämfört med provbetyget, samhällskunskap',
        'sid': 'sa_andel_lika',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'sa_andel_sankt__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel (%) elever med lägre slutbetyg jämfört med provbetyget, samhällskunskap',
        'sid': 'sa_andel_sankt',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'sa_antal_m_betyg__123',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever med provbetyg och slutbetyg, samhällskunskap',
        'sid': 'sa_antal_m_betyg',
        'table': '123',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, totalt och per kön, geografi, historia, religionskunskap och samhällskunskap',
        'unit': 'No'
    },
    {
        'concept': 'sal_and_uppn_malen__95',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Residual (R=F-B) för andel som uppnått kunskapskraven',
        'sid': 'sal_and_uppn_malen',
        'table': '95',
        'table_name': 'Salsa, skolenheters resultat av slutbetygen i årskurs 9 med hänsyn till elevsammansättningen',
        'unit': 'Prc'
    },
    {
        'concept': 'sal_meritvarde__95',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Residual (R=F-B) för genomsnittligt meritvärde',
        'sid': 'sal_meritvarde',
        'table': '95',
        'table_name': 'Salsa, skolenheters resultat av slutbetygen i årskurs 9 med hänsyn till elevsammansättningen',
        'unit': 'Scale'
    },
    {
        'concept': 'school',
        'concept_type': 'entity_domain',
        'alt_spelling': 'skol_kod',
        'form': None,
        'name': 'Skolkod',
        'sid': 'skolkod',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'semester',
        'concept_type': 'entity_domain',
        'form': None,
        'name': 'Termin',
        'sid': None,
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'skola_and_natt__12',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 3 i skolan som nått kravnivån i nationella provet i ämnet',
        'sid': 'skola_and_natt',
        'table': '12',
        'table_name': 'Resultat nationella prov årskurs 3',
        'unit': 'Prc'
    },
    {
        'concept': 'skola_ant_elever__12',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever som läser ämnet i årskurs 3',
        'sid': 'skola_ant_elever',
        'table': '12',
        'table_name': 'Resultat nationella prov årskurs 3',
        'unit': 'No'
    },
    {
        'concept': 'skolnamn',
        'concept_type': 'string',
        'alt_spelling': 'skol_namn',
        'form': '11',
        'name': 'Skolnamn',
        'sid': 'skolnamn',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'skolnamn',
        'concept_type': 'string',
        'form': '11',
        'name': 'Skolnamn',
        'sid': 'skola',
        'table': None,
        'table_name': None,
        'unit': None
    },
    {
        'concept': 'sv_andel_hojt__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med högre slutbetyg i svenska jämfört med provbetyget',
        'sid': 'sv_andel_hojt',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sv_andel_hojt__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med högre slutbetyg i svenska jämfört med provbetyget',
        'sid': 'sv_andel_hojt',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'sv_andel_hojt__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med högre slutbetyg i svenska jämfört med provbetyget',
        'sid': 'sv_andel_hojt',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sv_andel_lika__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lika slutbetyg i svenska jämfört med provbetyget',
        'sid': 'sv_andel_lika',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sv_andel_lika__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med lika slutbetyg i svenska jämfört med provbetyget',
        'sid': 'sv_andel_lika',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'sv_andel_lika__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lika slutbetyg i svenska jämfört med provbetyget',
        'sid': 'sv_andel_lika',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sv_andel_sankt__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lägre slutbetyg i svenska jämfört med provbetyget',
        'sid': 'sv_andel_sankt',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sv_andel_sankt__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med lägre slutbetyg i svenska jämfört med provbetyget',
        'sid': 'sv_andel_sankt',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'sv_andel_sankt__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lägre slutbetyg i svenska jämfört med provbetyget',
        'sid': 'sv_andel_sankt',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sv_antal_m_betyg__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 6 med provbetyg och slutbetyg i svenska',
        'sid': 'sv_antal_m_betyg',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'No'
    },
    {
        'concept': 'sv_antal_m_betyg__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 9 med provbetyg och slutbetyg i svenska',
        'sid': 'sv_antal_m_betyg',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'No'
    },
    {
        'concept': 'sv_antal_m_betyg__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 9 med provbetyg och slutbetyg i svenska',
        'sid': 'sv_antal_m_betyg',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'No'
    },
    {
        'concept': 'sva_andel_hojt__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med högre slutbetyg i svenska som andraspråk jämfört med provbetyget',
        'sid': 'sva_andel_hojt',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sva_andel_hojt__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med högre slutbetyg i svenska som andraspråk jämfört med provbetyget',
        'sid': 'sva_andel_hojt',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sva_andel_hojt__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med högre slutbetyg i svenska som andraspråk jämfört med provbetyget',
        'sid': 'sva_andel_hojt',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'sva_andel_lika__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lika slutbetyg i svenska som andraspråk jämfört med provbetyget',
        'sid': 'sva_andel_lika',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sva_andel_lika__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med lika slutbetyg i svenska som andraspråk jämfört med provbetyget',
        'sid': 'sva_andel_lika',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'sva_andel_lika__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lika slutbetyg i svenska som andraspråk jämfört med provbetyget',
        'sid': 'sva_andel_lika',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sva_andel_sankt__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 med lägre slutbetyg i svenska som andraspråk jämfört med provbetyget',
        'sid': 'sva_andel_sankt',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'sva_andel_sankt__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lägre slutbetyg i svenska som andraspråk jämfört med provbetyget',
        'sid': 'sva_andel_sankt',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sva_andel_sankt__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 med lägre slutbetyg i svenska som andraspråk jämfört med provbetyget',
        'sid': 'sva_andel_sankt',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'Prc'
    },
    {
        'concept': 'sva_antal_m_betyg__2',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 9 med provbetyg och slutbetyg i svenska som andraspråk',
        'sid': 'sva_antal_m_betyg',
        'table': '2',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, per kön, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'No'
    },
    {
        'concept': 'sva_antal_m_betyg__1',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 9 med provbetyg och slutbetyg i svenska som andraspråk',
        'sid': 'sva_antal_m_betyg',
        'table': '1',
        'table_name': 'Relationen mellan nationella prov och slutbetyg årskurs 9, svenska/svenska som andraspråk, matematik och engelska',
        'unit': 'No'
    },
    {
        'concept': 'sva_antal_m_betyg__83',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever i årskurs 6 med provbetyg och slutbetyg i svenska som andraspråk',
        'sid': 'sva_antal_m_betyg',
        'table': '83',
        'table_name': 'Relationen mellan nationella prov och terminsbetyg årskurs 6',
        'unit': 'No'
    },
    {
        'concept': 'tot_andel_ae__200',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) i nationella provet för ämnet, totalt',
        'sid': 'tot_andel_ae',
        'table': '200',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Geografi, Historia, Religionskunskap, Samhällskunskap',
        'unit': 'Prc'
    },
    {
        'concept': 'tot_andel_ae__196',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) nationella provet för ämnet, totalt',
        'sid': 'tot_andel_ae',
        'table': '196',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Prc'
    },
    {
        'concept': 'tot_andel_ae__71',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 6 som uppnått kunskapskraven (A-E) i ämnet, pojkar',
        'sid': 'tot_andel_ae',
        'table': '71',
        'table_name': 'Betyg per ämne årskurs 6',
        'unit': 'Prc'
    },
    {
        'concept': 'tot_andel_ae__193',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) i nationella provets delprov, totalt',
        'sid': 'tot_andel_ae',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Prc'
    },
    {
        'concept': 'tot_andel_ae__199',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever i årskurs 9 som uppnått kunskapskraven (A-E) i nationella provet för ämnet, totalt',
        'sid': 'tot_andel_ae',
        'table': '199',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Biologi, Fysik och Kemi',
        'unit': 'Prc'
    },
    {
        'concept': 'tot_andel_fli__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel flickor årskurs 1-9',
        'sid': 'tot_andel_fli',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'Prc'
    },
    {
        'concept': 'tot_andel_foraldr_eftergy_utb__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever med föräldrar med eftergymnasial utbildning årskurs 1-9',
        'sid': 'tot_andel_foraldr_eftergy_utb',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'Prc'
    },
    {
        'concept': 'tot_andel_utl_bakgr__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Andel elever med utländsk bakgrund årskurs 1-9',
        'sid': 'tot_andel_utl_bakgr',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'Prc'
    },
    {
        'concept': 'tot_elever__6',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever årskurs 1-9',
        'sid': 'tot_elever',
        'table': '6',
        'table_name': 'Antal elever per årskurs',
        'unit': 'No'
    },
    {
        'concept': 'tot_elever__21',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Totalt antal elever per program och inriktning',
        'sid': 'tot_elever',
        'table': '21',
        'table_name': 'Antal elever som började 2011 eller senare, per program',
        'unit': 'No'
    },
    {
        'concept': 'tot_elever__70',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Totalt antal elever per program',
        'sid': 'tot_elever',
        'table': '70',
        'table_name': 'Antal elever som började 2011 eller senare, per program och inriktning',
        'unit': 'No'
    },
    {
        'concept': 'tot_elever__136',
        'concept_type': 'measure',
        'form': '21',
        'name': 'Totalt antal elever',
        'sid': 'tot_elever',
        'table': '136',
        'table_name': 'Antal elever',
        'unit': 'No'
    },
    {
        'concept': 'tot_gbp__71',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 6, totalt',
        'sid': 'tot_gbp',
        'table': '71',
        'table_name': 'Betyg per ämne årskurs 6',
        'unit': 'Scale'
    },
    {
        'concept': 'tot_gbp__196',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 9, totalt',
        'sid': 'tot_gbp',
        'table': '196',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'tot_gbp__200',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 9, totalt',
        'sid': 'tot_gbp',
        'table': '200',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Geografi, Historia, Religionskunskap, Samhällskunskap',
        'unit': 'Scale'
    },
    {
        'concept': 'tot_gbp__199',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provet för ämnet för elever i årskurs 9, totalt',
        'sid': 'tot_gbp',
        'table': '199',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Biologi, Fysik och Kemi',
        'unit': 'Scale'
    },
    {
        'concept': 'tot_gbp__193',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Genomsnittligt betygspoäng i nationella provets delprov för ämnet för elever i årskurs 9, totalt',
        'sid': 'tot_gbp',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'tot_m_betyg__71',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever med betyg i ämnet årskurs 6',
        'sid': 'tot_m_betyg',
        'table': '71',
        'table_name': 'Betyg per ämne årskurs 6',
        'unit': 'Scale'
    },
    {
        'concept': 'tot_m_betyg__196',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever som deltagit i nationella provet i ämnet årskurs 9',
        'sid': 'tot_m_betyg',
        'table': '196',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'tot_m_betyg__200',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever som deltagit i nationella provet i ämnet årskurs 9',
        'sid': 'tot_m_betyg',
        'table': '200',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Geografi, Historia, Religionskunskap, Samhällskunskap',
        'unit': 'Scale'
    },
    {
        'concept': 'tot_m_betyg__199',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever som deltagit i nationella provet i ämnet årskurs 9',
        'sid': 'tot_m_betyg',
        'table': '199',
        'table_name': 'Resultat nationella prov årskurs 9, provbetyg per kön - Biologi, Fysik och Kemi',
        'unit': 'Scale'
    },
    {
        'concept': 'tot_m_betyg__193',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Antal elever som deltagit i nationella provets delprov i ämnet årskurs 9',
        'sid': 'tot_m_betyg',
        'table': '193',
        'table_name': 'Resultat nationella prov årskurs 9, per delprov och kön - Engelska, Matematik och Svenska/svenska som andraspråk',
        'unit': 'Scale'
    },
    {
        'concept': 'ver_and_uppn_malen__95',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Faktiskt värde för andel (%) som uppnått kunskapskraven',
        'sid': 'ver_and_uppn_malen',
        'table': '95',
        'table_name': 'Salsa, skolenheters resultat av slutbetygen i årskurs 9 med hänsyn till elevsammansättningen',
        'unit': 'Prc'
    },
    {
        'concept': 'ver_meritvarde__95',
        'concept_type': 'measure',
        'form': '11',
        'name': 'Faktiskt genomsnittligt meritvärde',
        'sid': 'ver_meritvarde',
        'table': '95',
        'table_name': 'Salsa, skolenheters resultat av slutbetygen i årskurs 9 med hänsyn till elevsammansättningen',
        'unit': 'Scale'
    },
    {
        'concept': 'year',
        'concept_type': 'time',
        'form': None,
        'name': 'År',
        'sid': 'year',
        'table': None,
        'table_name': None,
        'unit': None
    }
]
