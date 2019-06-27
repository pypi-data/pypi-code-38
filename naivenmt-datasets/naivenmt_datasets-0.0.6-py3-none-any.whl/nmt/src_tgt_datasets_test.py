import tensorflow as tf

from datasets.nmt.src_tgt_datasets import SourceDataset, TargetDataset, SourceTargetDataset
from datasets.utils import data_dir_utils as utils


class SourceTargetDatasetsTest(tf.test.TestCase):

    def testSourceDataset(self):
        d = SourceDataset(
            src_train_files=[utils.get_data_file('iwslt15.tst2013.100.en')],
            src_eval_files=[utils.get_data_file('iwslt15.tst2013.100.en')],
            src_predict_files=[utils.get_data_file('iwslt15.tst2013.100.en')],
            src_vocab_file=utils.get_data_file('iwslt15.vocab.100.en'),
            params=None
        )

        train_dataset = d.build_train_dataset()
        eval_dataset = d.build_eval_dataset()
        predict_dataset = d.build_predict_dataset()

        for src in train_dataset:
            print(src)
        print('=========================================================\n')
        for src in eval_dataset:
            print(src)
        print('=========================================================\n')
        for src in predict_dataset:
            print(src)

    def testTargetDataset(self):
        d = TargetDataset(
            tgt_train_files=[utils.get_data_file('iwslt15.tst2013.100.vi')],
            tgt_eval_files=[utils.get_data_file('iwslt15.tst2013.100.vi')],
            tgt_vocab_file=utils.get_data_file('iwslt15.vocab.100.vi'),
            params=None
        )

        train_dataset = d.build_train_dataset()
        eval_dataset = d.build_eval_dataset()
        predict_dataset = d.build_predict_dataset()

        assert not predict_dataset

        for tgt in train_dataset:
            print(tgt)
        print('=========================================================\n')

        for tgt in eval_dataset:
            print(tgt)
        print('=========================================================\n')

    def testSourceTargetDataset(self):
        d = SourceTargetDataset(
            src_train_files=[utils.get_data_file('iwslt15.tst2013.100.en')],
            src_eval_files=[utils.get_data_file('iwslt15.tst2013.100.en')],
            src_predict_files=[utils.get_data_file('iwslt15.tst2013.100.en')],
            src_vocab_file=utils.get_data_file('iwslt15.vocab.100.en'),
            tgt_train_files=[utils.get_data_file('iwslt15.tst2013.100.vi')],
            tgt_eval_files=[utils.get_data_file('iwslt15.tst2013.100.vi')],
            tgt_vocab_file=utils.get_data_file('iwslt15.vocab.100.vi'),
            params=None
        )

        train_dataset = d.build_train_dataset()
        eval_dataset = d.build_eval_dataset()
        predict_dataset = d.build_predict_dataset()

        for src, tgt in train_dataset:
            print('src:')
            print(src)
            print('tgt:')
            print(tgt)
        print('=========================================================\n')

        for src, tgt in eval_dataset:
            print(src)
            print(tgt)
        print('=========================================================\n')

        for src in predict_dataset:
            print(src)


if __name__ == '__main__':
    tf.test.main()
