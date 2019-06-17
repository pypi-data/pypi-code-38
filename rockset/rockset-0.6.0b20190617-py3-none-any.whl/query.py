"""
Usage
-----

Query module contains a set of APIs that allows you to compose powerful
queries over collections.

This module comprises of two major components:

* ``Q`` : Query Builder
    Used to compose complex and powerful queries.

>>> from rockset import Q
>>> q = Q('hello-world').limit(10)
>>> (sqltxt, sqlargs) = q.sql()
>>> print(sqltxt)
SELECT *
FROM "hello-world"
LIMIT 10
>>>

* ``F`` : Field Reference
    Used to construct field expressions that refer to particular fields
    within a document.

>>> from rockset import F
>>> (F['answer'] == 42).sqlexpression()
'"answer" = 42'
>>>

Example
-------
::

    from rockset import Client, Q, F

    # connect to Rockset
    api_key = 'adkjf234rksjfa23waejf2'
    rs = Client(api_key=...)

    # fetch user whose "_id" == "u42"
    u = rs..query(Q('users').where(F["_id"] == "u42"))

    # fetch the 100 oldest users in the 'users' collection
    q = Q('users').highest(100, F["age"])
    old100 = rs.query(q)

    # find the average rating of all songs by "The Beatles"
    q = Q('songs').where(F["artist"] == "The Beatles").select(F["rating"].avg())
    avg_rating = rs.query(q)

Query Operators: Overview
-------------------------

.. autofunction:: rockset.Q

* Constructor

  * ``Q``: Specify the collection to be queried

  >>> # return all documents in the logins collection.
  >>> q = Q('logins')

* Filter queries

  * ``where``: Classic selection operator to only return documents that match \
the given criteria. Use ``F`` to construct field expressions to specify the \
selection criteria.

  >>> # return all docs in logins where field "user_id" is equal to "u42"
  >>> q = Q('logins').where(F['user_id'] == 'u42')

* Projection

  * ``select``: Specify the list of desired fields to be returned

  >>> # will return the fields "user_id" and "login_ip" from all docs in logins
  >>> q = Q('logins').select(F['user_id'], F['login_ip'])

* Pagination

  * ``limit`` : Specify limit with skip support

  >>> # return 10 documents from logins after skipping the first 40 results
  >>> q = Q('logins').limit(10, skip=40)

* Sorting

  * ``highest``, ``lowest``: Find the top N or the bottom N

  >>> # will return 10 documents with the most recent "login_time"
  >>> q = Q('logins').highest(10, F['login_time'])

* Aggregation

  * ``aggregate``: Group by and aggregate fields

  >>> # will aggregate all documents in logins by "user_id",
  >>> # and return "user_id", max("login_time") and count(*) after aggregation.
  >>> Q('logins').aggregate(F['user_id'], F['login_time'].max(), F.count())

* Joins

  * ``join``:  Regular JOIN operator
  * TODO: docs coming soon
  * ``lookup``: LEFT OUTER JOIN operator
  * TODO: docs coming soon
  * ``apply``: Graph traversal operator
  * TODO: docs coming soon

Field Expressions Overview
--------------------------

.. autodata:: rockset.F

* Value comparators

  * ``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=``:

  >>> # match all docs where "first_name" is equal to "Jim"
  >>> F["first_name"] == "Jim"
  >>> # match all docs where "rating" is greater than or equal to 4.5
  >>> F["rating"] >= 4.5
  >>> # match all docs where "title" text is lexographcially greater than "Star Wars"
  >>> F["title"] >= "Star Wars"

* String functions

  * ``startswith``, ``like``: Prefix and classic SQL LIKE expressions

  >>> # match all docs where "title" starts with "Star Wars"
  >>> F["title"].startswith("Stars Wars")
  >>> # match all docs where "title" contains the word "Wars"
  >>> F["title"].like("% Wars %")

* Boolean compositions

  * ``&``, ``|``, ``~``: AND, OR and NOT expressions

  >>> # match all records with "rating" >= 4.5 AND "title" starts with "Star Wars"
  >>> e1 = (F["rating"] >= 4.5) & F["title"].startswith("Star Wars")
  >>> # match all records with "director" == "George Lucas" OR "title" starts with "Star Wars"
  >>> e2 = (F["director"] == 'George Lucas') | F["title"].startswith("Star Wars")
  >>> # match all records that are not included in expressions e1 or e2
  >>> e1e2_complement = ~(e1 | e2)

* Field aggregations

  * ``avg``, ``collect``, ``count``, ``countdistinct``, ``max``, ``min``, ``sum``

  >>> # count(*)
  >>> F.count()
  >>> # min(login_time)
  >>> F["login_time"].min()
  >>> # max(login_time) as last_login_time
  >>> F["login_time"].max().named('last_login_time')

* Nested documents and arrays

  * ``[]``: The ``[]`` notation can be used to refer to fields within nested documents and arrays.

  * Consider a collection where documents looked like this example below.

  ::

    {
      "_id": {"u42"},
      "name": {
          "first": "James",
          "middle": "Nicholas",
          "last": "Gray" },
      "tags": [
          "ACID",
          "database locking",
          "two phase commits",
          "five-minute rule",
          "data cube",
          "turing award" ]
     }

  * Example field references to access nested documents and arrays:

  >>> # expression to find all documents where field "name" contains a
  >>> # nested field "middle" with value equal to "Nicholas"
  >>> F["name"]["middle"] == "Nicholas"
  >>>
  >>> # similarly, for array fields, you can specify the array offset.
  >>> # expression to find all documents where the first "tags" field
  >>> # is equal to "ACID"
  >>> F["tags"][0] == "ACID"

  * In order to match against any element within an array field, you can use
    Python's empty slice ``[:]`` notation.

  >>> # expression to find all documents where the "tags" array field
  >>> # contains "ACID" as one of the elements
  >>> F["tags"][:] == "ACID"
  >>> # find all documents where one of the "tags" is "turing award"
  >>> F["tags"][:] == "turing award"


--------------

Query Operator: Filters
-----------------------

=========================
Where operator
=========================
    Syntax:
    ``<Query>.where(<Query>)``

    ``where`` allows you to chain a new query object as a conjuntion.
    In most cases, field reference expressions are sufficient, but
    ``where`` comes in especially handy when you want to sub-select
    documents following another operation such as a sort or an aggregation.

    Examples:
    ::

      # find all "Jim"s who are in the top 100 highest scorers
      Q('players')  \\
      .highest(100, F["score"])  \\
      .where(F["first_name"] == "Jim")

.. automethod:: Query.where

Query Operator: Projection
--------------------------

=========================
Select operator
=========================
    Syntax:
    ``<Query>.select(<field_ref> [, <field_ref> [, ...]])``

    Allows you to specify the fields that you wish to include in the
    query results.

    Examples:
    ::

      Q('authors') \\
      .where(F["last_name"] == "Gray")  \\
      .select(F["first_name"], F["last_name"], F["age"])

.. automethod:: Query.select

Query Operator: Pagination
--------------------------

=========================
Limit operator
=========================
    Syntax:
    ``<Query>.limit(<max_results> [, <skip_count>])``

    Limit operator allows you to perform pagination queries and positional
    filters.

    Examples:
    ::

      # find the "_id" field of the 5 most recently uploaded documents
      # since the default sorting is more recently updated first,
      # this query will simply be:
      Q('uploads').limit(5)

      # fetch a third batch of 100 results, for all users older than 18
      # i.e., skip the first 200 results
      Q('uploads').where(F["age"] >= 18).limit(100, skip=200)

.. automethod:: Query.limit

Query Operator: Sorting
-----------------------

=========================
Highest, Lowest operators
=========================
    Syntax:
    ``<Query>.highest(N, <field_ref> [, <field_ref> [, ...]])``,
    ``<Query>.lowest(N, <field_ref> [, <field_ref> [, ...]])``

    Examples:
    ::

      Q(F["last_name"] == "Gray").highest(5, F["score"], F["first_name"])
      Q(F["last_name"] == "Gray").lowest(10, F["salary"])

.. automethod:: Query.highest
.. automethod:: Query.lowest


Query Operator: Aggregation
---------------------------

====================================================
Aggregate operator and field ref aggregate functions
====================================================
    Syntax:
    ``<Query>.aggregate(<field_ref> [, <field_ref> [, ...]])``

    Field reference objects can also include any of the following aggregation
    functions:

    * ``min``
    * ``max``
    * ``avg``
    * ``sum``
    * ``count``
    * ``countdistinct``
    * ``approximatecountdistinct``
    * ``collect``

    You can also optionally provide a field name alias in the
    field reference using the ``named`` function. This comes in
    especially handy for the aggregated fields.

    Examples:
    ::

      # find min and max salaries broken down by age
      Q('employees').aggregate(F["age"], F["salary"].min(), F["salary"].max())
      # will return documents such as:
      # {"age", "18", "min(salary)": 50000, "max(salary)": 150000}
      # {"age", "19", "min(salary)": 50000, "max(salary)": 152000}

      # example using field name alias
      Q('employees').aggregate(F["age"], F["salary"].avg().named("avg_salary"))
      # will return documents such as:
      # {"age", "18", "avg_salary": 82732}

.. automethod:: Query.aggregate

.. automethod:: FieldRef.min
.. automethod:: FieldRef.max
.. automethod:: FieldRef.avg
.. automethod:: FieldRef.sum
.. automethod:: FieldRef.count
.. automethod:: FieldRef.countdistinct
.. automethod:: FieldRef.approximatecountdistinct
.. automethod:: FieldRef.collect

Query Operator: Joins
---------------------------

=========================
Lookup operator
=========================

    Syntax:
    ``<Query>.lookup(<local_field_ref> \
[, <target_field_ref>] \
[, <target_query_ref>] \
[, <new_field_ref>])``

    Lookup operator allows you to perform a LEFT OUTER JOIN between results
    of the current ``<Query>`` object and the results of the
    ``<target_query_ref>``.

    The LEFT OUTER JOIN operation will be performed on the
    ``<local_field_ref>`` from the results of the current ``<Query>`` object
    and the ``<target_field_ref>`` in ``<target_query_ref>``.

    The output of the JOIN operation will be presented as an array value
    within the ``<new_field_ref>`` in the post JOIN results.

    Examples:
    ::

      # Assume you have following 2 collections:
      #
      # "employees" collection:
      #   {"_collection": "emp", "_id": "e42",
      #       "name": "Jim Gray", "deptId": "d7" }
      #   {"_collection": "emp", "_id": "e43",
      #       "name": "Peter Parker", "deptId": "d8" }
      #   {"_collection": "emp", "_id": "e44",
      #       "name": "Jane Doe", "deptId": null }
      #   {"_collection": "emp", "_id": "e45",
      #       "name": "John Smith" }
      #
      # "dept" collection (only has "d7" but no "d8"):
      #   {"_collection": "dept", "_id": "d7", "name": "eng" }
      #

      # fetch all employees along with their relevant dept records
      rs = Client()
      q = Q("emp").lookup(F["deptId"], target_field=F["_id"],
              target_query=Q("dept"))
      everyone = rs.query(q)

      # the above query will return the following results:
      #
      # [ {"_collection": "emp", "_id": "e42",
      #       "name": "Jim Gray", "deptId": "d7",
      #       "deptId:lookup":
      #           [ {"_collection": "dept", "_id": "d7", "name": "eng"} ]
      #   },
      #   {"_collection": "emp", "_id": "e43",
      #       "name": "Peter Parker", "deptId": "d8",
      #       "deptId:lookup": [ ]
      #   },
      #   {"_collection": "emp", "_id": "e44",
      #       "name": "Jane Doe", "deptId": null,
      #       "deptId:lookup": null
      #   },
      #   {"_collection": "emp", "_id": "e45",
      #       "name": "John Smith"
      #   }
      # ]


    Another example:
    ::

      # another query on the same two collections described above
      # example to fetch name of employee "u42" along with their dept name
      #
      # first define target_query to only select dept id (JOIN field) and name
      target_query = Q("dept").select(F["_id"], F["name"])

      #
      # LEFT OUTER JOIN between employee "u42" and target_query
      # Note: default target_field '_id' works here and is not specified
      jim = Q("emp").where(F["_id"] == "u42").lookup(
                local_field=F["deptId"],
                target_query=target_query,
                new_field=F["dept"])

      #
      # only select relevant fields post JOIN
      jim = jim.select(F["name"], F["dept"])

      # execute the query
      rs = Client()
      everyone = rs.query(jim)

      # the above query will return the following results:
      # [ { "name": "Jim Gray", "dept": [ {"_id": "d7", "name": "eng"} ]
      #   }
      # ]

.. automethod:: Query.lookup

.. _Graph queries:

=========================
Apply operator
=========================
    Syntax:
    ``<Query>.apply(<field_ref>)``

    Apply operator matches all documents whose ``<field_ref>``
    value matches the results of the given ``<Query>``.

    Apply operators enable graph queries that allows you to perform
    graph traversals across related fields in different collections
    without requiring any special data shaping or schema modeling or
    graph specific indexing.

    The common pattern for using ``apply`` will look as follows:

    Step 1: Search, process and filter for relevant documents

    Step 2: Select the field that defines the source vertex

    Step 3: Apply over the field that defines the destination vertex

    Step 4: Go back to Step 1 for another graph traversal hop, if required.

    Examples:
    ::

      # Assume you have following 2 collections:
      #
      # "bad_ips" collection:
      #   {"_collection": "bad_ips", "ip_address": "106.6.6.6", "last_seen": ... }
      #   {"_collection": "bad_ips", "ip_address": "107.6.6.6", "last_seen": ... }
      #
      # "login_attempts" collection:
      #   {"_collection": "login_attempts", "login_ip": "72.43.99.108", ... }
      #   {"_collection": "login_attempts", "login_ip": "106.6.6.6", ... }
      #
      # You can model the above 2 collections as a graph, where there exists
      # an edge between every login_attempts.login_ip and the corresponding
      # bad_ips.ip_address
      #
      # The following query will find all login_attempts from any of the
      # bad_ips:
      rs = Client()
      results = rs.query( Q("bad_ips")  \\
                               .select(F["ip_address"])  \\
                               .apply(F["login_ip"], Q("login_attempts")) )

      # the slow and inefficient way to achive the same would be to
      # materialize the list of all bad_ips and then building out a
      # new query object which could potentially be quite big.
      # DO NOT USE THIS. USE APPLY OPERATOR INSTEAD.
      bad_ips = rs.query(Q("bad_ips"))
      suspicious_logins = None
      for bad_ip in bad_ips:
          is_login_ip_bad = (F["login_ip"] == bad_ip["ip_address"])
          if suspicious_logins:
              suspicious_logins |= is_login_ip_bad
          else:
              suspicious_logins = is_login_ip_bad

      # execute the query against "login_attempts"
      results = rs.query(Q("login_attempts").where(suspicious_logins))


    Another example:
    ::

      # Assume you have following 3 collections:
      # "users"
      # {"_id": "u42", "name": "Patrick", "zip": "94107"}
      # {"_id": "u67", "name": "Paul", "zip": "94306"}
      #
      # "merchants"
      # {"_id": "m2345", "name": "Muddy Waters", "zip": "53706"}
      # {"_id": "m8442", "name": "Beli Deli", "zip": "94002"}
      #
      # "payments"
      # {"_id": "p23rsdkjkapw3", "payer": "u42", "merchant": "m2345", "amount": 17.45, "time": 1488244768}
      # {"_id": "qase8432akdfa", "payer": "u67", "merchant": "m8442", "amount": 42.72, "time": 1488244807}
      # {"_id": "r23raskdfa235", "payer": "u42", "merchant": "m8442", "amount": 11.83, "time": 1488244942}
      # {"_id": "s06slkgeka92s", "payer": "u42", "merchant": "m8442", "amount": 10000, "time": 1488244944}
      #

      # find all merchants in zip code 53706,
      # then find all of their payments,
      # then find the top 100 users by total amount spent
      merchants = Q("merchants").where(F["zip"] == "53706")
      payments  = merchants.select(F["_id"]).apply(F["merchant"], Q("payments"))
      all_users = payments.aggregate(F["payer"], F["amount"].sum().named("total_amount"))
      top_users = all_users.highest(10, F["total_amount"])

      # execute the top_users query
      rs = Client()
      results = rs.query(top_users)

.. automethod:: Query.apply

--------------

Field Expression: Value Comparators
-----------------------------------

=========================
Equality operator: ``==``
=========================
    Supported types: ``int``, ``float``, ``bool``, ``str``

    Syntax:
    ``<field_ref> == <value>``

    Examples:
    ::

      F["first_name"] == "Jim"
      F["year"] == 2017
      F["score"] == 5.0
      F["tags"][:] == 'critical'

===============================================
Value comparators: ``<``, ``<=``, ``>=``, ``>``
===============================================
    Supported types: ``int``, ``float``, ``str``

    Syntax:
    ``<field_ref> < <value>``,
    ``<field_ref> <= <value>``,
    ``<field_ref> >= <value>``,
    ``<field_ref> > <value>``

    Examples:
    ::

      F["year"] < 2000
      F["year"] >= 2007
      F["rating"] >= 4.5
      F["title"] >= "Star Wars"

===============================
Prefix operator: ``startswith``
===============================
    Supported types: ``str``

    Syntax:
    ``<field_ref>.startswith(<prefix>)``

    Examples:
    ::

      F["first_name"].startswith("Ben")

===============================
Like operator: ``like``
===============================
    Supported types: ``str``

    Syntax:
    ``<field_ref>.like(<pattern>)``

    Examples:
    ::

      F["address"].like("%State St%")

===============================
Field alias: ``named``
===============================
    Supported types: All field references

    Syntax:
    ``<field_ref>.named(<new-field-name>)``

    Examples:
    ::

      F["full_name"].named("name")
      F["login_time"].max().named("last_login_time")

===============================
Field existence: ``is_defined``
===============================
    Supported types: All

    Syntax:
    ``<field_ref>.is_defined()``

    Field existence tested with ``<field_ref>.is_defined()`` will match all
    documents where the field is defined, even if it has a null value.

================================
Null comparison: ``is_not_null``
================================
    Supported types: All

    Syntax:
    ``<field_ref>.is_not_null()``

    Field expression ``<field_ref>.is_not_null()`` will match all documents
    where the field is defined and has a non-null value.

.. tip:: There is no ``is_null()`` because of the potential confusion of \
calling ``is_null()`` on an undefined field. Use \
``~<field_ref>.is_not_null()`` or ``<field_ref>.is_defined() & \
~<field_ref>.is_not_null()`` depending on your use case.

=========================
Nested operator
=========================
    Syntax:
    ``<field_ref>.nested(<Query>)``

    ``nested`` operator makes it easy to work with nested array of documents.

    Example:
    ::

        # find all books authored by 'Jim Gray'
        F["authors"].nested((F["first_name") == "Jim") \
& (F["last_name"] == "Gray"))

        # find all users who logged in from given IP on June 06, 2006
        F["logins"].nested((F["ipv4"] == "10.6.6.6") \
& (F["login_date"] == "2006-06-06"))


Field Expression: Boolean Compositions
--------------------------------------

Three different boolean operators (``&``, ``|``, and ``~``) are
overloaded to allow easy composition of boolean operators.

.. note:: The boolean operators are **NOT** ``and``, ``or``, and ``not``, \
as those are special and cannot be overridden in Python.

==================================
AND operator: ``&`` (intersection)
==================================
    Syntax:
    ``<Query object> & <Query object>``

    Examples:
    ::

      # find all documents where field tags contains the "turing award"
      # and the age is greater than 40
      (F["tags"][:] == "turing award") & (F["age"] > 40)

==========================
OR operator: ``|`` (union)
==========================
    Syntax:
    ``<Query object> | <Query object>``

    Examples:
    ::

      # find all documents where the first_name is "jim"
      # or last_name is "gray"
      (F["first_name"] == "jim") | (F["last_name"] == "gray")

==============================
NOT operator: ``~`` (negation)
==============================
    Syntax:
    ``~<Query object>``

    Examples:
    ::

      # find all documents whose title does not contain the term "confidential"
      ~F["title"][:] == "confidential"


"""
import copy
import json
from .value import encode, decode, py_type


class Query(object):
    def __init__(self, source=None, alias=None, child=None, children=None):
        self._source = source
        self._alias = alias

        if child:
            self._source = child.get_source()

        if children:
            for c in children:
                if c.get_source() and not self.get_source():
                    self._source = c.get_source()
                if (
                    self.get_source() and c.get_source() and
                    self.get_source() != c.get_source()
                ):
                    raise ValueError(
                        'Cannot combine multiple sub-queries '
                        'bound to different target collections. '
                    )

        # if query is bound to a collection, then init FieldRef
        # so one can do q.F['name']
        if self.get_source():
            self.F = FieldRef(source=(self.get_alias() or self.get_source()))
        else:
            self.F = FieldRef()

        # init params to empty map
        self.P = ParamDict()  # params explicitly set by user

    def __and__(self, other):
        if not isinstance(other, Query):
            return NotImplemented
        return AndQuery([self, other])

    def __or__(self, other):
        if not isinstance(other, Query):
            return NotImplemented
        return OrQuery([self, other])

    def __sub__(self, other):
        if not isinstance(other, Query):
            return NotImplemented
        return DifferenceQuery(self, other)

    def __invert__(self):
        return NotQuery(self)

    # property getters
    def get_source(self):
        return self._source

    def get_alias(self):
        return self._alias

    def select(self, *fields):
        """ Returns a new query object that when executed will only include
        the list of fields provided as input.

        Args:
            fields (list of FieldRef): fields you wish to select

        Returns:
            Query: new query object that includes the desired field selection
        """
        return SelectQuery(fields, self)

    def where(self, query):
        """ Returns a new query object that when executed will only return
        documents that match the current query object AND the query object
        provided as input.

        Args:
            query (Query): the conjunct query object

        Returns:
            Query: new query object that returns documents in
            **self** AND **query**
        """
        return WhereQuery(query, self)

    def highest(self, limit, *fields):
        """ Returns a new query object that when executed will sort the results
        from the current query object by the list of fields provided as input
        in descending order and return top N defined by the limit parameter.

        Args:
            limit (int): top N results you wish to fetch
            fields (list of FieldRef): fields you wish to sort
            descending by

        Returns:
            Query: new query object that returns top N descending
        """
        return SortQuery('desc', fields, self).limit(limit)

    def lowest(self, limit, *fields):
        """ Returns a new query object that when executed will sort the results
        from the current query object by the list of fields provided as input
        in ascending order and return top N defined by the limit parameter.

        Args:
            limit (int): top N results you wish to fetch
            fields (list of FieldRef): fields you wish to sort
            ascending by

        Returns:
            Query: new query object that returns top N ascending
        """
        return SortQuery('asc', fields, self).limit(limit)

    def aggregate(self, *fields):
        """ Returns a new query object that when executed will aggregate
        results from the current query object by the list of fields
        provided as input.

        Field reference objects can include one of the supported aggregate
        functions such as ``max``, ``min``, ``avg``, ``sum``,
        ``count``, ``countdistinct``, ``approximatecountdistinct``, ``collect``
        as follows: ``<field_ref>.max()``, ``<field_ref>.min()``, ... .

        The list of fields provided as input can contain a mix of field
        references that include an aggregate function and field references
        that does not.

        Args:
            fields (list of FieldRef): fields you wish to aggregate by

        Returns:
            Query: new query object that includes the desired field aggregations
        """
        return AggregateQuery(fields, self)

    def lookup(
        self, local_field, target_field=None, target_query=None, new_field=None
    ):
        """ Lookup allows you to perform a LEFT OUTER JOIN between the results
        of the current query object and the results of the target_query
        provided as input. The LEFT OUTER JOIN operation will be performed
        on the local_field from the results of the current query object
        and the target_field field in target_query. All results from the
        target_query whose target_field value matches the local_field value,
        will be presented as an array value within the new_field in the post
        JOIN results.

        **local_field**:
        For every result document in the current query object, the value of
        the local_field is JOINed against the target_field in the
        target_query. All the documents that match from the target_query
        are presented in a new field whose field name defined by the new_field
        parameter.

        This field is mandatory.

        **target_field**:
        The field from the target_query results against which the local_field
        should be JOINed with.

        This field is optional.

        Default value for target_field is ``F["_id"]`` field.

        **target_query**:
        Defined as a Query object, whose results will be used to JOIN against
        the local_field. The results from the target_query should include
        the target_field.

        All fields selected from the target_query will be present within the
        new_field in the post JOIN results.

        This field is optional.

        Default value for target_query is ``Q(<source-collection>)``, which
        will return all documents in the current collection.

        **new_field**:
        New field in every result document will contain  an array value of all
        the matching results from the target_query.

        If the local field is undefined in a result document,
        then the new field will also be undefined in that result document.

        If the local field value is null in a result document,
        then the new field will also be null in that result document.

        If the local field value is defined and not null in a result document,
        then the new field will have an array of all the documents from the
        target query results whose target field matches the local field value.

        The new field will be an empty array if there are no matches.

        This new field name is optional and defaults to local field name
        concatenated with ``:lookup``.

        .. note:: If the target_query does not contain target_field, then there \
        will not be any matches with the local_field value, and thus the \
        new_field will be an empty array for all results.

        Args:
            local_field (FieldRef): local field you wish to perform the
                LEFT OUTER JOIN.
                This is a required parameter.
            target_field (FieldRef): target field in the target query
                against which you wish to perform the LEFT OUTER JOIN.
                This is an optional parameter.
                Default value: ``F['_id']`` field
            target_query (Query): defines a Query object, whose results will
                be used to match against the local_field.
                This is an optional parameter.
                Defaults to ``Q(<source-collection>)``
            new_field (FieldRef): defines a new field where the results of
                LEFT OUTER JOIN will be present.
                This is an optional parameter.
                Defaults to local field name concatenated with ":lookup".

        Returns:
            Query: new query object that includes the desired LEFT OUTER JOIN
        """
        return LookupQuery(
            local_field,
            new_field=new_field,
            target_field=target_field,
            target_query=target_query,
            child=self
        )

    def apply(self, to_field, target_query=None):
        """ Returns a new query object that when executed will match all
        documents where values of the to_field provided as input will match
        any of the results from the current query object.

        The current query object is expected to have a single field in them,
        and is commonly achieved using the **select** operator.

        Read more about the ``apply`` operator in the `Graph queries`_
        section.

        Args:
            to_fields (FieldRef): field you wish to match the results with
            target_query (Query): Optional. Use this for cross-collection
                graph queries, where the apply needs to work on a different
                collection than what the current query object is referring to.

        Example:
            Find all login IP addresses for user 'u42', and then find all
            activity logs from any of those IP addresses::

                Q('logins')
                  .where(F['user'] == 'u42')
                  .select(F['source_ip'])
                  .apply(F['ip_address'], Q('activity_logs'))


        Returns:
            Query: new query object that includes the desired apply operation
        """
        return ApplyQuery(to_field, self, target_query=target_query)

    def limit(self, limit, skip=0):
        """ Returns a new query object that when executed will only return
        a subset of the results. The query when executed will return no more
        than ``limit`` results after skipping the first ``skip`` number of
        results. The limit operator is most commonly used for pagination.

        Args:
            limit (int): maximum number of results to return
            skip (int): the number of results to skip

        Returns:
            Query: new query object that only returns the desired subset
        """
        return LimitQuery(limit=limit, skip=skip, child=self)

    def sample(self, ratio):
        """ Returns a new query object that when executed will only return
        a uniformly sampled subset of the results. When ratio is 0.1, 1 out of
        every 10 results will be returned.

        Args:
            ratio (float): sampling ratio between 0.0 and 1.0
                0.0 (0% sampling) will not return any results
                1.0 (100% sampling) will return all results

        Returns:
            Query: new query object that only returns the desired subset
        """
        return SampleQuery(ratio=ratio, child=self)

    def boost(self, factor):
        """ Returns a new query object that boosts the results from the given
        query object. Commonly, used along with the the Query.search method,
        to rank certain query contidions higher than other within a single
        search query.

        Eg::

            Q('tv-series').search(
                F["title"].proximity("game of thrones").boost(1.5),
                F["article_body"].proxmity("game of thrones").boost(1.0),
                (F["popular"] == "yes").boost(3.0))

        Args:
            factor (float): boost factor that determines the relevance of the
                matching results.

                Default boost factor is 1.0.
                Need to be a postive float > 0.0, but can be < 1.0.
                Higher boost factors will make matching documents more relevant.

        Returns:
            Query: new query object that incorporate the desired boost
        """
        return BoostedQuery(factor=factor, child=self)

    def search(self, *conditions):
        """ Returns a new query object that performs a search query against
        the given set of conditions.

        Documents that match all the conditions will be considered more
        relevant and should appear before documents that only match
        a subset of the given conditions.

        Unlike boolean AND queries that will only return if all the
        conditions are met, search queries perform a Weak-AND, where if no
        documents match all of the given criteria, then the ones that match
        most of the conditions will be returned.

        Each of the individual conditions could be boosted using the Query.boost
        method to control the relevance of each input query condition.

        Eg::

            Q('tv-series').search(
                F["title"].proximity("game of thrones").boost(1.5),
                F["article_body"].proxmity("game of thrones").boost(1.0),
                (F["popular"] == "yes").boost(3.0))

        Args:
            conditions (list of Query): conditions you want to search against

        Returns:
            Query: new search query object with the given set of conditions
        """
        return SearchQuery(conditions=conditions, child=self)

    def score(self, name, code, context=''):
        """ Returns a new query object that performs custom scoring on
        documents. Each document is added (or modified) a ':score' field
        and sorted based on that field, in descending order.

        The first parameter is name of the custom scorer. The only one currently
        supported is a javascript scorer, with a name 'js'.

        For the javascript scorer, the second parameter is a custom javascript
        code that is executed on each document. The code needs to export a
        function called 'score' that takes two parameters: 1) a document to be
        scored, 2) context (see third parameter). Unfortunatley only
        ECMAScript 5.1 is supported at the moment.

        The third parameter is context, which is passed to the javascript
        function as-is. It can be either a string or a dictionary. Dictionary
        will be converted to JSON when passed to javascript function.

        Eg::

            Q('tv-series').search(
                F["title"].proximity("game of thrones"))
                .score("js",
                       ("var score = function(doc, context) "
                       "{ return doc[':score'] * context['boost']; }"),
                       {"boost": 1.2})

        Args:
            name (str): name of the scorer, currently only "js" is supported
            code (str): In javascript scorer, custom javascript code that
                        scores the document
            context (str or dict): In javascript scorer, context that will be
                                   passed to javascript function

        Returns:
            Query: new score query object with the given set of parameters
        """
        return ScoreQuery(name, code, context, child=self)

    def __str__(self):
        try:
            return self.sql()[0]
        except NotImplementedError:
            return repr(self)

    def sqlprepare(self, sqlsel):
        """ Returns an SQLSelect object, which can be used to build
        the SQL version of the query.
        """
        return sqlsel

    def sqlbuild(self, sqlsel):
        """ Returns an SQLSelect object, which can be used to generate
        the SQL text for the query.
        """
        raise NotImplementedError(
            'Class {} does not implement sqlbuild()'.format(type(self))
        )

    def sqlexpression(self, **kwargs):
        """ Returns a text SQL fragment for the underlying query expression.
        """
        raise NotImplementedError(
            'Class {} does not implement sqlexpression()'.format(type(self))
        )

    def sql(self, **kwargs):
        """ Returns a tuple of (SQL, params) for the underlying query
        expression.
        """
        # step 1: prepare and get all sql params
        params = ParamDict()
        params.update(self.P)
        sqlsel = self.sqlprepare(SQLSelect(params=params))
        sqlsel.P.update(self.P)  # merge with user set params

        # step 2: build the SQL expression into sqlsel
        sqlsel = self.sqlbuild(sqlsel)

        # step 3:
        # translate sqlsel into sql text and return sql params from step 1
        return (sqlsel.sqlexpression(**kwargs), sqlsel.P)


def _sqlexp(s, delim=' ', **kwargs):
    s = decode(s)
    if isinstance(s, list) or isinstance(s, tuple):
        return delim.join([_sqlexp(x, **kwargs) for x in s])
    if isinstance(s, set):
        return delim.join(sorted(set([_sqlexp(x, **kwargs) for x in s])))
    if isinstance(s, bool):
        return str(s).lower()
    if isinstance(s, int) or isinstance(s, float):
        return str(s)
    if isinstance(s, str):
        return json.dumps(s)
    if isinstance(s, slice):
        return Symbol('[*]')
    if isinstance(s, (SubQuery, SQLSelectSubQuery)):
        kwargs['level'] = kwargs.get('level', 0) + 1
    return s.sqlexpression(**kwargs)


def _sqlprep(sqlsel, *args, **kwargs):
    for arg in args:
        if not hasattr(arg, 'sqlprepare'):
            continue
        if not callable(arg.sqlprepare):
            continue
        sqlsel = arg.sqlprepare(sqlsel)
    return sqlsel


def _escape_chars(v, chars=set()):
    for c in set(chars):
        v = v.replace(c, r"\{}".format(c))
    return v


class SQLSelect(object):
    def __init__(self, params=None):
        self._select_list = []
        self._from_list = []
        self._join_list = []
        self._where_list = []
        self._groupby_list = []
        self._orderby_list = []
        self._limit = None
        self._skip = None
        self._build_order = 0
        self.P = params or ParamDict()

    def _set_build_order(self, build_order):
        if self._build_order < build_order:
            self._build_order = build_order
        return self

    def _enforce_build_order(self, build_order, coalesce=False):
        """ use to automatically nest and build inner subquery in
        cases such as Q().aggregate().limit().where()
        """
        if self._build_order < build_order:
            return self._set_build_order(build_order)
        if coalesce and self._build_order == build_order:
            return self
        sq = SQLSelectSubQuery(child=self, alias='subq')
        return (SQLSelect(params=self.P)
            .add_from(sq)
            ._set_build_order(build_order))

    def add_select(self, *f):
        # allow select from any order, so default to current
        build_order = self._build_order
        # unless select list is non-empty, then force a nested sub query
        if len(self._select_list) > 0:
            build_order = 0
        this = self._enforce_build_order(build_order, coalesce=True)
        this._select_list += f
        return this

    def add_from(self, *t):
        this = self._enforce_build_order(1)
        this._from_list += t
        return this

    def add_join(self, r, p, join_type='JOIN'):
        this = self._enforce_build_order(1, coalesce=True)
        this._join_list.append((Symbol(join_type), r, p))
        return this

    def add_left_outer_join(self, r, p):
        return self.add_join(r, p, join_type='LEFT OUTER JOIN')
        return this

    def add_where(self, *op):
        this = self._enforce_build_order(2, coalesce=True)
        this._where_list += op
        return this

    def add_groupby(self, *f):
        this = self._enforce_build_order(3)
        this._groupby_list += f
        return this

    def add_orderby(self, mode, *fields):
        this = self._enforce_build_order(4)
        this._orderby_list += [(field, Symbol(mode)) for field in fields]
        return this

    def add_limit(self, limit, skip=0):
        this = self._enforce_build_order(5)
        this._limit = limit
        this._skip = skip
        return this

    def sqlexpression(self, **kwargs):
        linesep = '\n' + (' ' * kwargs.get('level', 0) * 7)
        ret = ''
        select_list = self._select_list or [F]
        ret += 'SELECT {} '.format(
            _sqlexp(select_list, delim=', ', **kwargs)
        )
        if self._from_list:
            ret += linesep
            ret += '  FROM {} '.format(
                _sqlexp(self._from_list, delim=', ', **kwargs)
            )
        if self._join_list:
            ret += linesep
            for j in self._join_list:
                ret += '    {} {} ON {} '.format(
                    _sqlexp(j[0], **kwargs), _sqlexp(j[1], **kwargs),
                    _sqlexp(j[2], **kwargs)
                )
        if self._where_list:
            ret += linesep
            ret += ' WHERE {} '.format(
                _sqlexp(self._where_list, delim=' AND ', **kwargs)
            )
        if self._groupby_list:
            ret += linesep
            ret += ' GROUP BY {} '.format(
                _sqlexp(self._groupby_list, delim=', ', **kwargs)
            )
        if self._orderby_list:
            ret += linesep
            ret += ' ORDER BY {} '.format(
                _sqlexp(self._orderby_list, delim=', ', **kwargs)
            )
        if self._limit:
            ret += linesep
            ret += ' LIMIT {} '.format(_sqlexp(self._limit, **kwargs))
            if self._skip:
                ret += ' OFFSET {} '.format(_sqlexp(self._skip, **kwargs))
        return ret

    def __str__(self):
        return self.sqlexpression()


class SQLSelectText(SQLSelect):
    def __init__(self, sqltext, alias=None):
        self._sqltext = sqltext
        self._alias = alias or 'subq'
        super(SQLSelectText, self).__init__()

    def _enforce_build_order(self, build_order, coalesce=False):
        # irrespective of build_order, turn sqltext into inner sub query
        sq = SQLSelectSubQuery(child=self, alias=self._alias)
        return SQLSelect(params=self.P).add_from(sq)

    def sqlexpression(self, **kwargs):
        return _sqlexp(Symbol(self._sqltext))


class SQLSelectSubQuery(SQLSelect):
    def __init__(self, child, alias=None):
        self._child = child
        self._alias = alias
        super(SQLSelectSubQuery, self).__init__(params=child.P)

    def sqlexpression(self, **kwargs):
        open_paren = '\n' + ' ' * ((kwargs.get('level', 0) * 7) - 1) + '('
        t = [Symbol(open_paren), self._child, Symbol(')')]
        if self._alias:
            t += [Symbol(' as '), self._alias]
        return _sqlexp(t, delim='', **kwargs)


def _QueryString(qs, alias):
    # detect if input string is collection-name or SQL
    if len(qs.strip().split()) == 1:
        # case 2: exactly one token means it is a resource name
        return QueryStringResource(qs.strip(), alias=alias)
    else:
        # case 3: not s-expr, not resource name -> assume SQL
        return QueryStringSQLText(qs, alias=alias)


class QueryStringResource(Query):
    def __init__(self, qs, alias=None):
        self._resource = qs
        super(QueryStringResource, self).__init__(source=qs, alias=alias)

    def sqlbuild(self, sqlsel):
        return sqlsel.add_from(self)

    def sqlexpression(self, **kwargs):
        t = [self._resource]
        if self.get_alias():
            t += [Symbol('as'), self.get_alias()]
        return _sqlexp(t, **kwargs)


class QueryStringSQLText(Query):
    def __init__(self, qs, alias=None):
        self._sqlexpr = qs
        super(QueryStringSQLText, self).__init__(alias=alias)

    def sqlbuild(self, sqlsel):
        return SQLSelectText(self._sqlexpr, alias=self.get_alias())


class SubQuery(Query):
    def __init__(self, child, alias=None):
        if not isinstance(child, Query):
            raise TypeError('invalid query type ' + type(child))
        super(SubQuery, self).__init__(child=child, alias=alias)
        self.child = child

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.child)

    def sqlbuild(self, sqlsel):
        return sqlsel.add_from(self)

    def sqlexpression(self, **kwargs):
        childsq = self.child.sqlbuild(SQLSelect(params=self.P))
        sq = SQLSelectSubQuery(child=childsq, alias=self.get_alias())
        return sq.sqlexpression(**kwargs)


class MultiTermQuery(Query):
    def __init__(self, children=[], **kwargs):
        super(MultiTermQuery, self).__init__(children=children, **kwargs)
        self.children = children

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, *self.children)


class AndQuery(MultiTermQuery):
    def __and__(self, other):
        if isinstance(other, AndQuery):
            children = self.children + other.children
            if len(children) == 1:
                return children.pop()
            return AndQuery(children)
        if not isinstance(other, Query):
            return NotImplemented
        if len(self.children) == 0:
            return other
        return AndQuery(self.children + [other])

    def sqlexpression(self, **kwargs):
        return _sqlexp(self.children, delim=' AND ', **kwargs)


class OrQuery(MultiTermQuery):
    def __or__(self, other):
        if isinstance(other, OrQuery):
            children = self.children + other.children
            if len(children) == 1:
                return children.pop()
            return OrQuery(children)
        if not isinstance(other, Query):
            return NotImplemented
        if len(self.children) == 0:
            return other
        return OrQuery(self.children + [other])

    def sqlexpression(self, **kwargs):
        return _sqlexp(self.children, delim=' OR ', **kwargs)


class NotQuery(Query):
    def __init__(self, negated):
        super(NotQuery, self).__init__(child=negated)
        self.negated = negated

    def __invert__(self):
        return self.negated

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.negated)

    def sqlexpression(self, **kwargs):
        return _sqlexp(
            [Symbol('NOT'),
             Symbol('('), self.negated,
             Symbol(')')], **kwargs
        )


class DifferenceQuery(Query):
    def __init__(self, base, diminisher):
        super(DifferenceQuery, self).__init__(child=base)
        self.base = base
        self.diminisher = diminisher


def checked_decode(x, ty=None):
    x = decode(x)
    if ty:
        assert isinstance(x, ty)
    return x


class FieldOpQuery(Query):
    def __init__(self, field, v, op, sqlop=None):
        super(FieldOpQuery, self).__init__()
        self.field = _fref(field)
        self.value = v
        if isinstance(v, (BaseRef, Query)):
            self.value_p = v
        else:
            self.value_p = Literal(v)
        self.op = op
        self.sqlop = sqlop
        self.nested_field_expr = self._init_nested_field_op_query()

    def _init_nested_field_op_query(self):
        if not self.field._is_array_field():
            return None
        # turn F['foo'][:]['bar'][:]['baz'] == 10
        # into F['foo'].nested(F['bar'].nested(F['baz'] == 10))
        fparts = self._split_array_path(self.field)
        fop_q = FieldOpQuery(fparts.pop(), self.value_p, self.op, self.sqlop)
        for fpart in reversed(fparts):
            fop_q = fpart.nested(fop_q)
        return fop_q

    def _split_array_path(self, field):
        parts = []
        tp = FieldRef()
        for fp in field._path():
            if isinstance(fp, slice):
                parts.append(tp)
                tp = FieldRef()
                continue
            tp = tp[fp]
        parts.append(tp)
        return parts

    def sqlprepare(self, sqlsel):
        sqlsel = _sqlprep(sqlsel, self.field, self.value)
        """
        FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME

        Disabling auto-params feature for now.
        Remove this once issue #1506 is fixed.

        FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME

        if not isinstance(self.value, (BaseRef, Query)):
            # replace value with param ref, stash the value in sqlsel
            pname = sqlsel.P.new_param(self.field)
            sqlsel.P[pname] = self.value
            self.value_p = ParamRef(pname)
        """
        return sqlsel

    def sqlexpression(self, **kwargs):
        if self.nested_field_expr:
            return _sqlexp(self.nested_field_expr, **kwargs)
        return _sqlexp([self.field, Symbol(self.sqlop), self.value_p], **kwargs)


class FieldEqQuery(FieldOpQuery):
    def __init__(self, field, v):
        super(FieldEqQuery, self).__init__(field=field, v=v, op='eq', sqlop='=')


def _make_ne(field, v):
    return NotQuery(FieldEqQuery(field, v))


class FieldIntOpQuery(FieldOpQuery):
    def __init__(self, field, v, op, sqlop):
        super().__init__(field, checked_decode(v, int), op, sqlop)


class FieldFloatOpQuery(FieldOpQuery):
    def __init__(self, field, v, op, sqlop):
        super().__init__(field, checked_decode(v, float), op, sqlop)


class FieldStringOpQuery(FieldOpQuery):
    def __init__(self, field, v, op, sqlop):
        super().__init__(field, checked_decode(v, str), op, sqlop)


class FieldBaseRefOpQuery(FieldOpQuery):
    def __init__(self, field, v, op, sqlop):
        super().__init__(field, checked_decode(v, BaseRef), op, sqlop)


def convert_re(s):
    if hasattr(s, 'flags') and hasattr(s, 'pattern'):
        if s.flags != 0:
            raise ValueError('RegexObjects with flags not supported')
        return s.pattern
    return checked_decode(s, str)


class FieldTermMatchesQuery(FieldOpQuery):
    def __init__(self, field, v):
        super().__init__(field, convert_re(v), 'term_matches')

    def sqlexpression(self, **kwargs):
        raise NotImplementedError(
            'term_regex operator in SQL mode is '
            'not yet implemented!'
        )


class FieldTermPrefixQuery(FieldOpQuery):
    def __init__(self, field, v):
        super().__init__(field, checked_decode(v, str), 'term_prefix')

    def sqlexpression(self, **kwargs):
        raise NotImplementedError(
            'term_prefix operator in SQL mode is '
            'not yet implemented!'
        )


class FieldMatchesQuery(FieldOpQuery):
    def __init__(self, field, v):
        super().__init__(field, convert_re(v), 'regex')

    def sqlexpression(self, **kwargs):
        raise NotImplementedError(
            'regex operator in SQL mode is '
            'not yet implemented!'
        )


class FieldLikeQuery(FieldOpQuery):
    def __init__(self, field, v):
        # v could be str or Literal
        v = decode(v)
        super().__init__(field, v, None, 'LIKE')


class FieldPrefixQuery(FieldOpQuery):
    def __init__(self, field, v):
        # v could be str or Literal
        v = decode(v)
        super().__init__(field, v, 'prefix', None)

        # need to escape '%_' since sql query is re-written with LIKE
        if isinstance(v, str):
            v = _escape_chars(v, '%_')
            v = v + '%'
        elif isinstance(v, Literal):
            v = Literal(_escape_chars(v.value, '%_'))
            v = Literal(v.value + '%')
        self.sql_fop = FieldOpQuery(field, v, None, 'LIKE')

    def sqlprepare(self, sqlsel):
        return self.sql_fop.sqlprepare(sqlsel)

    def sqlexpression(self, **kwargs):
        return self.sql_fop.sqlexpression(**kwargs)


class UnaryOpQuery(Query):
    def __init__(self, field, op, pre_sqlop=None, post_sqlop=None):
        super(UnaryOpQuery, self).__init__()
        self.field = _fref(field)
        self.op = op
        self.pre_sqlop = pre_sqlop
        self.post_sqlop = post_sqlop

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.field)

    def sqlexpression(self, **kwargs):
        exp = []
        self.pre_sqlop and exp.append(Symbol(self.pre_sqlop))
        exp.append(self.field)
        self.post_sqlop and exp.append(Symbol(self.post_sqlop))
        return _sqlexp(exp, **kwargs)


class FieldIsDefinedQuery(UnaryOpQuery):
    def __init__(self, field):
        super(FieldIsDefinedQuery, self).__init__(
            field, 'is_defined', post_sqlop='IS NOT NULL'
        )


class FieldIsNullQuery(UnaryOpQuery):
    def __init__(self, field):
        super(FieldIsNullQuery, self).__init__(
            field, 'not-implemented', post_sqlop='IS NULL'
        )


class FieldExistsQuery(UnaryOpQuery):
    def __init__(self, field):
        super(FieldExistsQuery, self).__init__(
            field, 'not-implemented', pre_sqlop='EXISTS'
        )
        self.field = field


class FieldIsNotNullQuery(UnaryOpQuery):
    def __init__(self, field):
        super(FieldIsNotNullQuery, self).__init__(field, 'is_not_null')

    def sqlexpression(self, **kwargs):
        return _sqlexp(
            FieldIsDefinedQuery(self.field) & FieldOpQuery(
                self.field, Symbol('NULL_VALUE'), 'ne', 'IS DISTINCT FROM'
            ), **kwargs
        )


class ApplyQuery(Query):
    def __init__(self, to_field, child, target_query=None):
        if target_query:
            if not child.get_source():
                raise ValueError(
                    'cannot specify target_query for apply '
                    'when inner query is not bound to a collection'
                )
        super(ApplyQuery, self).__init__(child=(target_query or child))
        self.to_field = _fref(to_field)
        self.child = SubQuery(child)
        self.target_query = target_query or Q(child.get_source())
        self.in_q = FieldOpQuery(self.to_field, self.child, 'apply', 'IN')

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.in_q, self.target_query)

    def sqlbuild(self, sqlsel):
        sqlsel.add_from(self.target_query)
        sqlsel.add_where(self.in_q)
        return sqlsel


class NestedQuery(Query):
    def __init__(self, base_field, inner_query):
        super(NestedQuery, self).__init__(child=inner_query)
        self.base_field = _fref(base_field)
        self.inner_query = inner_query
        uq = Symbol('UNNEST({})'.format(self.base_field))
        self.unnest_query = FieldExistsQuery(
            SubQuery(Q(uq, alias='uq').where(inner_query).select(Literal(1)))
        )

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.base_field, self.unnest_query)

    def sqlexpression(self, **kwargs):
        return _sqlexp(self.unnest_query)


class ProximityQuery(Query):
    def __init__(self, field, search_query, analyzer):
        super(ProximityQuery, self).__init__()
        self.search_field = field
        self.search_query = search_query
        self.analyzer = analyzer


class LookupQuery(Query):
    def __init__(
        self, local_field, target_field, target_query, new_field, child
    ):
        super(LookupQuery, self).__init__(child=child)
        #
        # initialize all fields with appropriate defaults when not specified
        self.local_field = _fref(local_field)
        if target_field is None:
            self.target_field = F['_id']
        else:
            self.target_field = _fref(target_field)
        if new_field is None:
            self.new_field = copy.copy(self.local_field)
            self.new_field._concat(':lookup')
        else:
            self.new_field = _fref(new_field)
        if target_query is None:
            self.target_query = AllQuery(child=child).select(self.target_field)
        else:
            self.target_query = target_query
        self.child = child
        #
        # rewrite SQL components with a nested subquery with group-by
        target_q_alias = (
            self.target_query.get_alias() or self.target_query.get_source()
        )
        if not target_q_alias:
            raise ValueError(
                'Cannot use lookup operator with a target query '
                'that is not bound to a particular collection.'
            )
        sub_q_alias = target_q_alias + '_lookup'
        self.sub_q = SubQuery(
            SubQuery(self.target_query).aggregate(
                self.target_field,
                self.target_query.F.collect().named(self.new_field)
            ),
            alias=sub_q_alias
        )
        self.eq_q = FieldEqQuery(
            self.child.F[self.local_field], self.sub_q.F[self.target_field]
        )

    def sqlprepare(self, sqlsel):
        return _sqlprep(
            sqlsel, self.sub_q, self.eq_q, self.new_field, self.child
        )

    def sqlbuild(self, sqlsel):
        sqlsel = self.child.sqlbuild(sqlsel)
        sqlsel = sqlsel.add_left_outer_join(self.sub_q, self.eq_q)
        sqlsel = sqlsel.add_select(self.child.F, self.sub_q.F[self.new_field])
        return sqlsel


class AllQuery(AndQuery):
    def __init__(self, child=None):
        super(AllQuery, self).__init__(child=child)
        self.child = child

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.child)

    def sqlbuild(self, sqlsel):
        return self.child.sqlbuild(sqlsel)


class NoneQuery(OrQuery):
    def __init__(self):
        super(NoneQuery, self).__init__()


class AggregateQuery(Query):
    def __init__(self, fields, child):
        super(AggregateQuery, self).__init__(child=child)
        self.dimension_fields = []
        self.aggregate_fields = []
        for f in fields:
            fr = _fref(f)
            if isinstance(fr, AggFieldRef):
                self.aggregate_fields += [fr]
            else:
                self.dimension_fields += [fr]
        self.child = child

    def sqlprepare(self, sqlsel):
        all_fields = self.dimension_fields + self.aggregate_fields
        return _sqlprep(sqlsel, self.child, *all_fields)

    def sqlbuild(self, sqlsel):
        all_fields = self.dimension_fields + self.aggregate_fields
        sqlsel = self.child.sqlbuild(sqlsel)
        sqlsel = sqlsel.add_select(*all_fields)
        sqlsel = sqlsel.add_groupby(*self.dimension_fields)
        return sqlsel


class SortQuery(Query):
    def __init__(self, mode, fields, child):
        super(SortQuery, self).__init__(child=child)
        self.mode = mode
        self.fields = [_fref(f) for f in fields]
        self.child = child

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.child, *self.fields)

    def sqlbuild(self, sqlsel):
        sqlsel = self.child.sqlbuild(sqlsel)
        return sqlsel.add_orderby(self.mode, *self.fields)


class LimitQuery(Query):
    def __init__(self, limit, skip, child):
        super(LimitQuery, self).__init__(child=child)
        self.max_results = limit
        self.skip_results = skip
        self.child = child

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.child, self.max_results, self.skip_results)

    def sqlbuild(self, sqlsel):
        sqlsel = self.child.sqlbuild(sqlsel)
        return sqlsel.add_limit(limit=self.max_results, skip=self.skip_results)


class SampleQuery(Query):
    def __init__(self, ratio, child):
        super(SampleQuery, self).__init__(child=child)
        if type(ratio) == int:
            ratio = float(ratio)
        if type(ratio) != float or ratio < 0.0 or ratio > 1.0:
            raise ValueError(
                'SampleQuery specified with an invalid ratio. '
                '{} is not between 0.0 and 1.0'.format(ratio)
            )
        self.ratio = ratio
        self.child = child


class BoostedQuery(Query):
    def __init__(self, factor, child):
        super(BoostedQuery, self).__init__(child=child)
        if type(factor) == int:
            factor = float(factor)
        if type(factor) != float or factor <= 0.0:
            raise ValueError(
                'BoostedQuery specified with an invalid boost. '
                '{} is not a positive float'.format(factor)
            )
        self.factor = factor
        self.child = child


class SearchQuery(Query):
    def __init__(self, conditions, child):
        super(SearchQuery, self).__init__(child=child)
        self.conditions = [c for c in conditions]
        self.child = child


class ScoreQuery(Query):
    def __init__(self, name, code, context, child):
        super(ScoreQuery, self).__init__(child=child)
        self.name = name
        self.code = code
        self.context = context
        self.child = child


class SelectQuery(Query):
    def __init__(self, fields, child):
        super(SelectQuery, self).__init__(child=child)
        if not isinstance(child, Query):
            return NotImplemented
        self.fields = [_fref(f) for f in fields]
        self.child = child

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.child, *self.fields)

    def sqlbuild(self, sqlsel):
        sqlsel = self.child.sqlbuild(sqlsel)
        return sqlsel.add_select(*self.fields)


class WhereQuery(Query):
    def __init__(self, pred, child):
        super(WhereQuery, self).__init__(child=child)
        if not isinstance(child, Query) or not isinstance(pred, Query):
            return NotImplemented
        self.pred = pred
        self.child = child

    def sqlprepare(self, sqlsel):
        return _sqlprep(sqlsel, self.child, self.pred)

    def sqlbuild(self, sqlsel):
        sqlsel = self.child.sqlbuild(sqlsel)
        return sqlsel.add_where(self.pred)


def _fref(f):
    if isinstance(f, BaseRef):
        return f
    if type(f) is str:
        return FieldRef()[f]
    return NotImplemented


class BaseRef(object):
    def sqlexpression(self, **kwargs):
        raise NotImplementedError(
            'Class {} does not implement sqlexpression()'.format(type(self))
        )


class Symbol(BaseRef):
    def __init__(self, v):
        self.value = v

    def __str__(self):
        return str(self.value)

    def sqlexpression(self, **kwargs):
        return self.value


class Literal(BaseRef):
    def __init__(self, v):
        self.value = v

    def sqlexpression(self, **kwargs):
        if isinstance(self.value, str):
            return "'{}'".format(_escape_chars(self.value, "'"))
        return str(self.value)


class FieldPathPartRef(BaseRef):
    def __init__(self, fp, level=0):
        self.fp = fp
        self.level = level

    def sqlexpression(self, **kwargs):
        if self.level == 0:
            ret = [self.fp]
        elif isinstance(self.fp, slice):
            ret = [Symbol('[*]')]
        elif isinstance(self.fp, int):
            ret = [Symbol('[{}]'.format(self.fp))]
        else:
            ret = [Symbol('.'), self.fp]
        return _sqlexp(ret, delim='', **kwargs)


class FieldRef(BaseRef):
    def __init__(self, name=None, parent=None, source=None):
        if isinstance(name, slice):
            if not (
                name.start is None and name.stop is None and name.step is None
            ):
                raise ValueError('Only empty slices (":") are supported')
        elif isinstance(name, str):
            if name == '*':
                name = slice(None)
        elif isinstance(name, int):
            pass
        elif name is None:
            assert parent is None
            pass
        else:
            raise TypeError('Invalid FieldRef type ' + type(name))

        # if parent is None it means that name also needs to be None
        assert parent is not None or name is None

        self._name = name
        self._parent = parent
        self._source = source

    def __getitem__(self, name):
        if isinstance(name, FieldRef):
            this = self
            for fp in name._path():
                this = FieldRef(fp, this)
        else:
            this = FieldRef(name, self)
        return this

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError('Field reference has no attribute {}', name)
        return FieldRef(name, self)

    def __iter__(self):
        for part in self._path():
            if isinstance(part, slice):
                yield '*'
                continue
            yield part

    def _concat(self, suffix):
        self._name += suffix

    def _path(self):
        r = self
        p = []
        while r._parent is not None:
            p.append(r._name)
            r = r._parent
        p.reverse()
        return p

    def _is_simple_field_lookup(self):
        return isinstance(self._name, str) and len(self._path()) == 1

    def _is_root_field(self):
        if self._name is None and self._parent is None:
            return True
        if isinstance(self._name, slice) and self._parent is not None:
            return self._parent._is_root_field()

    def _is_array_field(self):
        return '*' in list(self)

    def _get_source(self):
        if self._parent:
            return self._parent._get_source()
        return self._source

    def min(self):
        """ Returns a new FieldRef that represents a min() aggregation
        of the given field.

        Returns:
           AggFieldRef: FieldRef object that represents the desired ``min``
           aggregation.
        """
        return AggFieldRef("min", self)

    def max(self):
        """ Returns a new FieldRef that represents a max() aggregation
        of the given field.

        Returns:
           AggFieldRef: FieldRef object that represents the desired ``max``
           aggregation.
        """
        return AggFieldRef("max", self)

    def avg(self):
        """ Returns a new FieldRef that represents an avg() aggregation
        of the given field.

        Returns:
           AggFieldRef: FieldRef object that represents the desired ``avg``
           aggregation.
        """
        return AggFieldRef("avg", self)

    def sum(self):
        """ Returns a new FieldRef that represents a sum() aggregation
        of the given field.

        Returns:
           AggFieldRef: FieldRef object that represents the desired ``sum``
           aggregation.
        """
        return AggFieldRef("sum", self)

    def count(self):
        """ Returns a new FieldRef that represents a count() aggregation
        of the given field.

        Returns:
          AggFieldRef: FieldRef object that represents the desired ``count``
          aggregation.
        """
        return AggFieldRef(
            "count", self, allow_root=True, root_field=FieldRef()
        )

    def approximatecountdistinct(self):
        """ Returns a new FieldRef that represents a approximatecountdistinct()
        aggregation of the given field.

        Returns:
          AggFieldRef: FieldRef object that represents the desired
          ``approximatecountdistinct`` aggregation.
        """
        return AggFieldRef("approximatecountdistinct", self)

    def countdistinct(self):
        """ Returns a new FieldRef that represents a countdistinct()
        aggregation of the given field.

        Returns:
          AggFieldRef: FieldRef object that represents the desired
          ``countdistinct`` aggregation.
        """
        return AggFieldRef("countdistinct", self)

    def collect(self):
        """ Returns a new FieldRef that represents a collect()
        aggregation of the given field.

        Returns:
          AggFieldRef: FieldRef object that represents the desired
          ``collect`` aggregation.
        """
        return AggFieldRef(
            "collect", self, allow_root=True, root_field=FieldRef()[:]
        )

    def apply(self, inner_query):
        """ Returns a new query object that matches all documents where
        the given field matches the results of the inner_query

        E.g: say the inner query returns N documents {r1, r2, ... rN},
        and each of those contain a single field 'f', then the following
        two expressions are equivalent to one another, but the **apply()**
        version is faster, more efficient and requires only one round-trip::

          <field_ref>.apply(inner_query)

          (<field_ref> == r1['f']) | (<field_ref> == r2['f']) \
... | (<field_ref> == rN['f'])

        Args:
            inner_query (Query): query object on whose results you wish \
            to perform the apply operation on.

        Returns:
            Query: query object that represents the desired apply operation
        """
        return ApplyQuery(self, inner_query)

    def nested(self, nested_query):
        """ Returns a new query object that matches all documents
        where the given inner query matches on one or more individual
        nested documents present within the field path of the given field.

        Useful to run complex query expressions on fields that contain
        an nested array of documents.

        Example:
          Say you have a collection where every document describes a book,
          and each document has an "authors" field that is a nested array of
          documents describing each author::

            {"title": "Transaction Processing: Concepts and Techniques",
             "authors": [
                 {"first_name": "Jim", "last_name": "Gray"},
                 {"first_name": "Andreas", "last_name": "Reuter"},
             ],
             "publisher": ... }

        If you want to do find all books where 'Jim Gray' was one of the
        authors, you can use the following query::

            F["authors"].nested((F["first_name"] == 'Jim') \
& (F["last_name"] == 'Gray'))

        Note: Constructing the same query as follows is incorrect::

            # CAUTION: This is not same as the query above
            (F["authors"][:]["first_name"] == 'Jim') \
& (F["authors"][:]["last_name"] == 'Gray')

        The incorrect version will return all books which has at least one
        author with first name 'Jim' and at least one author with last name
        'Gray', but it need not be the same author. A book with two authors
        named 'Jim Smith' and 'Alice Gray' will also match, which is not what
        is intended.

        Args:
            nested_query (Query): query expression to run on every nested \
            document present within the given field path

        Returns:
            Query: query object that represents desired nested operations
        """
        return NestedQuery(self, nested_query)

    def proximity(self, search_query, analyzer="default"):
        """ Returns a new query object that when executed will perform a
        proximity query with the given input search query, tokenized with the
        specified analyzer on the given field.

        Eg: Split the search query "jim phone number" on whitespace and search
        across all documents on the "email_body" field, while ranking documents
        where the search terms appear closer together higher::

            F["email_body"].proximity("jim phone number", \
analyzer="default")

        Proxmity queries matches the query string against the text and adds
        a boost if terms are close together, i.e. "jim phone number" query will
        score "Jim's phone number" higher than "Jim bought a new phone".
        Proximity queries also does spell checking with an English dictionary.

        Args:
            search_query (str): Text search string
            analyzer (str): Name of the analyzer to use on the search_query
                before performing the search. Defaults to "default".

        Returns:
            Query: query object that represents the proximity query
        """
        return ProximityQuery(self, search_query, analyzer)

    def sqlexpression(self, **kwargs):
        # for root_fields just use '*'
        # eg: SELECT count(*) FROM employees;
        terms = []
        if self._get_source():
            terms += [self._get_source(), Symbol('.')]
        if self._is_root_field():
            terms += [Symbol('*')]
        else:
            terms += [
                FieldPathPartRef(p, i) for i, p in enumerate(self._path())
            ]
        return _sqlexp(terms, delim='', **kwargs)

    def __str__(self):
        try:
            return self.sqlexpression()
        except NotImplementedError:
            return repr(self)


class AggFieldRef(BaseRef):
    def __init__(self, agg_op, field, allow_root=False, root_field=None):
        self._field = field
        self._aggregate_op = agg_op
        if not allow_root and self._field._is_root_field():
            raise ValueError(
                'Aggregation function {} is not allowed on '
                'the root field reference'.format(agg_op)
            )
        if allow_root and field._is_root_field() and root_field is not None:
            self._field = root_field
            self._alias = self._aggregate_op
        elif self._field._is_root_field():
            self._alias = self._aggregate_op
        elif self._field._is_simple_field_lookup():
            self._alias = '{}_{}'.format(self._aggregate_op, self._field._name)
        else:
            self._alias = None

    def __str__(self):
        try:
            return self.sqlexpression()
        except NotImplementedError:
            return repr(self)

    def _check_valid_alias(self):
        if self._alias is None:
            raise ValueError(
                'Complex field paths require explicit aliases: ' +
                self._field.sqlexpression()
            )

    def named(self, alias):
        self._alias = alias
        return self

    def sqlexpression(self, **kwargs):
        return _sqlexp(
            [
                Symbol(self._aggregate_op),
                Symbol('('), self._field,
                Symbol(')'),
                Symbol(' as '), self._alias
            ],
            delim='',
            **kwargs
        )


def _gen_param_name(field):
    if isinstance(field, FieldRef):
        fpath = list(field)
        fpath.reverse()
    elif isinstance(field, str):
        fpath = [field]
    else:
        raise TypeError('invalid field type "{}"'.format(type(field)))
    fname = None
    for fname in fpath:
        if (isinstance(fname, int) or (fname == '*') or (fname == '')):
            continue
        # found a good fname in fpath to seed new param; bail
        break

    # a is for apple, p is for param
    fname = fname or 'p'
    # replace all non alphanumeric with '_'
    fname = [c.isalnum() and c or '_' for c in fname]
    # strip all consecutive '_' with a single '_'
    fname = [
        c for i, c in enumerate(fname)
        if ((i == 0) or (c != '_') or (fname[i] != fname[i - 1]))
    ]
    fname = ''.join(fname)
    return fname


class ParamRef(BaseRef):
    def __init__(self, name=''):
        self._name = name
        self._pname = _gen_param_name(name)

    def _symbol(self):
        return ':' + self._pname

    def __getitem__(self, name):
        if self._name != '':
            raise ValueError('nested parameters are not supported')
        return ParamRef(name)

    def __setitem__(self, name, value):
        raise ValueError(
            'cannot assign values to ParamRef. '
            'use ParamDict instead'
        )

    def __str__(self):
        return self._symbol()

    def sqlexpression(self, **kwargs):
        return _sqlexp(Symbol(self._symbol()), **kwargs)


class ParamDict(dict):
    def __setitem__(self, name, value):
        k = _gen_param_name(name)
        v = value
        _ = self._type_map(value)  # ensure value type is supported
        super(ParamDict, self).__setitem__(k, v)

    def _type_map(self, v):
        # map Python types to Rockset type
        if isinstance(v, bool):
            return 'bool'
        elif isinstance(v, int):
            return 'int'
        elif isinstance(v, float):
            return 'float'
        elif isinstance(v, str):
            return 'string'
        raise TypeError(
            'parameter value of type {} is not supported'.format(type(v))
        )

    def new_param(self, field):
        fname = _gen_param_name(field)
        for i in range(1, 1001):
            candidate = fname
            if i > 1:
                candidate += str(i)
            if candidate not in self:
                return candidate
        raise ValueError(
            'too many parameters bound with name "{}"'.format(fname)
        )

    def sqlparams(self):
        params = []
        for k in sorted(self):
            params.append(
                {
                    'name': k,
                    'value': str(self[k]),
                    'type': self._type_map(self[k])
                }
            )
        return params


_arg_ops = [
    ('__eq__', {}, FieldEqQuery),
    ('__ne__', {}, _make_ne),
    ('term_matches', {
        str: FieldTermMatchesQuery
    }, None),
    ('term_startswith', {
        str: FieldTermPrefixQuery
    }, None),
    ('matches', {
        str: FieldMatchesQuery
    }, None),
    ('startswith', {
        str: FieldPrefixQuery,
        Literal: FieldPrefixQuery
    }, None),
    ('like', {
        str: FieldLikeQuery,
        Literal: FieldLikeQuery
    }, None),
]

for op in (('lt', '<'), ('le', '<='), ('gt', '>'), ('ge', '>=')):

    def f_int(field, v, op=op[0], sqlop=op[1]):
        return FieldIntOpQuery(field, v, op, sqlop)

    def f_float(field, v, op=op[0], sqlop=op[1]):
        return FieldFloatOpQuery(field, v, op, sqlop)

    def f_string(field, v, op=op[0], sqlop=op[1]):
        return FieldStringOpQuery(field, v, op, sqlop)

    def f_baseref(field, v, op=op[0], sqlop=op[1]):
        return FieldBaseRefOpQuery(field, v, op, sqlop)

    type_map = {
        int: f_int,
        float: f_float,
        str: f_string,
        FieldRef: f_baseref,
        ParamRef: f_baseref
    }
    _arg_ops.append(('__{}__'.format(op[0]), type_map, None))

_no_arg_ops = [
    ('is_defined', FieldIsDefinedQuery),
    ('is_not_null', FieldIsNotNullQuery),
]


def _agg_ni(self, x, op=op):
    raise TypeError(
        'Operator {} is not supported for aggregated '
        'field references'.format(op)
    )


for op, type_map, default_ctor in _arg_ops:

    def f(self, x, op=op, type_map=type_map, default_ctor=default_ctor):
        ty = py_type(x)
        ctor = type_map.get(ty, default_ctor)
        if ctor is None:
            raise TypeError(
                'Invalid FieldRef op / type combination: {}, {}'.format(op, ty)
            )
        return ctor(self, x)

    setattr(FieldRef, op, f)
    setattr(AggFieldRef, op, _agg_ni)

for op, ctor in _no_arg_ops:

    def f(self, ctor=ctor):
        return ctor(self)

    setattr(FieldRef, op, f)
    setattr(AggFieldRef, op, _agg_ni)

F = FieldRef()
F.__doc__ = """``F`` is a field reference object that helps in building
query expressions natively using Python language expressions.
``F`` uses Python operator overloading heavily and operations on field
references generate Query_ objects that can be used in conjunction with
``Q`` to build compose complex queries."""

P = ParamRef()
P.__doc__ = """``P`` is a query parameter reference object used to define
query parameters within query expressions."""


def Q(query, alias=None):
    """All query objects are constructed using the ``Q(<collection-name>)``
    query builder construct and are then followed by a chain of query
    operators to build the full query expression."""
    if isinstance(query, Query):
        return SubQuery(query, alias=alias)
    elif type(query) == str:
        return _QueryString(query, alias=alias)
    elif isinstance(query, Symbol):
        return QueryStringResource(query, alias=alias)
    return NotImplemented


Q.all = AllQuery()
Q.none = NoneQuery()
