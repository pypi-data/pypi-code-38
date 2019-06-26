def generate_output(content,debug=None):
    output = {
        'error': None,
        'body': content,
        'debug': debug
    }
    return output

def generate_error(message,body=None,debug=None):
    output = {
        'error': message,
        'body': body,
        'debug': debug
    }
    return output