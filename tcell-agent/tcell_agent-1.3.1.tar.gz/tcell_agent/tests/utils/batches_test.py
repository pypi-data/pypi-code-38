import unittest

from tcell_agent.utils.batches import batches


class BatchesTest(unittest.TestCase):
    def test_in_batches(self):
        sample = [1, 2, 3, 4, 5]
        batches_list = []

        for keys_batch in batches(sample, 2):
            batches_list.append(keys_batch)

        self.assertEqual(
            batches_list,
            [(1, 2,), (3, 4,), (5,)]
        )
