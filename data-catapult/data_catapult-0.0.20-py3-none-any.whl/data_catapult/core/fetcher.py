# import os
import requests
import pandas as pd

try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

ZIP = "zip code tabulation area"
STATE = 'state'
COUNTY = 'county'
PLACE = 'place'
TRACT = 'tract'


def json_data(base_url, query, mode='json'):
    if mode == 'json':
        try:
            r = requests.get(base_url, params=query)
            data = r.json()
            return data
        except ValueError:
            print("Catapult Fetcher: {}".format(r.text))
    else:
        raise NotImplementedError("Not ready yet!")


def acs_to_df(url):
    # census api has a limit of 50 query vars, so chunk the requests
    # and join dataframes
    # GEOID is extracted and passed on each query call to ensure that
    # the geoid is available to each chunk as an index to join on.
    # (Can't assume that each call the table will be returned in order).
    #
    # Please check logic carefully... 2011 is a weird year, and there's
    # some workarounds to it. 2011 doesn't contain a geoid column.
    chunk_size = 50
    u = urlparse(url)
    query = parse_qs(u.query)
    base_url = u._replace(query=None).geturl()
    requested_year = u[2].split('/')[2]

    # get geo level so that duplicates (it gets sent back
    # with every chunk) can be deleted
    # The split is to handle 'state:36', no other level
    # has a colon
    geo_level = query['for'][0].split(':')[0]

    # Assumes that there will always be a get field
    # with list value
    columns = query['get'][0].split(',')

    # dealing with geoid not being in 2011. This str
    # is appended to the end of each chunked request.
    # initialized as empty, turned into GEOID if not
    # year 2011
    request_geoid = ''
    if requested_year != '2011':
        # This is because in years other than 2011,
        # GEOID exists in the request but is removed
        # here to allow for calculating chunked requests
        # without repeating GEOID
        columns.remove('GEOID')
        request_geoid = ',GEOID'

    # To compensate for geo being added for each chunk:
    # for columns, calculate how many geoid need to accompany
    # e.g.
    # 48  -> 1 geoid
    # 49  -> 1 geoid (total 50, one chunk)
    # 50  -> 2 geoid (total 51, two chunks)
    # 98  -> 2 geoid (total 100, two chunks)
    # 99  -> 3 geoid (total 102, three chunks)
    # 100 -> 3 geoid (total 103, three chunks)
    # then recalculate chunk size on new total.
    geoid_needed = ((len(columns) - 1) // (chunk_size - 1)) + 1
    chunk_num = ((len(columns) + geoid_needed) // chunk_size) + 1

    dfs = []
    for i in range(0, chunk_num):
        if i == chunk_num - 1:
            # last chunk
            query['get'] = [','.join(columns[(chunk_size - 1) * i:]) + request_geoid]
        else:
            query['get'] = [','.join(
                columns[(chunk_size - 1) * i:
                        (chunk_size - 1) * i + (chunk_size - 1)]) + request_geoid]

        raw_data = json_data(base_url, query)
        header = raw_data[0]
        raw_data = [dict(zip(header, row)) for row in raw_data[1:]]

        df = pd.DataFrame(raw_data)

        # extra logic for 2011 API, builds the GEOID out of other components
        if requested_year == '2011':
            prefix = {
                STATE: "040",
                COUNTY: "050",
                PLACE: "160",
                TRACT: "140",
                ZIP: "860"
            }
            if geo_level == STATE:
                df['GEOID'] = prefix[geo_level] + "00US" + df[STATE]
            elif geo_level == COUNTY:
                df['GEOID'] = prefix[geo_level] + "00US" + df[STATE] + df[COUNTY]
            elif geo_level == TRACT:
                df['GEOID'] = prefix[geo_level] + "00US" + df[STATE] + df[COUNTY] + df['tract']
            elif geo_level == PLACE:
                df['GEOID'] = prefix[geo_level] + "00US" + df[STATE] + df['place']
            elif geo_level == ZIP:
                df['GEOID'] = prefix[geo_level] + "00US" + df[ZIP]

        # Now that GEOID definitely exists, set_index on GEOID
        df = df.set_index('GEOID')

        # Drop duplicate geo level columns
        if i < chunk_num - 1:
            del(df[geo_level])

        dfs.append(df)

    df = pd.concat(dfs, axis=1)
    df.reset_index(level=0, inplace=True)
    return df
