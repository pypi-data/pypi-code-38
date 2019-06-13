import math
import geopy.distance


class CategorySimilarityNaive(object):
    """ Similarity measure for categorical attributes defined manually
    """
    def compute_similarity(self, col, val1, val2, aggr_col):
        # print(col, val1, val2)
        if col not in self.cate_cols:
            return 0
        if col in self.vector_dict:
            if val1 not in self.vector_dict[col] or val2 not in self.vector_dict[col]:
                return 0
            if col == 'community_area':
                dist_km = geopy.distance.vincenty(self.vector_dict[col][val1], self.vector_dict[col][val2]).km
                # print(val1, val2, 1.0 /
                    # math.exp(math.pow(dist_km,0.75)))
                sim = 7.0 / math.exp(math.pow(dist_km,0.75))
                if sim > 1:
                    sim = 1.0
                return sim
            dist = math.sqrt(sum(map(
                lambda x:(x[0]-x[1])*(x[0]-x[1]),
                zip(self.vector_dict[col][val1], self.vector_dict[col][val2]
            ))))
            return 1.0 / (1.0+dist)

        if val1 == val2:
            return 1.0
        else:
            return 0.0

    def __init__(self, cur, table_name, embedding_table_list=[]):
        type_query = '''SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{}';'''.format(table_name)
        cur.execute(type_query)
        res = cur.fetchall()
        print('Similarity Naive: ', res)
        self.cate_cols = {}
        self.vector_dict = {}
        for (col, dt) in res:
            if (dt == 'boolean' or dt.find('character') != -1) and (col != 'year' or len(embedding_table_list) == 0):
                self.cate_cols[col] = True

        if table_name.startswith('synthetic'):
            self.cate_cols['beat']  = True
            self.cate_cols['primary_type']  = True
            self.cate_cols['community_area']  = True
            self.cate_cols['district']  = True
            self.cate_cols['description']  = True
            self.cate_cols['location_description']  = True
            self.cate_cols['ward']  = True

        for (col, embedding_table_name) in embedding_table_list:
            self.vector_dict[col] = {}
            read_query = '''SELECT *  FROM {} ;'''.format(embedding_table_name)
            cur.execute(read_query)
            res = cur.fetchall()
            for (x, lat, log) in res:
                self.vector_dict[col][x] = (lat, log)        

    def is_categorical(self, col):
        return col in self.cate_cols