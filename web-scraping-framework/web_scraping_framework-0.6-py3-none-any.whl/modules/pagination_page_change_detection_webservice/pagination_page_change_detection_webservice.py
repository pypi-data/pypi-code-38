from flask import Flask
from flask import request
from flask import jsonify
try:
    from pagination_page_change_detection import PaginationpageChangeDetection
except Exception:
    from .pagination_page_change_detection import PaginationpageChangeDetection
from traceback import format_exc
import sys

app = Flask(__name__)


@app.route("/")
def hello():
    return "You are at Adhril, trying to use pagination page change detection service", 200


@app.route("/pagination_page_change_detection", methods=['POST'])
def paginationpage_change_detection_call():
    """
    this webservice detect change in pagination page.
    request :
            mehtod  : POST
            url     : /pagination_page_change_detection
            param   :
                prev_url            : (type: string)Url of previous web page.
                curr_url            : (type: string)Url of current web page.
                prev_screen_shot    : (type: string)Previous web page screenshot with full path.
                curr_screen_shot    : (type: string)Current web page screenshot with full path.
                prev_content        : (type: string)Contents of previous web page.
                curr_content        : (type: string)Contents of current web page.
                threshold_value     : (type: float)Threshold value to apply for page contents.
                                        Value should given in between (0 to 1.0). Give zero to apply default threshold(0.9).

    :return:
        json_response, Response code.
        where,
            400 -> Bad request
            200 -> OK
    """
    try:
        prev_url = request.form.get('prev_url')
        if prev_url is None:
            raise Exception("prev_url not found")
        # print("Previous Url :" + prev_url)

        curr_url = request.form.get('curr_url')
        if curr_url is None:
            raise Exception("curr_url not found")
        # print("current Url :" + curr_url)

        prev_screen_shot = request.form.get('prev_screen_shot')
        if prev_screen_shot is None:
            raise Exception("prev_screen_shot not found")
        # print("previous screen shot :" + prev_screen_shot)

        curr_screen_shot = request.form.get('curr_screen_shot')
        if curr_screen_shot is None:
            raise Exception("curr_screen_shot not found")
        # print("current screen shot :" + curr_screen_shot)

        prev_content = request.form.get('prev_content')
        if prev_content is None:
            raise Exception("prev_content not found")
        # print(str(prev_content))

        curr_content = request.form.get('curr_content')
        if curr_content is None:
            raise Exception("curr_content not found")
        # print(curr_content)

        threshold_value = request.form.get('threshold_value')
        # print(threshold_value)
        if threshold_value is None:
            raise Exception("threshold_value not found")
        print("threshold: " + threshold_value)
    except Exception as e:
        print("failed to receive DATA," + format_exc())
        return jsonify("failed to receive DATA"), 400
    try:
        # Pagination page Change Detection object
        pcd_obj = PaginationpageChangeDetection()
        if float(threshold_value) > 0.0:
            pcd_obj.set_threshold_content(float(threshold_value))
        return_obj = pcd_obj.get_report(prev_url, curr_url, prev_screen_shot, curr_screen_shot, prev_content,
                                        curr_content)
        return jsonify(return_obj), 200
    except Exception as e:
        print(format_exc())
        return jsonify("Exception in generating report"), 400

def run_server(port):
    app.run(port=port)

if __name__ == "__main__":
    """
    usage :
        $ python pagination_page_change_detection_webservice.py <port number>

        port number : port number to run service. (not mandatory)
    example :

    1.  > python pagination_page_change_detection_webservice.py

    2.  > python pagination_page_change_detection_webservice.py 4000
    """
    try:
        port = sys.argv[1]
        default_port = int(port)
    except Exception as e:
        default_port = 9001
    run_server(default_port)