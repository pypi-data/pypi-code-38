from nlp_model_gen.base import CURRENT_BASE_PATH

def load_test_files():
    files = list([])
    files.append(open(CURRENT_BASE_PATH + '/config/resources/test_file_a.txt', 'r'))
    files.append(open(CURRENT_BASE_PATH + '/config/resources/test_file_b.txt', 'r'))
    files.append(open(CURRENT_BASE_PATH + '/config/resources/test_file_c.txt', 'r'))
    return files
