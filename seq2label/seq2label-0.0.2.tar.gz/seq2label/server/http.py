import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
from seq2label.input import to_fixed_len

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# app.config['DEBUG'] = True
CORS(app)

from tensorflow.contrib import predictor

server = None


def load_predict_fn(export_dir):
    global server
    server = Server(export_dir)

    return server


class Server(object):
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.predict_fn = predictor.from_saved_model(model_dir)

    def serve(self, input_text, raise_exception=False):
        # input_text = list(map(self.char_to_index_table.lookup, input_text))

        input_feature = {
            'words': [to_fixed_len([i for i in input_text], 20, '<pad>')],
        }

        print(input_feature)

        predictions = self.predict_fn(input_feature)
        label = predictions['label'][0]

        return label.decode()


@app.route("/parse", methods=['GET'])
def single_tokenizer():
    text_msg = request.args.get('q')

    print(text_msg)

    label = server.serve(text_msg)

    print(label)
    # print(seq)

    response = {
        'text': text_msg,
        'label': label
    }

    return jsonify(response)


if __name__ == "__main__":
    load_predict_fn(sys.argv[1])

    app.run(host='0.0.0.0', port=5000)
