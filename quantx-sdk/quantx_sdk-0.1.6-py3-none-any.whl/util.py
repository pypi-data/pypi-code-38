import pandas as pd


class Util:
    @staticmethod
    def convert_df(df, date_columns, number_columns):
        for c in date_columns:
            df[c] = pd.to_datetime(df[c], errors="ignore")
        for c in number_columns:
            df[c] = pd.to_numeric(df[c], errors="ignore")
        return df
