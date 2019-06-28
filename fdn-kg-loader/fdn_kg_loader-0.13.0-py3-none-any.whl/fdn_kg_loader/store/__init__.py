
from grakn.client import GraknClient
import copy, re
class Store:
    
    session = None
    tx = None

    def __init__(self, host='naga.fdn', port=48555, keyspace='grakn'):
        self.HOST = host
        self.PORT = port
        self.KEYSPACE = keyspace
        self._client = None
        self.bulk_query = []

        # self._client = self._make_client()
        self._session = GraknClient(uri="{}:{}".format(self.HOST, self.PORT)).session(keyspace=self.KEYSPACE)

    def _close(self):
        if self._session is not None:
            self._session.close()
            # self._client.close()
    
    def __del__(self):
        self._close()
        
    def exec(self, q):
        with self._session.transaction().write() as tx:
            #rqit is read query iterator
            rqit = tx.query(q)
            # concepts = rqit.collect_concepts()
            # id = concepts[0].id
            tx.commit()

    def query(self, q):
        
        with self._session.transaction().read() as tx:
            #rqit is read query iterator
            rqit = tx.query(q)
            rs = rqit.collect_concepts()
            for r in rs:
                yield r
                    
    
    def _make_client(self):
        return GraknClient(uri="{}:{}".format(self.HOST, self.PORT))

    def relates(self, rel, filter=None):
        def _build_query(props,relation_name):
            Left, Right = props['relates']

            query = '''
                match 
                    $l isa {}, has {} "{}";
                    $r isa {}, has {} "{}";
                insert 
                    $R({}: $l , {}:$r) isa {};
            '''.format(Left['entity'],Left['identifier'],Left['value'],
                        Right['entity'],Right['identifier'],Right['value'],
                        Left['as'],Right['as'],relation_name)
            print(query)
            return re.sub(r'\s+',' ',query)

        relation_name = getattr(rel.__class__,'relation_name')
        props = rel.__dict__
        query = _build_query(props, relation_name)
        Left, Right = props['relates']
        if filter is None:
            self.bulk_query.append(query)
        elif filter(Left, Right):
            self.bulk_query.append(query)

        # with self._make_client() as client:
        #     with client.session(keyspace=self.KEYSPACE) as session:
        #         with session.transaction().write() as tx:
                    
        #             '''
        #                 class : relation_name
        #                 obj_struct:
        #                 {
        #                     relates:(
        #                         {
        #                             entity: Left
        #                             identifier: gid
        #                             value: <x>
        #                             as: beep
        #                         },
        #                         {
        #                             entity: Right
        #                             identifier: gid
        #                             value: <y>
        #                             as: bop
        #                         }
        #                     )
        #                 }
        #             '''
        #             query = _build_query(props, relation_name)
        #             Left, Right = props['relates']
        #             if filter is None:
        #                 insert_it = tx.query(query)
        #                 concepts = insert_it.collect_concepts()
        #                 tx.commit()
        #                 print("No filter")
        #                 print(query)
        #             elif filter(Left, Right):
        #                 insert_it = tx.query(query)
        #                 concepts = insert_it.collect_concepts()
        #                 tx.commit()
        #                 print("with filter")
        #                 print(query)
        
    def save(self, o):
        # with self._make_client() as client:
        #     with client.session(keyspace=self.KEYSPACE) as session:
        #         with session.transaction().write() as wtx:

        entity_name = getattr(o.__class__,'entity_name')
        props = o.__dict__
        fields = ', '.join([ 'has {} "{}"'.format(key, props[key]) for key in props if props[key] != ''])
        # query = 'match $o isa {}, {}; delete $o; insert $o isa {}, {}; '.format(entity_name, fields, entity_name,fields)
        
        delq = 'match $o isa {}, {}; delete $o;'.format(entity_name, fields)
        insq = 'insert $o isa {}, {}; '.format(entity_name,fields)
        self.bulk_query.append(delq)
        self.bulk_query.append(insq)

        # if len(fields) > 0 :
        #     print(query)
        #     insert_it = wtx.query(query)
        #     concepts = insert_it.collect_concepts()
        #     print("inserted content with id {}".format(concepts[0].id))
        #     wtx.commit()
        # else:
        #     print("ignoring query for object : {}".format(o.__dict__))

    def flush(self):
        
        with self._session.transaction().write() as wtx:
            # q = " ".join(self.bulk_query)
            # print("executing :\n< {} >".format(q))
            
            for q in self.bulk_query:
                try:
                    print("writing: <{}>".format(q))
                    insert_it = wtx.query(q)
                    concepts = insert_it.collect_concepts()
                    print(concepts)
                    
                except Exception as e:
                    print("Exception : {}".format(e))
                    Exception("Insert not returns id, it may caused by insertion failed.")
            
            wtx.commit()
        
            del self.bulk_query
            self.bulk_query = []

    def update(self, o, update_by):
        
        entity_name = getattr(o.__class__,'entity_name')
        props = o.__dict__
        crit_prop = copy.deepcopy(o.__dict__)
        criteria = [(key, crit_prop[key]) for key in update_by]
        print("props: {}, crit : {}, searchc: {}".format(props, crit_prop, criteria))
        # del props['name']
        # del props['gid']
        print("props: {}, crit : {}, searchc: {}".format(props, crit_prop, criteria))

        fields = ', '.join([ 'has {} "{}"'.format(key, props[key]) for key in props if props[key] != '' and key != 'gid' ])
        criteria = ', '.join(['has {} "{}"'.format(k, v) for k, v in criteria])
        if len(fields) > 0:
            query = 'match $x isa {}, {} ; insert $x {}; '.format(entity_name,criteria,fields)
            self.bulk_query.append(query)