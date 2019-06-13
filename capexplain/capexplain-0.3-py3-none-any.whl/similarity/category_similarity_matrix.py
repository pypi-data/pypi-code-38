class CategorySimilarityMatrix(object):
    """ Similarity measure for categorical attributes defined manually
    """
    def compute_similarity(self, col, val1, val2, aggr_col):
        # if col == 'pubkey':
            # print('In compute_similarity:', col, val1, val2, self.sim_matrix[col][val1])
        if col not in self.sim_matrix:
            return 0
        else:
            if val1 not in self.sim_matrix[col] and val2 not in self.sim_matrix[col]:
                if val1 == val2:
                    return 1
                else:
                    return 0
            return self.sim_matrix[col][val1][val2]

    def __init__(self, inf='', schema=None):
        self.sim_matrix = {}
        if schema is not None:
            for k in schema:
                if schema[k] != 'integer' and not schema[k].startswith('double') and not schema[k].startswith('float'):
                    self.sim_matrix[k] = {}
        if inf == '':
            return
        infile = open(inf, 'r')

        col = ''
        while True:
            line = infile.readline()
            if not line:
                break
            temp_arr = line.split(',')
            if len(temp_arr) == 1:
                col = line.strip()
                self.sim_matrix[col] = {}
            else:
                sim_tuple = temp_arr
                if sim_tuple[0] not in self.sim_matrix[col]:
                    self.sim_matrix[col][sim_tuple[0]] = {sim_tuple[0]:1.0}
                if sim_tuple[1] not in self.sim_matrix[col]:
                    self.sim_matrix[col][sim_tuple[1]] = {sim_tuple[1]:1.0}
                self.sim_matrix[col][sim_tuple[0]][sim_tuple[1]] = float(sim_tuple[2])
                self.sim_matrix[col][sim_tuple[1]][sim_tuple[0]] = float(sim_tuple[2])
        print('Similarity Matrix')
        print(self.sim_matrix)


    def is_categorical(self, col):
        return col in self.sim_matrix