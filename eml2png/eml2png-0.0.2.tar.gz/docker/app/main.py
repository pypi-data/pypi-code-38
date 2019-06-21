import os
from io import BytesIO

from eml2png import __version__, get_html_str_from_file, to_png
from flask import Flask, abort, request, send_file

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            output_name = '{}.png'.format(file.filename)
            eml_html = get_html_str_from_file(None, str(file.read(), 'utf8'))
            png_bytes = to_png(None, eml_html)
            return send_file(BytesIO(png_bytes), as_attachment=True, attachment_filename=output_name, mimetype='image/png')
        else:
            return abort(400, 'Missing file')
    return 'Hello World from eml2png: {}'.format(__version__)


if __name__ == '__main__':
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=int(os.environ.get('PORT', '80')))
