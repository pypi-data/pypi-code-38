import tensorflow as tf

from datasets.matchpyramid import MatchPyramidSameFileDataset, MatchPyramidSeparateFilesDataset
from datasets.utils import data_dir_utils

config = {
    'x_vocab_file': data_dir_utils.get_data_file('dssm.vocab.txt'),
    'share_vocab_file': True,
    'train_batch_size': 2,
    'eval_batch_size': 2,
    'predict_batch_size': 2,
    'num_parallel_calls': 1,
}


class XYZSameFileDatasetTest(tf.test.TestCase):

    def printDataset(self, ds):
        for i, v in enumerate(ds):
            print('%d : %s' % (i, v))

    def testBuildTrainDataset(self):
        d = MatchPyramidSameFileDataset(config=config, logger_name=None)
        files = [data_dir_utils.get_data_file('dssm.query.doc.label.txt')]
        dataset = d.build_train_dataset(train_files=files)
        self.printDataset(dataset)

    def testBuildEvalDataset(self):
        d = MatchPyramidSameFileDataset(config=config, logger_name=None)
        files = [data_dir_utils.get_data_file('dssm.query.doc.label.txt')]
        dataset = d.build_eval_dataset(eval_files=files)
        self.printDataset(dataset)

    def testBuildPredictDataset(self):
        d = MatchPyramidSameFileDataset(config=config, logger_name=None)
        files = [data_dir_utils.get_data_file('dssm.query.doc.label.txt')]
        dataset = d.build_predict_dataset(predict_files=files)
        self.printDataset(dataset)


class XYZSeparateFileDatasetTest(tf.test.TestCase):

    def testBuildTrainDataset(self):
        o = MatchPyramidSeparateFilesDataset(config=config, logger_name=None)
        x_files = [data_dir_utils.get_data_file('dssm.query.txt')]
        y_files = [data_dir_utils.get_data_file('dssm.doc.txt')]
        z_files = [data_dir_utils.get_data_file('dssm.label.txt')]
        train_dataset = o.build_train_dataset(x_files, y_files, z_files)
        v = next(iter(train_dataset))
        print(v)

    def testBuildEvalDataset(self):
        o = MatchPyramidSeparateFilesDataset(config=config, logger_name=None)
        x_files = [data_dir_utils.get_data_file('dssm.query.txt')]
        y_files = [data_dir_utils.get_data_file('dssm.doc.txt')]
        z_files = [data_dir_utils.get_data_file('dssm.label.txt')]
        train_dataset = o.build_eval_dataset(x_files, y_files, z_files)
        v = next(iter(train_dataset))
        print(v)

    def testBuildPredictDataset(self):
        o = MatchPyramidSeparateFilesDataset(config=config, logger_name=None)
        x_files = [data_dir_utils.get_data_file('dssm.query.txt')]
        y_files = [data_dir_utils.get_data_file('dssm.doc.txt')]
        train_dataset = o.build_predict_dataset(x_files, y_files)
        v = next(iter(train_dataset))
        print(v)


if __name__ == '__main__':
    tf.test.main()
