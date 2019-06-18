import unittest
import radar

class testradar(unittest.TestCase):
    
    def test_dat(self):
        
        file=radar.dat_reader("xethru_datafloat_20190614_141837.dat",180,"converted")
        self.assertEqual(file,1)
    
    def test_raw(self):
        
        file2=radar.raw_reader("xethru_datafloat_20190614_141837.dat","converted_2")
        self.assertEqual(file2,1)
        

if __name__=='__main__':
    
    unittest.main()