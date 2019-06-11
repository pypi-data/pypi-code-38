"""
This module exists solely to support the type hinting supplied by Python3.5, and by MyPy, to define custom type
aliases used in the main module.

Author: Vincent Medina, EveryMundo
Company: vincent@everymundo.com
2016-12-08
"""
from typing import Any, AnyStr, Dict, List, Mapping, NamedTuple, Optional, Sequence, SupportsFloat, SupportsInt, Union

# The header sent out with requests
Header = Dict[
    AnyStr,
    Optional[
        Union[
            AnyStr,
            SupportsFloat
        ]
    ]
]
# Any 'value' that can be passed and serialized into a .json
Entry = Optional[
    Union[
        AnyStr,
        Sequence,
        SupportsFloat,
        SupportsInt,
        int,
        float,
        str,
        Dict[AnyStr, Any]
    ]
]
# The Query document. Should be able to be used in any nested query
Query = Dict[
    AnyStr,
    Union[
        Dict[
            AnyStr,
            Union[
                Any,
                Entry
            ]
        ],
        Entry
    ]
]
# Aggregation queries
AggregationQuery = List[
    Query
]
# Payload that is sent to datacore for posting and also the data returned from gets.
Payload = Sequence[
    Mapping[
        AnyStr,
        Optional[Entry]
    ]
]
# Definition of datacore api endpoint of interest
EndpointDefinition = Dict[
    AnyStr,
    Union[
        AnyStr,
        int
    ]
]
