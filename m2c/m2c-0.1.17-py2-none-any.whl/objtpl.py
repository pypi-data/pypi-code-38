#!/usr/bin/env python
#coding: utf-8
#by yangbin at 2018.11.28

OBJ_FIXED_CODE_TPL = '''
func Get$BIGOBJNAME$Table() *mgo.Collection {
	return $OBJNAME$Table
}

func Get(id int64) ($OBJNAME$ *$BIGOBJNAME$, err error) {
	$OBJNAME$ = &$BIGOBJNAME${}
	err = $OBJNAME$Table.FindId(id).One($OBJNAME$)
	if err != nil && err.Error() == "not found" {
		$OBJNAME$ = nil
		err = nil
	}
	return
}

func MustGet(id int64, outerr error) ($OBJNAME$ *$BIGOBJNAME$) {
	$OBJNAME$ = &$BIGOBJNAME${}
	err := $OBJNAME$Table.FindId(id).One($OBJNAME$)
	if err != nil && err.Error() == "not found" {
		$OBJNAME$ = nil
		err = nil
	}

    if err != nil {
        panic(err)
    } 

	if $OBJNAME$ == nil {
		panic(outerr)
	}
	return
}

func Save($OBJNAME$ *$BIGOBJNAME$) (err error) {
	if $OBJNAME$.Id == 0 {
		$OBJNAME$.Id = id.Gen("$OBJNAME$")
	}
	now := time.Now().Unix()
	if $OBJNAME$.CTime == 0 {
		$OBJNAME$.CTime = now
	}
	$OBJNAME$.MTime = now
	_, err = $OBJNAME$Table.UpsertId($OBJNAME$.Id, $OBJNAME$)
	return
}

func Update(id int64, updater map[string]interface{}) ($OBJNAME$ *$BIGOBJNAME$, err error) {
	now := time.Now().Unix()
	updater["mtime"] = now
	change := mgo.Change{
		Update:    bson.M{"$set": updater},
		Upsert:    true,
		ReturnNew: true,
	}
	$OBJNAME$ = &$BIGOBJNAME${}
	_, err = $OBJNAME$Table.Find(bson.M{"_id": id}).Apply(change, $OBJNAME$)
	if err != nil {
		$OBJNAME$ = nil
	}
	return
}

func Delete(id int64) (err error) {
	err = $OBJNAME$Table.RemoveId(id)
	if err != nil && err.Error() == "not found" {
		err = nil
	}
	return
}

type $BIGOBJNAME$Query struct {
	pageIndex int
	pageSize  int
	filter    bson.M
	or        []bson.M
	sort      []string
}

func Query() *$BIGOBJNAME$Query {
	return &$BIGOBJNAME$Query{
		filter: bson.M{},
		or:     []bson.M{},
	}
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) GetQuery() bson.M {
	if len($OBJNAME$Query.or) > 0 {
		$OBJNAME$Query.filter["$or"] = $OBJNAME$Query.or
	}
	return $OBJNAME$Query.filter
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) WithPage(pageIndex int64, pageSize int64) *$BIGOBJNAME$Query {
	$OBJNAME$Query.pageIndex = int(pageIndex-1) * int(pageSize)
	$OBJNAME$Query.pageSize = int(pageSize)
	return $OBJNAME$Query
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) WithFilter(filter map[string]interface{}) *$BIGOBJNAME$Query {
	if len($OBJNAME$Query.filter) == 0 {
		$OBJNAME$Query.filter = filter
	} else {
		for k, v := range filter {
			$OBJNAME$Query.filter[k] = v
		}
	}
	return $OBJNAME$Query
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) WithIn(key string, values interface{}) *$BIGOBJNAME$Query {
	$OBJNAME$Query.filter[key] = bson.M{"$in": values}
	return $OBJNAME$Query
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) WithNotIn(key string, values interface{}) *$BIGOBJNAME$Query {
	$OBJNAME$Query.filter[key] = bson.M{"$nin": values}
	return $OBJNAME$Query
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) WithSort(sort []string) *$BIGOBJNAME$Query {
	$OBJNAME$Query.sort = sort
	return $OBJNAME$Query
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) WithTextSearch(text string) *$BIGOBJNAME$Query {
	$OBJNAME$Query.filter["$text"] = bson.M{"$search": text}
	return $OBJNAME$Query
}

// https://docs.mongodb.com/manual/reference/operator/query/or/#or-and-text-queries
func ($OBJNAME$Query *$BIGOBJNAME$Query) OrTextSearch(text string) *$BIGOBJNAME$Query {
	$OBJNAME$Query.or = append($OBJNAME$Query.or, bson.M{"$text": bson.M{"$search": text}})
	return $OBJNAME$Query
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) Count() (n int64, err error) {
	_n, err := $OBJNAME$Table.Find($OBJNAME$Query.GetQuery()).Count()
	n = int64(_n)
	return
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) Update(updater map[string]interface{}) (updated int64, err error) {
	now := time.Now().Unix()
	updater["mtime"] = now
	change := bson.M{"$set": updater}
	info, err := $OBJNAME$Table.UpdateAll($OBJNAME$Query.GetQuery(), change)
	if err != nil {
		return
	}
	updated = int64(info.Updated)
	return
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) One() ($OBJNAME$ *$BIGOBJNAME$, err error) {
	$OBJNAME$ = &$BIGOBJNAME${}
	err = $OBJNAME$Table.Find($OBJNAME$Query.GetQuery()).Sort($OBJNAME$Query.sort...).One($OBJNAME$)
	if err != nil && err.Error() == "not found" {
		$OBJNAME$ = nil
		err = nil
	}
	return
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) MustOne(outerr error) ($OBJNAME$ *$BIGOBJNAME$) {
	$OBJNAME$ = &$BIGOBJNAME${}
	err := $OBJNAME$Table.Find($OBJNAME$Query.GetQuery()).Sort($OBJNAME$Query.sort...).One($OBJNAME$)
	if err != nil && err.Error() == "not found" {
		$OBJNAME$ = nil
		err = nil
	}

    if err != nil {
        panic(err)
    } 

	if $OBJNAME$ == nil {
		panic(outerr)
	}
	return
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) All() ($OBJNAME$ []*$BIGOBJNAME$, err error) {
	$OBJNAME$ = []*$BIGOBJNAME${}
	err = $OBJNAME$Table.Find($OBJNAME$Query.GetQuery()).Skip($OBJNAME$Query.pageIndex).Limit($OBJNAME$Query.pageSize).Sort($OBJNAME$Query.sort...).All(&$OBJNAME$)
	return
}

func ($OBJNAME$Query *$BIGOBJNAME$Query) Scan() (ch chan *$BIGOBJNAME$, err chan error) {
	iter := $OBJNAME$Table.Find($OBJNAME$Query.GetQuery()).Iter()
	ch = make(chan *$BIGOBJNAME$)
	err = make(chan error)
	go func() {
		defer iter.Close()
		defer close(ch)
		defer close(err)
		for {
			p := &$BIGOBJNAME${}
			if ok := iter.Next(p); ok {
				if p.CTime != 0 { // empty object
					ch <- p
				}
			}
			if iter.Err() != nil {
				err <- iter.Err()
				return
			}
			if iter.Done() {
				return
			}
		}
	}()
	return
}

// save $OBJNAME$
func ($OBJNAME$ *$BIGOBJNAME$) Save() (err error) {
	if $OBJNAME$.Id == 0 {
		$OBJNAME$.Id = id.Gen("$OBJNAME$")
	}
	now := time.Now().Unix()
	if $OBJNAME$.CTime == 0 {
		$OBJNAME$.CTime = now
	}
	$OBJNAME$.MTime = now
	_, err = $OBJNAME$Table.UpsertId($OBJNAME$.Id, $OBJNAME$)
	return
}
'''
OBJ_REF_HELPER_CODE_TPL = """
// single refer relation
func ({objName} *{ObjName}) Ref{RefName}({refName}Id int64) *{ObjName} {{
    {objName}.Ref{RefName}Id = {refName}Id
    return {objName}
}}

func ({objName} *{ObjName}) Get{RefName}() ({refName} *{refName}Object.{RefName}, err error) {{
    return {refName}Object.Get({objName}.Ref{RefName}Id)
}}
"""
OBJ_MGR_HELPER_CODE_TPL = '''
// manager relation, TODO transactions + upsert
func ({objName} *{ObjName}) Add{MgrShortName}({mgrShortName} *{mgrLongName}Object.{MgrLongName}) (err error) {{
    {mgrShortName}.Ref{ObjName}Id = {objName}.Id
    err = {mgrLongName}Object.Save({mgrShortName})
    if err != nil {{
        return
    }}
    {objName}.Mgr{MgrShortName}Id = {mgrShortName}.Id
    updater := map[string]interface{{}}{{
        "{mgrShortName}Id": {objName}.Mgr{MgrShortName}Id,
    }}
    {objName}, err = Update({objName}.Id, updater)
    return
}}

func ({objName} *{ObjName}) Get{MgrShortName}() ({mgrShortName} *{mgrLongName}Object.{MgrLongName}, err error) {{
    return {mgrLongName}Object.Get({objName}.Mgr{MgrShortName}Id)
}}
'''

OBJ_MGR_ARRAY_HELPER_CODE_TPL = '''
// array manager
func ({objName} *{ObjName}) Add{MgrShortName}({mgrShortName} *{mgrLongName}Object.{MgrLongName}) (err error) {{
	{mgrShortName}.Ref{ObjName}Id = {objName}.Id
	err = {mgrShortName}.Save()
	return
}}

func ({objName} *{ObjName}) Get{MgrShortName}ById({mgrShortName}Id int64) ({mgrShortName} *{mgrLongName}Object.{MgrLongName}, err error) {{
	return {mgrLongName}Object.Get({mgrShortName}Id)
}}

func ({objName} *{ObjName}) Query{MgrShortName}() (query{MgrShortName} *{mgrLongName}Object.{MgrLongName}Query) {{
	return {mgrLongName}Object.Query().WithFilter(map[string]interface{{}}{{
		"{objName}Id": {objName}.Id,
	}})
}}
'''
OBJ_MGR_REF_HELPER_CODE_TPL = '''
func ({objName} *{ObjName}) GetRef{ParentName}({parentName} interface{{}}) (err error) {{
	err = db.C("{parentName}").FindId({objName}.Ref{ParentName}Id).One({parentName})
	if err != nil && err.Error() == "not found" {{
		err = nil
	}}
	return
}}
'''
OBJ_FILTER_HELPER_CODE_TPL = '''
func ({objName}Query *{ObjName}Query) With{FieldName}Equal({fieldName} {filedType}) *{ObjName}Query {{
	{objName}Query.filter["{fieldName}"] = {fieldName}
	return {objName}Query
}}

func ({objName}Query *{ObjName}Query) With{FieldName}NotEqual({fieldName} {filedType}) *{ObjName}Query {{
	{objName}Query.filter["{fieldName}"] =  bson.M{{"$ne": {fieldName}}}
	return {objName}Query
}}
'''

OBJ_FILTER_STRING_LIKE_CODE_TPL = '''
func ({objName}Query *{ObjName}Query) Or{FieldName}Like({fieldName} string) *{ObjName}Query {{
	{objName}Query.or = append({objName}Query.or, bson.M{{"{fieldName}": bson.M{{"$regex": {fieldName}}}}})
	return {objName}Query
}}
func ({objName}Query *{ObjName}Query) With{FieldName}Like({fieldName} string) *{ObjName}Query {{
	{objName}Query.filter["{fieldName}"] = bson.M{{"$regex": {fieldName}}}
	return {objName}Query
}}
'''
