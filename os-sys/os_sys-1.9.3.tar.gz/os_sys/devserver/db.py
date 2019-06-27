def make_db_file():
    with open('site_db.os_sys_db', 'w+') as fh:
        fh.write('{}')
def add_data(db_name, **data_dict_kwargs):
    with open('site_db.os_sys_db') as file:
        file_ = file.read()
        data = eval(file_)
    data_dict_kwargs = data_dict_kwargs
    for i in list(data[db_name]):
        data_dict_kwargs[i] = data[db_name][i]
    data[db_name] = data_dict_kwargs
    with open('site_db.os_sys_db', 'w+') as wf:
        wf.write(str(data))
def make_db(db_name):
    with open('site_db.os_sys_db') as file:
        data = eval(file.read())
    data[db_name] = {}
    with open('site_db.os_sys_db', 'w+') as wf:
        wf.write(str(data))
def get_dbs():
    return eval(open('site_db.os_sys_db').read())
def get_db(db_name):
    return eval(open('site_db.os_sys_db').read())[db_name]
def add_table(db_name, table_name, **data_dict_kwargs):
    db_name = db_name + '-'.join(table_name)
    with open('site_db.os_sys_db') as file:
        file_ = file.read()
        data = eval(file_)
    data_dict_kwargs = data_dict_kwargs
    for i in list(data[db_name]):
        data_dict_kwargs[i] = data[db_name][i]
    data[db_name] = data_dict_kwargs
    with open('site_db.os_sys_db', 'w+') as wf:
        wf.write(str(data))
def get_tables():
    data = get_dbs()
    out = []
    for item in list(data):
        if '-' in item:
            out.append(data[item])
def get_table(db_name, table):
    return get_db(db_name + '-'.join(table))
def make_table(db_name, table):
    make_db(db_name + '-'.join(table))

