import unittest
import word_net


class WordNetTest(unittest.TestCase):
    def test_should_return_path_similarity_1_between_same_concepts(self):
        similarity = word_net.determine_path_similarity_between_two_concepts('cup.n.01', 'cup.n.01')
        self.assertEqual(similarity, 1.0)

    def test_should_return_path_similarity_033_between_sister_concepts(self):
        similarity = word_net.determine_path_similarity_between_two_concepts('drinking_glass.n.01', 'cup.n.01')
        expected_value = 1.0/3.0
        self.assertEqual(similarity, expected_value)


if __name__ == "__main__":
    unittest.main()
