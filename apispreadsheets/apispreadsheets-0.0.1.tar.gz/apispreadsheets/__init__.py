name = "apispreadsheets"

import requests

def data(file_id, output_format=None, accessKey=None, secretKey=None):
    base_url = "https://api-woyera.com/api/data/"

    check_paramter_errors(output_format, accessKey, secretKey)

    output = "jsonRow" if output_format is None else output_format

    url = base_url + str(file_id) + "/" + output + "/"

    if accessKey is None and secretKey is None:
        r = requests.get(url)

        get_status_code = r.status_code

        if get_status_code == 200:
            return r.json()
        elif get_status_code == 400:
            raise ValueError("The file is private. Please provide access and secret keys")
        elif get_status_code == 404:
            raise ValueError("This file ID does not exist. Please find the correct ID from your dashboard")
        else:
            raise ValueError("There was something wrong on our server. Try again or contact us at info@apispreadsheets.com if the problem persists")
    else:
        r = requests.post(url, headers={'accessKey': accessKey, 'secretKey': secretKey})

        post_status_code = r.status_code

        if post_status_code == 200:
            return r.json()
        elif post_status_code == 401:
            raise ValueError("The Access or Secret key is invalid")
        elif post_status_code == 404:
            raise ValueError("This file ID does not exist or is not your file. Please find the correct ID from your dashboard")
        else:
            raise ValueError("There was something wrong on our server. Try again or contact us at info@apispreadsheets.com if the problem persists")


def check_paramter_errors(output_format, accessKey, secretKey):
    if output_format not in ['jsonRow', 'jsonColumn', 'matrix'] and output_format is not None:
        raise ValueError("Output format must be jsonRow, jsonColumn or matrix or not used. Default is jsonRow")

    if (accessKey is None and secretKey is not None) or (secretKey is None and accessKey is not None):
        raise ValueError("Both access and secret key parameters must have values or not be used")
