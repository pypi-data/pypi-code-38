import os

import numpy as np
import paddle.fluid as fluid

from seq2label.input_paddle import read_vocabulary


class Inference(object):
    def __init__(self, model_path):
        # load model
        self.place = fluid.CPUPlace()
        self.exe = fluid.Executor(self.place)
        [self.inference_program, self.feed_target_names, self.fetch_targets] = fluid.io.load_inference_model(dirname=model_path, executor=self.exe)

        # load vocabulary
        self.vocabulary = read_vocabulary(os.path.join(model_path, 'data/vocabulary.txt'))
        self.tag = read_vocabulary(os.path.join(model_path, 'data/tags.txt'))

    def infer(self, input_text):
        data = [self.vocabulary.lookup(i) for i in input_text]

        word = fluid.create_lod_tensor([data], [[len(data)]], self.place)

        results, = self.exe.run(
            self.inference_program,
            feed={self.feed_target_names[0]: word},
            fetch_list=self.fetch_targets,
            return_numpy=True
        )

        # find best result
        best_result_int = np.argmax(results[0])

        # translate to str list
        best_result = self.tag.id_to_str(best_result_int)

        # candidate
        candidate = [(self.tag.id_to_str(i), v) for i, v in enumerate(results[0].tolist())]
        candidate = sorted(candidate, key=lambda v: v[1], reverse=True)

        return best_result, candidate


if __name__ == '__main__':
    inference = Inference('/Users/howl/PyCharmProjects/seq2label/results/saved_model/1557927547')

    result = inference.infer('查这几天的天气。')
    print(result)
