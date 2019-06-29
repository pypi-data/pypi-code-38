from seq2label.input import to_fixed_len
from tensorflow.contrib import predictor

model_dir = '/Users/howl/PyCharmProjects/seq2label/results/saved_model/TextCNN-32-0.001-600-15000/1555931680'

predict_fn = predictor.from_saved_model(model_dir)


def serve(input_text):
    # input_text = list(map(self.char_to_index_table.lookup, input_text))

    input_feature = {
        'words': [to_fixed_len([i for i in input_text], 20, '<pad>')],
    }

    print(input_feature)

    predictions = predict_fn(input_feature)
    print(predictions)
    
    
serve('你好么')
