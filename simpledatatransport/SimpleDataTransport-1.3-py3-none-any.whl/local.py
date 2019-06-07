from __future__ import print_function
import jsonpickle
import numpy as np
import requests


class ConnectionError(Exception):
    pass


def DataSender(data, host="0.0.0.0", port= 5000, endpoint="/api/image"):
    # type: (dict, str, int, str) -> dict
    """Utility function to send dict to api endpoint

    :param data: Dict containing fields such as images in the format of a uint8 numpy array
    :param host: Remote IP address
    :param port: Remote address port
    :param endpoint: The api endpoint set in the image receiver
    :return: Response dictionary containing endpoint response
    """
    headers = {'content-type': 'application/json'}
    post_url = "http://{}:{}{}".format(host, port, endpoint)

    try:
        post_response = requests.post(post_url, data=jsonpickle.encode(data), headers=headers)
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(e)
    return jsonpickle.decode(post_response.text)


if __name__ == '__main__':
    from timeit import default_timer as timer

    while True:
        start = timer()
        img = np.random.random((512, 512, 3))
        response = DataSender({"image": img})
        print("Response received in {:.2f} ms:".format((timer() - start) * 1000), response)
