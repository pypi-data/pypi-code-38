import pandas as pd
import os
from bamboo_lib.models import PipelineStep, ComplexPipelineExecutor  # ,Connector
from bamboo_lib.steps import LoadStep, UnzipStep
from bamboo_lib.connectors.models import Connector
from bamboo_lib.logger import logger
from bamboo_lib.pipelines.pums.mondrian import gen_schema
from bamboo_lib.pipelines.pums.cleaning import cleaner
from bamboo_lib.pipelines.pums.cleaning.util import num_helper
from pandas.api.types import is_numeric_dtype
import numpy as np

MEASURES = ["WKW", "AGEP", "WAGP", "WKHP", "PERNP", "PINCP"]

global file_counter

file_counter = 0


class SaveStep(PipelineStep):
    def __init__(self, **kwargs):
        super(SaveStep, self).__init__(**kwargs)
        self.file_counter = 0

    def run_step(self, prev, params):
        logger.debug("Generating schema...")
        file_path = "$HOME/pums-data/pums_{}{}_{}_{}.csv".format(params.get("regional-mode", "us"), params.get("year"), params.get("estimate"), self.file_counter)
        file_path = os.path.expandvars(file_path)
        prev.to_csv(file_path, index=False)
        self.file_counter += 1
        return file_path


class MakeSchemaStep(PipelineStep):
    def __init__(self, table_name, **kwargs):
        super(MakeSchemaStep, self).__init__(**kwargs)
        self.table_name = table_name

    def run_step(self, prev, params):
        logger.debug("Generating schema...")
        return gen_schema(self.table_name, output_as_fo=True)


class TransferToServerStep(PipelineStep):
    def run_step(self, prev, params):
        logger.debug("Transfering schema...")
        estimate = params["estimate"]
        fpath = "datausa-acs-temp/mondrian/frags/pums_{}.xml".format(estimate)
        self.connector.send_file(prev, fpath, use_fo=True)
        logger.debug("Flushing Mondrian...")
        http_res = self.http_connector.hit()
        logger.debug("Response {} {}".format(http_res.status_code, http_res.json()))
        return True


class ExtractStep(PipelineStep):
    def run_step(self, prev, params):
        logger.debug("Running ExtractStep step...")
        downloaded_file = self.connector.download(params=params)
        return downloaded_file


class AddPkStep(PipelineStep):
    def __init__(self, table_name, **kwargs):
        super(AddPkStep, self).__init__(**kwargs)
        self.table_name = table_name

    def run_step(self, prev, params):
        pk_cols = self.pk_cols
        return self.connector.add_pk(self.schema, self.table_name, pk_cols)


class ChunkStep(PipelineStep):
    def run_step(self, prev, params):
        logger.debug("Running TransformStep step...")
        used_vars = [
            "PUMA", "PWGTP", "SEX", "ESR", "ADJINC",
            "POBP", "SCHL", "ST", "RAC1P", "FOD1P",
            "SERIALNO", "SPORDER", "NAICSP", "SOCP",
            "CIT", "NATIVITY", "HISP", "VPS"
        ]

        weights = ["pwgtp{}".format(i) for i in range(1, 81)]

        if params["estimate"] == 5 or params["year"] == 2017:
            weights = [w.upper() for w in weights]

        cols = used_vars + weights + MEASURES

        def valid_col(x):
            if x in ["PUMA00", "PUMA10", "SOCP00", "SOCP10", "SOCP12", "SERIALNO", "serialno", "POBP05", "POBP12", "pobp05", "pobp12"]:
                return True
            return (x in cols) or (x in [c.lower() for c in cols])
        return pd.read_csv(prev, chunksize=50000000, usecols=valid_col, converters={
            "SERIALNO": str,
            "ESR": str,
            "SEX": str,
            "CIT": str,
            "HISP": str,
            "VPS": str,
            "PUMA": str,
            "PUMA00": str,
            "PUMA10": str,
            "SCHL": str,
            "NATIVITY": str,
            "ST": str,
            "FOD1P": str,
            "NAICSP": str,
            "SOCP": str,
            "SOCP00": str,
            "SOCP10": str,
            "MSP": str,
            "SPORDER": str})
            # na_values=['', ' '])


class TransformStep(PipelineStep):
    def __init__(self, connector, **kwargs):
        super(TransformStep, self).__init__(**kwargs)
        self.connector = connector

    def run_step(self, prev, params):
        df = prev
        estimate = params['estimate']

        if "year" in params:
            df["year"] = params["year"]
        inflation_cols = ["INTP", "OIP", "PAP", "PERNP", "PINCP", "RETP", "SEMP", "SSIP", "SSP", "WAGP"]
        df.ADJINC = df.ADJINC / 1000000.0
        for col in inflation_cols:
            if col in df.columns:
                if not is_numeric_dtype(df[col]):
                    df = num_helper(df, estimate, col)
                df[col] = df[col] * df.ADJINC
        del df['ADJINC']

        df.columns = [col.lower() for col in df.columns]
        # for i in range(1, 81):
            # del df["pwgtp{}".format(i)]
        df.replace('', np.nan, inplace=True)
        if params['estimate'] == 5:
            df = cleaner.standardize(df, **params)
        else:
            df['puma'] = "79500US" + df['st'].astype(str).str.zfill(2) + df['puma'].astype(str).str.zfill(5)
            df['st'] = "04000US" + df['st'].astype(str).str.zfill(2)

        cutoffs = [0, 10000, 20000, 30000, 40000, 50000,
                   60000, 70000, 80000, 90000, 100000, 110000, 120000,
                   130000, 140000, 150000, 160000, 170000, 180000, 190000,
                   200000, 1000000000]
        # TODO testing
        df['wage_bin'] = pd.cut(df.wagp, cutoffs, labels=[
            '< $10K',
            '$10-20k',
            '$20-30k',
            '$30-40k',
            '$40-50k',
            '$50-60k',
            '$60-70k',
            '$70-80k',
            '$80-90k',
            '$90-100k',
            '$100-110k',
            '$110-120k',
            '$120-130k',
            '$130-140k',
            '$140-150k',
            '$150-160k',
            '$160-170k',
            '$170-180k',
            '$180-190k',
            '$190-200k',
            '$200k+'], include_lowest=True)
        err_df_chk = df[(df.wagp >= 200000) & (df.wage_bin.isnull())]
        # TODO some values >200000 showed up as NA. todo, test values >= 200k
        assert err_df_chk.empty, "Bad wage bins!"
        df.wage_bin = df.wage_bin.astype(str)
        df['in_workforce'] = (df.agep.astype(int) >= 16) & (df.wagp > 0) & df.esr.astype(str).isin(["1", "2", "4", "5"])
        # TODO review and test
        df.wkhp = df.wkhp.astype(str).str.strip()
        df.loc[df.wkhp == '', 'wkhp'] = None
        df.wkhp = df.wkhp.astype(float)
        df.loc[df.in_workforce & (df.wkhp >= 35), 'time_status'] = 1
        df.loc[df.in_workforce & (df.wkhp < 35), 'time_status'] = 2
        df['fiveplus'] = df.agep >= 5 ## TODO double check for 2018
        df['birthplace_in_us'] = df.pobp.astype(int) <= 72 ## TODO: Test this!

        df.wage_bin = df.wage_bin.astype(str)
        df.loc[df.wagp.isnull(), 'wage_bin'] = 'N/A'
        wage_bin_map = {
            'N/A': None,
            '< $10K': 1,
            '$10-20k': 2,
            '$20-30k': 3,
            '$30-40k': 4,
            '$40-50k': 5,
            '$50-60k': 6,
            '$60-70k': 7,
            '$70-80k': 8,
            '$80-90k': 9,
            '$90-100k': 10,
            '$100-110k': 11,
            '$110-120k': 12,
            '$120-130k': 13,
            '$130-140k': 14,
            '$140-150k': 15,
            '$150-160k': 16,
            '$160-170k': 17,
            '$170-180k': 18,
            '$180-190k': 19,
            '$190-200k': 20,
            '$200k+': 21
        }
        # raise Exception(df.wage_bin.dtype)
        df['wage_bin_id'] = df.wage_bin.map(wage_bin_map)
        if 'socp00' in df.columns:
            del df['socp00']
        regional_mode = params.get("regional-mode", "us")
        df['nation_id'] = '01000US' if regional_mode == 'us' else  '01000PR'
        # SERIALNO overflows integer as of 2017. Need to fix, but for now since it is not used. will set to 0
        df['serialno'] = 0
        return df


def run(params, **kwargs):
    print(params, "PARAMS!!!!!!!")
    BAMBOO_LIB_DIR = os.environ.get("BAMBOO_LIB_DIR")
    conn_path = os.path.join(BAMBOO_LIB_DIR, "example", "conns.yaml")
    # TODO allow client to pick connectors from UI
    # fallback_source = open(conn_path)
    # connector = Connector.fetch("voyaguers-remote", params.get("output-db", fallback_source))
    # connector = Connector.fetch("postgres-local", open(conn_path))
    regional_mode = params.get("regional-mode", "us")
    if regional_mode == "pr":
        connector2 = Connector.fetch("pums-pr", open(conn_path))
    else:
        connector2 = Connector.fetch("pums-local", open(conn_path))
    # du_http_connector = Connector.fetch("datausa-cube-remote", open(conn_path))
    # dt = {"serialno": "text",
    #       "year": "smallint",
    #       "esr": "smallint",
    #       "cit": "smallint",
    #       "hisp": "smallint",
    #       "nativity": "smallint",
    #       "sex": "smallint",
    #       "puma": "VARCHAR(14)",
    #       "agep": "smallint",
    #       "socp": "VARCHAR(6)",
    #       "naicsp": "VARCHAR(8)",
    #       "pobp": "smallint",
    #       "rac1p": "smallint",
    #       "vps": "smallint",
    #       "msp": "smallint",
    #       "schl": "smallint",
    #       "sporder": "smallint",
    #       "fod1p": "VARCHAR(8)",
    #       "socp": "VARCHAR(6)",
    #       "st": "VARCHAR(9)",
    #       "wage_bin_id": "smallint"}
    dt = {
        "serialno": "text",
        "sporder": "integer",
        "st": "varchar(9)",
        "pwgtp": "integer",
        "agep": "smallint",
        "cit": "smallint",
        "schl": "smallint",
        "sex": "integer",
        "wagp": "real",
        "wkhp": "smallint",
        "wkw": "smallint",
        "esr": "smallint",
        "fod1p": "smallint",
        "hisp": "smallint",
        "naicsp": "varchar(8)",
        "nativity": "smallint",
        "pernp": "real",
        "pincp": "real",
        "rac1p": "smallint",
        "socp10": "varchar(6)",
        "socp": "varchar(6)",
        "vps": "smallint",
        "year": "smallint",
        "puma": "varchar(14)",
        "pobp": "smallint",
        "wage_bin": "varchar(14)",
        "in_workforce": "boolean",
        "time_status": "smallint",
        "fiveplus": "boolean",
        "wage_bin_id": "smallint",
        "nation_id": "varchar(7)",
        "birthplace_in_us": "boolean"
    }

    weights = ["pwgtp{}".format(i) for i in range(1, 81)]
    estimate = params['estimate']
    for w in weights:
        dt[w] = "smallint"
    step1 = ExtractStep(connector=connector2)
    step2 = UnzipStep(pattern=r"\.csv$")
    table_name = "pums_{}_v2".format(estimate)
    chunkstep = ChunkStep()
    step3 = TransformStep(None)
    step4 = SaveStep()
    # step4 = LoadStep(table_name, connector, if_exists="append",
                     # index=False, dtype=dt, schema="pums")
    logger.info("* PUMS pipeline starting...")
    # add_pk_step = AddPkStep(table_name, schema="pums", connector=connector, pk_cols=["sporder", "serialno"])
    pp = ComplexPipelineExecutor(params)
    only_gen_schema = params.get('only-gen-schema', False)
    # schema_step1 = MakeSchemaStep(table_name)
    # schema_connector = Connector.fetch("schema-remote", open(conn_path))
    # schema_step2 = TransferToServerStep(connector=schema_connector, http_connector=du_http_connector)
    if not only_gen_schema:
        pp = pp.next(step1).foreach(step2).foreach(chunkstep).next(step3).next(step4).endeach().endeach()
    # pp = pp.next(schema_step1)
    # pp = pp.next(schema_step2)
    # if not only_gen_schema:
    # #### pp = pp.next(add_pk_step)
    pp.run_pipeline()


if __name__ == '__main__':
    run({"year": 2017, "estimate": 5, "only-gen-schema": False, "regional-mode": "us"})
