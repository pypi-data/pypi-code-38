import clickhouse_driver


class ClickhouseDriver(object):
    def __init__(self, **kwargs):
        self.host = kwargs.get("host", "localhost")
        self.port = int(kwargs.get("port", 9000))
        self.database = kwargs.get("database", "default")
        self.user = kwargs.get("user", "default")
        self.password = kwargs.get("password", "")

    def get_data(self, df, dtypes, has_header=True):
        return list(df.values)

    def derive_kind(self, d, nullable=True, if_exists="fail"):
        d = str(d)
        if d in ['real', 'float', 'float64', 'real64']:
            return "Nullable(Float32)" if nullable else "Float32"
        elif d in ['int', 'int64']:
            return "Nullable(Int64)" if nullable else "Int64"
        return "Nullable(String)" if nullable else "String"

    def ingest(self, source, name, if_exists="fail"):
        # print source, type(source)
        # header_df = pd.read_csv(source, nrows=50000)
        columns = source.columns
        kinds = zip(columns, [self.derive_kind(d) for d in source.dtypes])
        kinds = ["{} {}".format(c, k) for c, k in kinds]
        table_name = name
        engine = "Log"  # -- TODO use better default engine
        create_table_sql = '''CREATE TABLE {} ({}) ENGINE = {}'''.format(table_name, ",".join(kinds), engine)
        client = clickhouse_driver.Client(host=self.host, port=self.port,
                                          database=self.database, user=self.user,
                                          password=self.password)
        try:
            client.execute(create_table_sql)
        except clickhouse_driver.errors.ServerException:
            if if_exists == "fail":
                print("Error when trying to create table. table already exists?")  # -- TODO allow append/fail modes
        # -- using list for now, but eventually use generator to stream inserts
        data = self.get_data(source, source.dtypes.values)
        # source.seek(0)
        my_sql_str = "INSERT INTO {} FORMAT CSV".format(table_name)
        client.execute(my_sql_str, data)
        client.disconnect()
        # return source
