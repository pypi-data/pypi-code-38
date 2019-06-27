import unittest
from fdn_kg_loader.store import Store
from fdn_kg_loader.model import Brand

class TestGraknConn(unittest.TestCase):
    def setUp(self):

        print("setup")
        self.host = "127.0.0.1"
        self.keyspace = "schema_check"
    def tearDown(self):
        store = Store(host=self.host, keyspace=self.keyspace)
        store.exec('match $o isa brand, has gid "9999"; delete $o;')
        print("deleting test data")

    def test_insert(self):

        b = Brand()
        b.from_dict({
            'gid':'9999',
            'name':'Test Object'
        })
        store = Store(host=self.host,keyspace=self.keyspace)
        store.update(b,update_by=['gid'])
        store.flush()
        # store.close()

    def test_duplicate(self):
        pass
        #save save flush
        # b = Brand()
        # b.from_dict({
        #     'gid':'9999',
        #     'name':'Test Object'
        # })
        # store = Store(host="127.0.0.1",keyspace="schema_check")
        # store.save(b)
        # store.save(b)
        # store.flush()

    def test_duplicate_and_reconnect(self):
        #save flush - save flush
        pass
        # b = Brand()
        # b.from_dict({
        #     'gid':'9999',
        #     'name':'Test Object'
        # })
        # store = Store(host="127.0.0.1",keyspace="schema_check")
        # store.save(b)
        # store.flush()
        # store.save(b)
        # store.flush()

    def test_different_connectoin(self):
        b = Brand()
        b.from_dict({
            'gid':'9999',
            'name':'Test Object'
        })
        store = Store(host="127.0.0.1",keyspace="schema_check")
        store2 = Store(host="127.0.0.1",keyspace="schema_check")
        store.update(b,update_by=['gid'])
        store.flush()
        store2.update(b,update_by=['gid'])
        store2.flush()

if __name__ == "__main__":
    unittest.main()