import unittest
import os
from KaUtil.Excel import OpenExcel


class KaUtilTest(unittest.TestCase):

    def test_write_excel(self):
        data = [[1], [2], [3]]
        with OpenExcel('data.xlsx', 'w') as f:
            f.write_data(data)
        os.remove('data.xlsx')


if __name__ == '__main__':
    unittest.main()
