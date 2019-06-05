from NightingaleORM.fields import Field
import json


def translateSelect(database, schema, table, alias, shows, joins, wheres, brackets, orders, pk, count=1, offset=0):
    if database is None or schema is None or table is None:
        raise 'interpreter cannot find the db or table'
    sqlStr = ''
    parameters = []
    if shows is None or len(shows) <= 0:
        raise 'select field can not be empty'
    # select
    sqlStrTop = f'''SELECT {translateShow(alias,shows)}'''
    sqlStrCountTop = 'SELECT count(1)'
    # from
    schemaStr = '' if len(schema) <= 0 else f'.{schema}'
    sqlStr = f'''{sqlStr} 
FROM {database}{schemaStr}."{table}" {alias}'''

    # join
    sqlStr = f'''{sqlStr} {translateJoin(joins,parameters)}'''
    # where
    if (wheres is None or len(wheres) <= 0) and (brackets is None or len(brackets) <= 0):
        raise 'where fields cannot be empty'

    sqlStr = f'''{sqlStr} 
WHERE 1=1{translateWhere(alias,wheres,parameters)}'''

    for bracketItem in brackets:
        sqlStr = f'''{sqlStr} {bracketItem.relation} (1=1 {translateWhere(alias,bracketItem.whereList,parameters)})'''
    # countsql
    sqlStrCountTop = f'''{sqlStrCountTop}{sqlStr}'''
    # order
    sqlStr = f'''{sqlStr} {translateOrder(orders,pk)}'''
    # limit
    if count>0:
        sqlStr = f'''{sqlStr} 
LIMIT {count}'''
    if offset>0:
        sqlStr = f'''{sqlStr}  OFFSET {offset}'''
    return (sqlStrTop+sqlStr, parameters, sqlStrCountTop)

# 添加where条件


def translateWhere(alias, wheres, parameters):
    sqlStr = ''
    for whereField in wheres:
        if isinstance(whereField, str):
            sqlStr = f'''{sqlStr} {whereField}'''
        else:
            sqlStr = f'''{sqlStr} {whereField.relation} {'' if len(alias)<=0 else f'{alias}.'}{whereField.fields if isinstance(whereField.fields,str) else whereField.fields.name}'''
            if whereField.operation == 'IN' or whereField.operation == 'NOT IN':
                if isinstance(whereField.value, list):
                    sqlStr = f'''{sqlStr} {whereField.operation} ('''
                    for whereItem in whereField.value:
                        parameters.append(whereItem)
                        sqlStr = f'''{sqlStr}${len(parameters)},'''
                    sqlStr = sqlStr.strip(',')
                    sqlStr = f'''{sqlStr})'''
                else:
                    sqlStr = f'''{sqlStr} {whereField.operation} ({whereField.value})'''
            elif whereField.operation == 'LEFT LIKE':
                parameters.append(f'%{whereField.value}')
                sqlStr = f'''{sqlStr} LIKE $%{len(parameters)}'''
            elif whereField.operation == 'RIGHT LIKE':
                parameters.append(f'{whereField.value}%')
                sqlStr = f'''{sqlStr} LIKE ${len(parameters)}'''
            elif whereField.operation == 'RIGHT LIKE':
                parameters.append(f'%{whereField.value}%')
                sqlStr = f'''{sqlStr} LIKE ${len(parameters)}'''
            else:
                parameters.append(whereField.value)
                sqlStr = f'''{sqlStr} {whereField.operation} ${len(parameters)}'''
    return sqlStr


def translateShow(alias, shows):
    sqlStr = ''
    for showfield in shows:
        sqlStr = f'''{sqlStr}{'' if len(alias)<=0 else f'{alias}.'}{ showfield.name if isinstance(showfield, Field) else showfield},'''
    sqlStr = sqlStr.strip(',')
    return sqlStr


def translateJoin(joins, parameters):
    sqlStr = ''
    if joins is not None and len(joins) > 0:
        sqlStr = ''
        for joinfield in joins:
            if isinstance(joinfield, str):
                sqlStr = f'''{joinfield[0]}'''
            else:
                onList = joinfield.onList
                if len(onList) > 0:
                    joinSchemaStr = ''
                    joinTable = ''
                    if all([onList[0], onList[0].fields]):
                        joinSchemaStr=f'.{onList[0].fields.__schema__}' if onList[0].fields.__schema__ else ''
                        joinTable = f'''{onList[0].fields.__dateBase__}{joinSchemaStr}."{onList[0].fields.__table__}" '''
                    sqlStr = f'''{sqlStr} 
{joinfield.joinType} {joinTable} ON'''
                    isFirst=True
                    for eachOn in onList:
                        if isinstance(eachOn, str):
                            sqlStr = f'''{sqlStr} {eachOn}'''
                        else:
                            if isinstance(eachOn.value, str):
                                parameters.append(eachOn.value)
                            else:
                                sqlStr = f'''{sqlStr} {'' if isFirst else eachOn.relation} {eachOn.fields.name} {eachOn.operation} {f'${len(parameters)}' if isinstance(eachOn.value,str) else eachOn.value.name}'''
                        isFirst=False
    return sqlStr


def translateOrder(orders, pk):
    sqlStr = ''
    if orders and len(orders) > 0:
        sqlStr = f'''
ORDER BY
        '''
        for order in orders:
            if isinstance(order, str):
                sqlStr = f'''{sqlStr} {order}'''
            else:
                sqlStr = f'''{sqlStr} {order.field.name} {order.orderType},'''
        sqlStr = sqlStr.strip(',')
    else:
        sqlStr = f'''
ORDER BY {pk.name}'''
    return sqlStr


def translateInsert(database, schema, table, mapDict, valueDict):
    '''
    get the sql of insert
    mapDict：Model_feild to  of db_feild
    valueDict:the model_feild Name
    '''
    if database is None or schema is None or table is None:
        raise 'interpreter cannot find the db or table'
    if mapDict is None or valueDict is None:
        raise AttributeError(r"db feild or value not be  none")

    schemaStr = '' if len(schema) <= 0 else f'.{schema}'
    insertStr = f'''INSERT INTO {database}{schemaStr}."{table}"'''  # 执行的sql
    parameters = []  # 参数化的参数
    fields = []  # 字段名称
    values = []  # 值
    for k, v in mapDict.items():
        if v.primary_key:
            continue
        if k in valueDict:
            parameters.append(valueDict.get(k))
            fields.append(v.name)
            values.append(f'${len(parameters)}')
        elif v.default is not None:
            parameters.append(v.default)
            fields.append(v.name)
            values.append(f'${len(parameters)}')
    if len(parameters) > 0:
        insertStr = f'''{insertStr} 
({','.join(fields)}) 
VALUES ({','.join(values)})'''
    return insertStr, parameters

def translateUpdateModel(database, schema, table, mapDict, valueDict):
    '''
    get the sql of UPDATE
    mapDict：Model_feild to  of db_feild
    valueDict:the model_feild Name
    '''
    if database is None or schema is None or table is None:
        raise 'interpreter cannot find the db or table'
    if mapDict is None or valueDict is None:
        raise AttributeError(r"db feild or value not be  none")

    schemaStr = '' if len(schema) <= 0 else f'.{schema}'
    updateStr = f'''UPDATE {database}{schemaStr}."{table}"'''  # 执行的sql
    parameters = []  # 参数化的参数
    fields = []  # 字段名称
    where = () # where条件
    for k, v in mapDict.items():
        if v.primary_key:
            if k not in valueDict  :
                raise 'primary_key not valid'
            if  isinstance(valueDict.get(k),int) and valueDict.get(k)<=0:
                raise 'primary_key not valid'
            where=(v.name,valueDict.get(k))
            continue
        if  k in valueDict:
            parameters.append(valueDict.get(k))
            fields.append(v.name)
        elif v.default is  not None:
            parameters.append(v.default)
            fields.append(v.name)
    if len(parameters) < 0:
         raise 'Update cannot find '
    if len(where)!=2:
         raise 'model not primary_key'
    updateStr = f'''{updateStr} 
SET'''
    for index,field in enumerate(fields):
        updateStr = f'''{updateStr} {field}=${index+1},'''
    
    updateStr = updateStr.strip(',')#去除最后一个空格

    #拼接 where条件
    parameters.append(where[1])
    updateStr = f'''{updateStr} 
WHERE {where[0]}=${len(parameters)}'''
    return updateStr,parameters

def translateUpdate(database, schema, table, updates,wheres, brackets):
    '''
    get the update sql 
    '''
    if database is None or schema is None or table is None:
        raise 'interpreter cannot find the db or table'
    if len(updates)<=0:
        raise 'updates must be any' 
    if len(wheres)<=0:
        raise 'wheres must be any' 
    schemaStr = '' if len(schema) <= 0 else f'.{schema}'
    sqlStr = f'''UPDATE {database}{schemaStr}."{table}"'''
    parameters = []
    sqlStr=f'''{sqlStr}
{translateSet(updates,parameters)}
WHERE 1=1{translateWhere('',wheres,parameters)}'''
    for bracketItem in brackets:
        sqlStr = f'''{sqlStr} {bracketItem.relation} (1=1 {translateWhere('',bracketItem.whereList,parameters)})'''
    return sqlStr,parameters

def translateSet(updates,parameters):
    sqlStr = ''
    if  updates and len(updates)>0:
        sqlStr = f'''SET '''
        for eachUpdate in updates:
            if isinstance(eachUpdate, str):
                sqlStr=f'''{sqlStr}{eachUpdate},'''
            else:  
                parameters.append(eachUpdate.value)
                sqlStr = f'''{sqlStr}{eachUpdate.fields.name} = ${len(parameters)},'''
    sqlStr = sqlStr.strip(',')
    return sqlStr
    