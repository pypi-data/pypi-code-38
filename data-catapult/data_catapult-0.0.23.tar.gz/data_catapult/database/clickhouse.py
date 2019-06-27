import clickhouse_driver
from clickhouse_driver.errors import ErrorCodes
import numpy as np
import math

class ClickhouseDriver(object):
    def __init__(self, **kwargs):
        self.host = kwargs.get("host", "localhost")
        self.port = int(kwargs.get("port", 9000))
        self.database = kwargs.get("database", "default")
        self.user = kwargs.get("user", "default")
        self.password = kwargs.get("password", "")
        self.engine = kwargs.get("engine", "MergeTree")
        self.engine_params = kwargs.get("engine_params", "")

    def clean_col_name(self, c):
        return c.lower().replace("nullable(", "").replace(")", "") if c else c

    def get_data(self, df, dtypes, has_header=True, nullable_list=None, user_dtype=None):
        int_col_types = ["int", "integer", "bigint", "uint8", "uint16", "uint32", "uint64", "int8", "int16", "int32", "int64"]
        user_dtype_vals_lower = [self.clean_col_name(v) for v in user_dtype.values()] if user_dtype else []
        dtypes_has_int = user_dtype and set(int_col_types).intersection(set(user_dtype_vals_lower))
        if not nullable_list and not dtypes_has_int:
            return df.values.tolist()
        else:
            indices = list(map(lambda x: list(df.columns).index(x), nullable_list)) if nullable_list else []
            int_col_names = [col_name for col_name, kind in user_dtype.items() if self.clean_col_name(kind) in int_col_types] if user_dtype else []
            int_indices = list(map(lambda x: list(df.columns).index(x), int_col_names))
            my_data = []
            for row in df.values:
                my_new_row = []
                for idx, item in enumerate(row):
                    if idx in int_indices:
                        if item and not math.isnan(item):
                            my_new_row.append(int(item))
                        else:
                            my_new_row.append(None)
                    elif (idx in indices) and (isinstance(item, float) or isinstance(item, int)) and math.isnan(item):
                        my_new_row.append(None)
                    else:
                        my_new_row.append(item)
                my_data.append(my_new_row)
            return my_data

    def derive_kind(self, d, nullable=True, if_exists="fail", user_dtypes=None, col_name=None):
        if col_name and user_dtypes and col_name in user_dtypes:
            target_type = user_dtypes[col_name]
            if nullable and not target_type.lower().startswith("nullable"):
                return "Nullable({})".format(target_type)
            return target_type
        d = str(d)
        if d in ['real', 'float', 'float64', 'real64']:
            return "Nullable(Float32)" if nullable else "Float32"
        elif d in ['int', 'int64']:
            return "Nullable(Int64)" if nullable else "Int64"
        return "Nullable(String)" if nullable else "String"

    def to_sql(self, source_df, name, if_exists="fail", nullable_list=None, pk=None, dtype=None, engine=None, engine_params=None):
        # print source, type(source)
        # header_df = pd.read_csv(source, nrows=50000)
        columns = source_df.columns
        my_engine = engine or self.engine
        my_engine_params = engine_params or self.engine_params
        kinds = zip(columns, [self.derive_kind(d, nullable=columns[idx] in nullable_list if nullable_list else False, user_dtypes=dtype, col_name=columns[idx]) for idx, d in enumerate(source_df.dtypes)])
        kinds = ['"{}" {}'.format(c, k) for c, k in kinds]
        table_name = name
        if not pk:
            raise ValueError("At this time, you Must specify primary key for Engine! Pass a list of column names as arguments, e.g. pk=['col1', 'col2']")
        if not isinstance(pk, list):
            raise ValueError("Primary key (pk parameter) must be provide as a list")
        engine = "{}({}) ORDER BY ({})".format(my_engine, my_engine_params, ",".join(pk))
        create_table_sql = '''CREATE TABLE {} ({}) ENGINE = {}'''.format(table_name, ",".join(kinds), engine)
        client = clickhouse_driver.Client(host=self.host, port=self.port,
                                          database=self.database, user=self.user,
                                          password=self.password)
        try:
            client.execute(create_table_sql)
        except clickhouse_driver.errors.ServerException as err:
            if if_exists == "fail":
                print("Error when trying to create table. table already exists?")
                raise ValueError("Mode is set to fail and table already exists")
            elif if_exists == "append":
                if err.code == ErrorCodes.TABLE_ALREADY_EXISTS:
                    pass # Allow the program to continue
                else:
                    raise RuntimeError("Could not import table!", str(err))
        # -- using list for now, but eventually use generator to stream inserts
            elif if_exists == "drop":
                 print("** ALERT! Droppping table ", table_name)
                 drop_table_sql = 'DROP TABLE {};'.format(table_name)
                 client.execute(drop_table_sql)
                 client.execute(create_table_sql)
            else:
                raise ValueError(if_exists, "bad value for if_exists")
        data = self.get_data(source_df, source_df.dtypes.values, nullable_list=nullable_list, user_dtype=dtype)
        # source_df.seek(0)
        col_list = ",".join(source_df.columns)
        my_sql_str = "INSERT INTO {} ({}) FORMAT CSV".format(table_name, col_list)
        try:
            client.execute(my_sql_str, data, types_check=False)
        except clickhouse_driver.errors.TypeMismatchError as err:
            print("ERROR *** TypeMismatchError in Clickhouse driver. Are you trying to insert null values into a non-nullable column?\n")
            raise err

        if my_engine == "ReplacingMergeTree":
            client.execute("OPTIMIZE TABLE {};".format(table_name))

        client.disconnect()
        # return source
