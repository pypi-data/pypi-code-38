"""
Define type hint aliases for Neo4J types.

 Several caveats:

  -  The spatial `Point` type and various `neotime` temporal types are not supported yet.

     (Adding these types to the unions below causes the type checker to skip validation.)

  -  The `bytes` and `bytearray` types are deliberately omitted.

     (These are not a first-class Neo4J type, although pass-through support exists.)

  -  The `None` value is omitted.

     (Explicit storage of `None` is discouraged by Neo4J.)

 See: https://neo4j.com/docs/cypher-manual/current/syntax/values/
 See: https://neo4j.com/docs/cypher-manual/current/syntax/working-with-null/

"""
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from typing import List, Union


PrimitiveType = Union[
    # basic types
    bool,
    float,
    int,
    str,
    # temporal types
    date,
    datetime,
    time,
    timedelta,
]


ListType = Union[
    # basic types
    List[bool],
    List[float],
    List[int],
    List[str],
    # temporal types
    List[date],
    List[datetime],
    List[time],
    List[timedelta],
]


PropertyType = Union[PrimitiveType, ListType]
