from bamboo_lib.pipelines.pums.cleaning.util import num_helper, preclean_io_codes
from bamboo_lib.pipelines.pums.cleaning.puma import puma_cleaning
from bamboo_lib.pipelines.pums.cleaning.io_converter import occ_convert


def clean_pobp(df):
    print("Cleaning birthplaces....")
    if 'pobp05' in df.columns:
        pobp05i = df['pobp05'].astype(int)
        pobp12i = df['pobp12'].astype(int)

        df.loc[pobp05i >= 0, 'pobp'] = df.loc[pobp05i >= 0, 'pobp05']
        df.loc[pobp12i >= 0, 'pobp'] = df.loc[pobp12i >= 0, 'pobp12']
        del df['pobp05']
        del df['pobp12']
    print("Completed cleaning birthplaces!")
    return df


def standardize(df, **kwargs):
    estimate = kwargs.get('estimate')
    year = kwargs.get('year')

    df = num_helper(df, estimate, 'wagp')
    df = num_helper(df, estimate, 'wkhp')

    assert df[df.st.isnull()].empty

    df = preclean_io_codes(df)

    df = puma_cleaning(df, year, estimate)
    df["st"] = "04000US" + df.st
    df = occ_convert(df, kwargs)
    df = clean_pobp(df)
    return df


if __name__ == '__main__':
    print("HELLO!!!")
