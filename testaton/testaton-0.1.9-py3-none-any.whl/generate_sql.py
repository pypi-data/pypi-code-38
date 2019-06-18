import re
import datetime


def decode_date(field):
    now = datetime.datetime.now()
    if field.find(":STR") > -1:
        format_string = "%Y%m%d"
        field = field.replace(":STR", "")
    else:  # :DT
        format_string = "%Y-%m-%d"

    if field == "TODAY":
        return now.strftime(format_string)
    if field[0:6] == "TODAY-":
        return (now - datetime.timedelta(days=int(field[6:]))).strftime(format_string)
    return ""


def decode_filter_statement(filter_key):
    """This method expands the filter statement if the statement has wildcards that need to be converted"""
    regex = re.compile("{(.*?)}")
    r = regex.search(filter_key)
    while r:
        field = r.groups()[0]
        if field.upper().find("TODAY") > -1:
            result = decode_date(field.upper())
            # note this section should not have a ' ' because the ' should be defined in the SQL statement
            filter_key = filter_key.replace(
                "{" + field + "}", result)
        r = regex.search(filter_key)
    return filter_key


def generate_uniqueness_sql(dataset, test_def):
    """Tests for uniqueness of a field, using a count and group by"""
    q = "select " + test_def['field'] + \
        ", count(1) as dupes " + "from " + \
        dataset[test_def['dataset']].table_name
    if 'filter' in test_def:
        q += " where " + decode_filter_statement(test_def['filter'])
    q += " group by " + test_def['field']
    q += " having count(1) > 1 "
    q += " order by dupes desc "
    q += " limit 10"
    return q


def generate_filter_sql(dataset, test_def):
    """Simple filter test"""
    q = "select count(1) as result_count from " + \
        dataset[test_def['dataset']].table_name
    q += " where " + decode_filter_statement(test_def['filter'])
    return q


def generate_fk_sql(dataset, test_def):
    """Tests for a foreign key constraint relationship"""
    filter_stmt = ""
    if 'filter' in test_def:
        filter_stmt += " where " + \
            decode_filter_statement(test_def['filter']) + " "

    q = """
     select count(1) as result_count from (
        select {parent_field} from {parent_table} {filter_statement}
        except
        select {child_field} from {child_table} {filter_statement}
    ) a""".format(child_field=test_def['child_field'], child_table=dataset[test_def['child_dataset']].table_name, filter_statement=filter_stmt,
                  parent_field=test_def['parent_field'], parent_table=dataset[test_def['parent_dataset']].table_name)
    return q


def generate_date_load_check_sql(dataset, test_def):
    # converted this to inner clause because of mysql
    q = """
    select d.date_id, data.records
    from {date_table} d left outer join 
            (select {date_field} as date_id, count(1) records 
            from {table} 
            where {date_field} >= '{start_date}' and {date_field} <= '{end_date}'  
            group by {date_field} ) data 
            on d.date_id = data.date_id
    where d.date_id >= '{start_date}' and d.date_id <= '{end_date}'
          and data.records is null
    order by d.date_id desc
    limit 10""".format(date_field=test_def['date_field'], table=dataset[test_def['dataset']].table_name,
                       start_date=decode_filter_statement(test_def['start_date']), end_date=decode_filter_statement(test_def['end_date']),
                       date_table=dataset[test_def['date_table']].table_name)
    return q


def generate_fk_sql_joins(dataset, test_def):
    """This uses joins to conduct the foreign key constraint check and return statistics on number of mathes"""
    filter_stmt = ""
    if 'filter' in test_def:
        filter_stmt += " where " + \
            decode_filter_statement(test_def['filter']) + " "

    q = """
        select sum(case when c_{child_field} is not null then 1 else 0 end) / sum(inc) as pc_populated, 
            sum(case when c_{child_field} is null then 1 else 0 end) as result_count
        from (
            select distinct p.{parent_field} as p_{parent_field}, c.{child_field} as c_{child_field}, 1 as inc
            from {parent_table} p left outer join {child_table} c on p.{parent_field} = c.{child_field} {filter_statement}
    ) a""".format(child_field=test_def['child_field'], child_table=dataset[test_def['child_dataset']].table_name,
                  parent_field=test_def['parent_field'], parent_table=dataset[test_def['parent_dataset']].table_name, filter_statement=filter_stmt)
    return q


def generate_field_sql(dataset, test_def):
    """Pulls out the two required fields to be compared for accuracy"""
    q = "select {field1}, {field2} from {table}".format(field1=test_def['fields'][0],
                                                        field2=test_def['fields'][1], table=dataset[test_def['dataset']].table_name)
    return q


# TODO Setup the tests again
##################################
############ TESTS ###############
##################################
"""
def test_foreign_key_sql():
    fk_test = {
        "test_name" : "customer vs transaction test",
        "test_type" : "foreign_key",
        "parent_table" : "customer", 
        "parent_field" : "customer_id", 
        "child_table" : "transaction", 
        "child_field" : "customer_id"
    }    
    q = generate_fk_sql(fk_test)
    assert(q == '\n     select count(1) from (\n        select customer_id from transaction\n        minus\n        select customer_id from customer\n    )')

def test_unique_sql():
    unique_test = {
        "test_name" : "product_id unique check",
        "test_type" : "unique",
        "table" : "cine", 
        "field" : "id_cine"
        }
    q = generate_uniqueness_sql(unique_test)
    assert(q == 'select id_cine, count(1) from cine group by id_cine having count(1) > 1  order by count(1) desc  limit 10')


def test_decode_date():
    today = datetime.datetime.now()
    yesterday = today + datetime.timedelta(days=-1)
    ten_days_ago = today + datetime.timedelta(days=-10)

    assert decode_date("TODAY") == today.strftime("%Y-%m-%d")

    assert decode_date("YESTERDAY") == yesterday.strftime("%Y-%m-%d")

    assert decode_date("TODAY-10") == ten_days_ago.strftime("%Y-%m-%d")

    assert decode_date("BLA") == ""


def test_decode_filter_statement():
    today = datetime.datetime.now()
    yesterday = today + datetime.timedelta(days=-1)
    ten_days_ago = today + datetime.timedelta(days=-10)

    assert decode_filter_statement("something = nothing") == "something = nothing"

    assert decode_filter_statement("d.date = {today}") == "d.date = '" + today.strftime("%Y-%m-%d") + "'"

    assert decode_filter_statement("d.date >= {today-10} and d.date <= {today-1}") == "d.date >= '" + ten_days_ago.strftime("%Y-%m-%d") + "' and d.date <= '" + yesterday.strftime("%Y-%m-%d") + "'"

test_foreign_key_sql()
test_unique_sql()
test_decode_filter_statement()
test_decode_date()

"""
