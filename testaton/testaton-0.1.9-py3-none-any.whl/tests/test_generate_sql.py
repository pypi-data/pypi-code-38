from generate_sql import generate_uniqueness_sql, generate_fk_sql, generate_filter_sql, generate_field_sql, generate_fk_sql_joins, \
    generate_date_load_check_sql, decode_date, decode_filter_statement

# VIP NOTE:
# In order to execute this test run it from the command line you NEED to execute it from the parent directory with the command
# so that python resolves the right directory structure. Otherwise the module not found errors will haunt you throughout your life
# READ this documentation: https://docs.pytest.org/en/latest/usage.html#cmdline
# python3 -m pytest tests/

import datetime


def test_decode_date():
    today = datetime.datetime.now()
    ten_days_ago = today + datetime.timedelta(days=-10)

    assert decode_date("TODAY") == today.strftime("%Y-%m-%d")

    assert decode_date("TODAY-10") == ten_days_ago.strftime("%Y-%m-%d")

    assert decode_date("BLA") == ""


def test_decode_filter_statement():
    today = datetime.datetime.now()
    yesterday = today + datetime.timedelta(days=-1)
    ten_days_ago = today + datetime.timedelta(days=-10)

    assert decode_filter_statement(
        "something = nothing") == "something = nothing"

    assert decode_filter_statement(
        "d.date = {today}") == "d.date = '" + today.strftime("%Y-%m-%d") + "'"

    # test the string format
    assert decode_filter_statement(
        "d.date = {today:str}") == "d.date = '" + today.strftime("%Y%m%d") + "'"

    assert decode_filter_statement(
        "d.date = {today-1:str}") == "d.date = '" + yesterday.strftime("%Y%m%d") + "'"

    assert decode_filter_statement("d.date >= {today-10} and d.date <= {today-1}") == "d.date >= '" + \
        ten_days_ago.strftime("%Y-%m-%d") + "' and d.date <= '" + \
        yesterday.strftime("%Y-%m-%d") + "'"


# def test_foreign_key_sql():
#     fk_test = {
#         "test_name": "customer vs transaction test",
#         "test_type": "foreign_key",
#         "parent_table": "customer",
#         "parent_field": "customer_id",
#         "child_table": "transaction",
#         "child_field": "customer_id"
#     }
#     q = generate_fk_sql("", fk_test)
#     assert(q == '\n     select count(1) from (\n        select customer_id from transaction\n        minus\n        select customer_id from customer\n    )')


# def test_unique_sql():
#     unique_test = {
#         "test_name": "product_id unique check",
#         "test_type": "unique",
#         "table": "cine",
#         "field": "id_cine"
#     }
#     q = generate_uniqueness_sql("", unique_test)
#     assert(q == 'select id_cine, count(1) from cine group by id_cine having count(1) > 1  order by count(1) desc  limit 10')
