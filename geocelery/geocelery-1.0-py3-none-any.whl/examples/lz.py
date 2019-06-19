from dboxapi import *

c = DBoxQuery()

pt = {"type": "point",
      "coordinates": [
          112.03653,
          38.897676
      ]
      }

q1 = LogicalFilter(
    LeafTerms("date_year", [2002, 2003]),
    LeafTerm("level", 0),
    LeafTerms("date_month", [5, 6, 7, 8])
)

q = BooleanQuery(q1)

print("检索条件为：", str(q))

jdata, code = c.m_query(q)

if jdata is not None:
    print("\n符合条件记录数：", jdata["count"])

    _id = jdata["items"][0]["id"]

    jitem, code = c.m_info(_id)
    if jitem is not None:
        print("====")
        test_jdata = jitem