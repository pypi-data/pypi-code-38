import pandas as pd
import geopandas as gpd
import requests
from shapely.geometry import Point

OSM_ENDPOINT = "http://www.overpass-api.de/api/interpreter"


def _format_node(e):
    """
    Internal function to format a node element into a dictionary.
    """

    ignored_tags = [
        "source",
        "source_ref",
        "source:ref",
        "history",
        "attribution",
        "created_by",
        "tiger:tlid",
        "tiger:upload_uuid",
    ]

    node = {"id": e["id"], "lat": e["lat"], "lon": e["lon"]}

    if "tags" in e:
        for t, v in list(e["tags"].items()):
            if t not in ignored_tags:
                node[t] = v

    return node


def _query_osm(query):
    """
    Internal function to make a request to OSM and return the parsed JSON.
    
    Parameters
    ----------
    query : str
        A string in the Overpass QL format.
    
    Returns
    -------
    data : dict
    """
    req = requests.get(OSM_ENDPOINT, params={"data": query})
    req.raise_for_status()

    return req.json()


def _build_node_query(lng_min, lat_min, lng_max, lat_max, where=[]):
    """
    Internal function that build the string for a node-based OSM query.
    
    Parameters
    ----------
    lng_min, lat_min, lng_max, lat_max : float
        the bounding box to search within
    tags : dict
        dictionary of key/value pairs to select certain nodes from OSM 
    
    Returns
    -------
    str :
        the formatted query
    """
    # format the tags dictionary into [key=value]
    tags = "".join(f"[{tag}]" for tag in where)

    return (
        "[out:json];"
        "("
        "node"
        f"{tags}"
        f"({lat_min},{lng_min},{lat_max},{lng_max});"
        ");"
        "out;"
    )


def get(lng_min, lat_min, lng_max, lat_max, where=None):
    """
    Search for OSM nodes within a bounding box that match given tags.
    
    Notes
    -----
    Where clauses can be specified using tag request clauses.
    
    From the Overpass API documentation:

    ["key"]            /* filter objects tagged with this key and any value */
    [!"key"]           /* filter objects not tagged with this key and any value */
    ["key"="value"]    /* filter objects tagged with this key and this value */
    ["key"!="value"]   /* filter objects tagged with this key but not this value, or not tagged with this key */
    ["key"~"value"]    /* filter objects tagged with this key and a value matching a regular expression */
    ["key"!~"value"]   /* filter objects tagged with this key but a value not matching a regular expression */
    [~"key"~"value"]   /* filter objects tagged with a key and a value matching regular expressions */
    [~"key"~"value",i] /* filter objects tagged with a key and a case-insensitive value matching regular expressions */

    Reference
    ---------
    - Key/value node language for where clause: 
        http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
    - OSM Overpass queries: 
        http://wiki.openstreetmap.org/wiki/Map_Features

    Parameters
    ----------
    lng_min, lat_min, lng_max, lat_max : float
        the bounding box to search within
    where : str, list of str
        the where clause to select specific node types; can be either 
        a single clause, or a list of clauses

    Returns
    -------
    geopandas.GeoDataFrame : 
        a GeoDataFrame holding the requested data

    Example
    -------
    >>> import osm2gpd
    >>> philadelphia_bounds = [-75.28030675,  39.86747186, -74.95574856,  40.13793484]
    >>> subway = osm2gpd.get(*philadelphia_bounds, where="station=subway")
    >>> subway
    >>> not_subway = osm2gpd.get(*philadelphia_bounds, where=["station", "station!=subway"])
    """
    # check param types
    if where is None:
        where = []
    if isinstance(where, str):
        where = [where]

    # run the query
    node_data = _query_osm(
        _build_node_query(lng_min, lat_min, lng_max, lat_max, where=where)
    )

    # no data
    if len(node_data["elements"]) == 0:
        raise RuntimeError("OSM query results contain no data.")

    # format the data
    nodes = [_format_node(n) for n in node_data["elements"]]

    # return a GeoDataFrame
    return gpd.GeoDataFrame(
        pd.DataFrame.from_records(nodes, index="id").assign(
            geometry=lambda df: df.apply(
                lambda row: Point(row["lon"], row["lat"]), axis=1
            )
        ),
        geometry="geometry",
        crs={"init": "epsg:4326"},
    )

