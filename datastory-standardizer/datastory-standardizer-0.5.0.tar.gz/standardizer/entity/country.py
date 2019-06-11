import os
import pandas as pd
from standardizer.path import DDF_DIR


def _read_entity_csv(entity, lang=None):
    fname = f"ddf--entities--{entity}.csv"
    if lang:
        path = os.path.join(DDF_DIR, f"lang/{lang}", fname)
    else:
        path = os.path.join(DDF_DIR, fname)
    df = pd.read_csv(path)
    return df


def _merge_translation(src_df, lang_df, col):
    src_df = src_df.merge(lang_df, on="country", how="left")
    src_df[f"{col}_x"] = src_df[f"{col}_y"].fillna(src_df[f"{col}_x"])
    src_df = src_df.drop(f"{col}_y", axis=1)
    src_df = src_df.rename(columns={f"{col}_x": col})
    return src_df


def name_to_id(lang=None):
    df = _read_entity_csv("country")
    df_alt = _read_entity_csv("country_alt_name")
    df_alt = df_alt.rename(columns={"country_alt_name": "name"})
    df = pd.concat([df, df_alt], sort=True)
    if lang:
        lang_df = _read_entity_csv("country", lang)
        df = _merge_translation(df, lang_df, "name")
    return df.set_index("name").country.to_dict()


def id_to_name(lang=None):
    df = _read_entity_csv("country")
    if lang:
        lang_df = _read_entity_csv("country", lang)
        df = _merge_translation(df, lang_df, "name")
    return df.set_index("country").name.to_dict()


def iso3_to_id():
    df = _read_entity_csv("country")
    df = df.dropna(subset=['iso3'])
    return df.set_index("iso3").country.to_dict()
