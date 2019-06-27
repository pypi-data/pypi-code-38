import tensorflow as tf

from datasets.nmt.legacy_datasets import LegacyDataset
from datasets.utils import data_dir_utils as utils


class LegacyDatasetTest(tf.test.TestCase):

    def testBuildDataset(self):
        nmt_dataset = LegacyDataset(
            src_train_files=[utils.get_data_file('iwslt15.tst2013.100.en')],
            tgt_train_files=[utils.get_data_file('iwslt15.tst2013.100.vi')],
            src_eval_files=[utils.get_data_file('iwslt15.tst2013.100.en')],
            tgt_eval_files=[utils.get_data_file('iwslt15.tst2013.100.vi')],
            predict_files=[utils.get_data_file('iwslt15.tst2013.100.en')],
            src_vocab_file=utils.get_data_file('iwslt15.vocab.100.en'),
            tgt_vocab_file=utils.get_data_file('iwslt15.vocab.100.vi'),
            src_vocab_size=100,
            tgt_vocab_size=100,
        )
        train_dataset = nmt_dataset.build_train_dataset()
        eval_dataset = nmt_dataset.build_eval_dataset()
        predict_dataset = nmt_dataset.build_predict_dataset()

        for v in next(iter(train_dataset)):
            print(v)
        print('-------------------------------------------------------')
        for v in next(iter(eval_dataset)):
            print(v)
        print('-------------------------------------------------------')
        for v in next(iter(predict_dataset)):
            print(v)


if __name__ == '__main__':
    tf.test.main()
