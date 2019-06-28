secrets = {
    "output_dir": "./__output_dir/",
    "data_dir": "./__data_dir/",
    "script_dir": "./__script_dir/",
    "sqlite": {"distro": "sqlite", "database": ":memory:"},
    "mysql": {
        "distro": "mysql",
        "server": "localhost",
        "database": "test_mason",
        "schema": "test_mason",
        "username": "test_mason",
        "password": "test_mason",
    },
    "postgresql": {
        "distro": "postgresql",
        "server": "localhost",
        "database": "test_mason",
        "schema": "test_mason",
        "username": "test_mason",
        "password": "test_mason",
    },
}
secrets["sql"] = secrets["postgresql"]

# -- create schema test_mason;
# create table test_mason.test_mason
# (id int)
# ;

# select * from test_mason.test_mason;
# drop table test_mason.test_mason;
