
import unittest 
from kaola.api.kaola import KaoLa

class TestBasic(unittest.TestCase):

    def test_get_taxnos(self):
        kl = KaoLa("edb6c3b9ac4847e7584c38e2b630b14f","8200ee92ec22fcae76e2f00bc5c79247188e0593",access_token="bff74ff8-bbec-4699-bc4c-529801aefcb4", sandbox=True)
        print(kl.basic.get_taxnos())

if __name__ == "__main__":
    unittest.main()