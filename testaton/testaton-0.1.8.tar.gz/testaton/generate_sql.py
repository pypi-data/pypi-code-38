def generate_uniqueness_sql(dataset, test_def):
    """Tests for uniqueness of a field, using a count and group by"""
    q = "select " + test_def['field'] + ", count(1) as dupes " + "from " + dataset[test_def['dataset']].table_name
    if 'filter' in test_def:
        q += " where " + test_def['filter'] 
    q += " group by " + test_def['field']
    q += " having count(1) > 1 "
    q += " order by dupes desc "
    q += " limit 10"
    return q

def generate_filter_sql(dataset, test_def):
    """Simple filter test"""
    q = "select count(1) as result_count from " + dataset[test_def['dataset']].table_name
    q += " where " + test_def['filter'] 
    return q

def generate_fk_sql(dataset, test_def):
    """Tests for a foreign key constraint relationship"""
    q = """
     select count(1) as result_count from (
        select {parent_field} from {parent_table}
        except
        select {child_field} from {child_table}
    ) a""".format(child_field=test_def['child_field'], child_table=dataset[test_def['child_dataset']].table_name, 
                parent_field=test_def['parent_field'], parent_table=dataset[test_def['parent_dataset']].table_name)
    return q

def generate_fk_sql_joins(dataset, test_def):
    """This uses joins to conduct the foreign key constraint check and return statistics on number of mathes"""
    q = """
        select sum(case when c_{child_field} is not null then 1 else 0 end) / sum(inc) as pc_populated, 
            sum(case when c_{child_field} is null then 1 else 0 end) as result_count
        from (
            select p.{parent_field} as p_{parent_field}, c.{child_field} as c_{child_field}, 1 as inc
            from {parent_table} p left outer join {child_table} c on p.{parent_field} = c.{child_field}
    ) a""".format(child_field=test_def['child_field'], child_table=dataset[test_def['child_dataset']].table_name, 
                parent_field=test_def['parent_field'], parent_table=dataset[test_def['parent_dataset']].table_name)
    return q

def generate_field_sql(dataset, test_def):
    """Pulls out the two required fields to be compared for accuracy"""
    q = "select {field1}, {field2} from {table}".format(field1=test_def['fields'][0],
    field2=test_def['fields'][1], table=dataset[test_def['dataset']].table_name)
    return q

#TODO Setup the tests again

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

test_foreign_key_sql()
test_unique_sql()
"""