from werkzeug import secure_filename
from flask import jsonify, abort

def upload_form_file(fname, file, bucket):

    filename = file.filename

    _filename = secure_filename(filename)
    basename, extension = _filename.rsplit('.', 1)

    filename = '{}.{}'.format(fname, extension)

    blob = bucket.blob(filename)

    blob.upload_from_string(
        file.stream.read(),
        content_type='image/' + extension)

    url = blob.public_url

    return url

def request_abort(status_code, message):
    data = {
        'error': {
            'code': status_code,
            'message': message
        }
    }
    response = jsonify(data)
    response.status_code = status_code
    abort(response)