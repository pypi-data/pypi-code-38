from excel_helper.helper import ParameterLoader

__author__ = 'schien'

import numpy as np

if __name__ == '__main__':
    # init random generator
    # http://www.kevinsheppard.com/images/0/09/Python_introduction.pdf p. 225
    np.random.seed(123)

    data = ParameterLoader.from_excel('test.xlsx', size=2, sheet_index=0)
    res = data['c']
    print(res)
