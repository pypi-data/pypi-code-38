from flask import Flask, request, jsonify, abort, send_file
import os
from io import BytesIO
from eml2png import __version__, to_png

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            file_path = os.path.join('/tmp', file.filename)
            file.save(file_path)
            output_name = '{}.png'.format(file.filename)
            output_path = os.path.join('/tmp', output_name)
            open(output_path, 'wb').write(to_png(file_path))
            resp = send_file(output_path, attachment_filename=output_name)
            try:
                os.remove(file_path)
                os.remove(output_path)
            except Exception:
                pass
            return resp
        else:
            return 'Missing file'
    return 'Hello World from eml2png: {}'.format(__version__)


if __name__ == '__main__':
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=int(os.environ.get('PORT', '80')))
