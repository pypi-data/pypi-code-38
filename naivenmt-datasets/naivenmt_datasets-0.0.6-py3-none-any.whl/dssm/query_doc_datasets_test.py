import tensorflow as tf

from datasets.dssm.query_doc_datasets import QueryDocSameFileDataset, QueryDocSeparateFilesDataset
from datasets.utils import data_dir_utils as utils


class QueryDocDatasetTest(tf.test.TestCase):

    def testQueryDocSameFileDataset(self):
        config = {
            'train_batch_size': 1,
            'eval_batch_size': 1,
            'predict_batch_size': 1,
            'num_parallel_calls': 1
        }
        o = QueryDocSameFileDataset(
            vocab_file=utils.get_data_file('dssm.vocab.txt'),
            params=config)

        train_dataset = o.build_train_dataset(train_files=[utils.get_data_file('dssm.query.doc.label.txt')])
        eval_dataset = o.build_eval_dataset(eval_files=[utils.get_data_file('dssm.query.doc.label.txt')])
        predict_dataset = o.build_predict_dataset(predict_files=[utils.get_data_file('dssm.query.doc.label.txt')])

        # print(train_dataset)

        for v in iter(train_dataset):
            (q, d), l = v
            print(q)
            print(d)
            print(l)
            print('=====================================')
        print('+++++++++++++++++++++++++++++++++++++')

        (q, d), l = next(iter(eval_dataset))
        print(q)
        print(d)
        print(l)
        print('=====================================')

        (q, d) = next(iter(predict_dataset))
        print(q)
        print(d)
        print('=====================================')

    def testQueryDocSeparateFilesDataset(self):
        config = {
            'train_batch_size': 1,
            'eval_batch_size': 1,
            'predict_batch_size': 1,
            'num_parallel_calls': 1
        }
        o = QueryDocSeparateFilesDataset(
            vocab_file=utils.get_data_file('dssm.vocab.txt'),
            params=config)

        train_query_files = [utils.get_data_file('dssm.query.txt')]
        train_doc_files = [utils.get_data_file('dssm.doc.txt')]
        train_label_files = [utils.get_data_file('dssm.label.txt')]
        eval_query_files = [utils.get_data_file('dssm.query.txt')]
        eval_doc_files = [utils.get_data_file('dssm.doc.txt')]
        eval_label_files = [utils.get_data_file('dssm.label.txt')]
        predict_query_files = [utils.get_data_file('dssm.query.txt')]
        predict_doc_files = [utils.get_data_file('dssm.doc.txt')]

        train_files = (train_query_files, train_doc_files, train_label_files)
        eval_files = (eval_query_files, eval_doc_files, eval_label_files)
        predict_files = (predict_query_files, predict_doc_files, None)

        train_dataset = o.build_train_dataset(train_files=train_files)
        eval_dataset = o.build_eval_dataset(eval_files=eval_files)
        predict_dataset = o.build_predict_dataset(predict_files=predict_files)

        # print(train_dataset)

        for v in iter(train_dataset):
            (q, d), l = v
            print(q)
            print(d)
            print(l)
            print('=====================================')
        print('+++++++++++++++++++++++++++++++++++++')

        (q, d), l = next(iter(eval_dataset))
        print(q)
        print(d)
        print(l)
        print('=====================================')

        (q, d) = next(iter(predict_dataset))
        print(q)
        print(d)
        print('=====================================')


if __name__ == '__main__':
    tf.test.main()
