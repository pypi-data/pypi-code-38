import pandas as pd
import tensorflow as tf


class TensorObserveHook(tf.train.SessionRunHook):
    def __init__(self, d1_mapping=None, d2_mapping=None, d2_mapper=None):
        self.d1_mapping = {} if not d1_mapping else d1_mapping
        self.d2_mapping = {} if not d2_mapping else d2_mapping
        self.d2_mapper = {} if not d2_mapper else d2_mapper

    def before_run(self, run_context):
        fetches = list(map(
            lambda x: run_context.session.graph.get_tensor_by_name(x),
            list(self.d1_mapping.values()) + list(self.d2_mapping.values())
        ))
        return tf.train.SessionRunArgs(
            fetches=fetches
        )

    def after_run(self, run_context, run_values):
        print('-- 1d level --')
        for i in range(len(self.d1_mapping)):
            print(list(self.d2_mapping.keys())[i], run_values.results[i])

        print('-- 2d level --')
        data = []
        for i in range(len(self.d1_mapping), len(self.d1_mapping) + len(self.d2_mapping)):
            v = run_values.results[i]
            k = list(self.d2_mapping.keys())[i - len(self.d1_mapping)]
            mapper = self.d2_mapper.get(k, lambda x: x)

            data.append([k, v, mapper])

        for index in range(len(data[0][1])):
            output_data = {}
            for k, v, mapper in data:
                decoded_v = list(map(mapper, v[index]))
                output_data[k] = decoded_v

            df = pd.DataFrame(output_data)

            print(df)


if __name__ == "__main__":
    hook = TensorObserveHook(
        {
            'fake_golden': 'fake_golden:0',
            'fake_prediction': 'fake_prediction:0'
        },
        {
            "word_str": "word_strings_Lookup:0",
            "predictions_id": "predictions:0",
            "predict_str": "predict_Lookup:0",
            "labels_id": "labels:0",
            "labels_str": "IteratorGetNext:2",
        },
        {
            "word_str": lambda x: x.decode(),
            'predict_str': lambda x: x.decode(),
            'labels_str': lambda x: x.decode()
        }
    )
