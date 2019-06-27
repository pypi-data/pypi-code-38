import os
import pandas as pd
from datasetmaker.path import DDF_DIR


concepts = pd.read_csv(os.path.join(DDF_DIR, 'ddf--concepts.csv'))


def _read_entity_csv(entity, lang=None):
    fname = f"ddf--entities--{entity}.csv"
    if lang:
        path = os.path.join(DDF_DIR, f"lang/{lang}", fname)
    else:
        path = os.path.join(DDF_DIR, fname)
    df = pd.read_csv(path)
    return df


def _merge_translation(src_df, lang_df, col):
    src_df = src_df.merge(lang_df, on=["indicator", "source"], how="left")
    src_df[f"{col}_x"] = src_df[f"{col}_y"].fillna(src_df[f"{col}_x"])
    src_df = src_df.drop(f"{col}_y", axis=1)
    src_df = src_df.rename(columns={f"{col}_x": col})
    return src_df


def read_concepts(lang=None):
    fname = "ddf--concepts.csv"
    if lang:
        path = os.path.join(DDF_DIR, f"lang/{lang}", fname)
    else:
        path = os.path.join(DDF_DIR, fname)
    df = pd.read_csv(path)
    return df


def id_to_name(source, lang=None):
    df = _read_entity_csv("indicator")
    if lang:
        lang_df = _read_entity_csv("indicator", lang)
        df = _merge_translation(df, lang_df, "name")
    df = df.query(f'source == "{source}"')
    return df.set_index("indicator").name.to_dict()


def sid_to_id(source):
    df = _read_entity_csv("indicator")
    return df.set_index("sid").indicator.to_dict()
