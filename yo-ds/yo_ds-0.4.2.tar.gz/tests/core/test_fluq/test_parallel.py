from tests.core.common import *
import os
import time
from yo_extensions.fluq_initiators import FileQuery
from yo_extensions.fluq import to_text_file

def _time_consuming_selector(q): # pragma: no cover
    time.sleep(0.1)
    return q



class ParallelTests(LinqTestBase):
    def test_fork(self):
        ctx = ForkContext(dict(factor=2, buffer = []))
        full_result = (
                Query
                .en(range(15))
                .fork(ctx, lambda query, context: Query
                      .en(query)
                      .where(lambda z: z%context['factor']==0)
                      .foreach_and_continue(lambda z: context['buffer'].append(z))
                      .select(lambda z: -z)
                      .to_list())
                .to_list()
        )
        self.assertListEqual(list(range(15)),full_result)
        self.assertListEqual([], ctx.sent['buffer'])
        self.assertListEqual([z for z in range(15) if z%2==0], ctx.received['buffer'])
        self.assertListEqual([-z for z in range(15) if z%2==0], ctx.result)


    def test_fire_and_forget(self):
        path = 'parallel.test.txt'
        if os.path.isfile(path):  # pragma: no cover
            os.remove(path)
        full_result = (Query
                       .en(range(15))
                       .fire_and_forget(lambda q: Query.en(q).where(lambda z: z%2==0).feed(to_text_file(self.path('test_fluq', path))))
                       .to_list()
                       )
        self.assertListEqual(list(range(15)),full_result)
        self.assertListEqual([z for z in range(15) if z%2==0], FileQuery().text(self.path('test_fluq',path)).select(int).to_list())

    def test_parallel_select_0(self):
        start_time = time.time()
        result = Query.en(range(10)).parallel_select(_time_consuming_selector,4,1).to_list()
        duration = time.time()-start_time
        self.assertLess(duration,0.5)

