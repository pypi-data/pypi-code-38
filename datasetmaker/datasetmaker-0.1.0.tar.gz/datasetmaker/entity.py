import os
import pandas as pd
from datasetmaker.path import DDF_DIR


class Country():
    @classmethod
    def _read_entity_csv(cls, entity, lang=None):
        fname = f"ddf--entities--{entity}.csv"
        if lang:
            path = os.path.join(DDF_DIR, f"lang/{lang}", fname)
        else:
            path = os.path.join(DDF_DIR, fname)
        df = pd.read_csv(path)
        return df

    @classmethod
    def _merge_translation(cls, src_df, lang_df, col):
        src_df = src_df.merge(lang_df, on="country", how="left")
        src_df[f"{col}_x"] = src_df[f"{col}_y"].fillna(src_df[f"{col}_x"])
        src_df = src_df.drop(f"{col}_y", axis=1)
        src_df = src_df.rename(columns={f"{col}_x": col})
        return src_df

    @classmethod
    def name_to_id(cls, lang=None):
        df = cls._read_entity_csv("country")
        if lang:
            lang_df = cls._read_entity_csv("country", lang)
            df = cls._merge_translation(df, lang_df, "name")
        map_ = df.set_index("name").country.to_dict()
        alt_names = df.set_index('alt_name').country.to_dict().items()
        for alts, id_ in alt_names:
            if pd.isnull(alts):
                continue
            map_.update({k: id_ for k in alts.split(';')})
        return map_


    @classmethod
    def id_to_name(cls, lang=None):
        df = cls._read_entity_csv("country")
        if lang:
            lang_df = cls._read_entity_csv("country", lang)
            df = cls._merge_translation(df, lang_df, "name")
        return df.set_index("country").name.to_dict()

    @classmethod
    def iso3_to_id(cls):
        df = cls._read_entity_csv("country")
        df = df.dropna(subset=['iso3'])
        return df.set_index("iso3").country.to_dict()
