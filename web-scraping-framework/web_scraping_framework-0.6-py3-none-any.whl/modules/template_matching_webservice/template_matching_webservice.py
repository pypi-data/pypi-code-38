from flask import Flask
from flask import request
from flask import jsonify
from .template_matching import TemplateMatching
from traceback import format_exc
import sys

app = Flask(__name__)


@app.route("/")
def hello():
    return "You are at Adhril, trying to use template matching service", 200


@app.route('/match_image/', methods=['POST'])
def search_for_template_call():
    """
    Request :
        Method :- POST
        URL    :- /match_image/

        Params :
        source_image_full_path  : source image with its full path.
        template_image_full_path: template image with its full path.
        is_ref_cord             : (type : bool(1 or 0))is reference co-ordinate is given or not.
        base_image_ref_cord_x   : x-coordinate form base image.
        base_image_ref_cord_y   : y-coordinate form base image.
    :return:
        json_response, Response code.
        where,
            400 -> Bad request
            200 -> OK
    """
    try:
        source_image_full_path = request.form.get('source_image_full_path')
        if source_image_full_path is None:
            raise Exception("source image not found")
        print(source_image_full_path)
    except Exception as e:
        print("failed to receive source image path")
        return jsonify("source image not found"), 400
    try:
        template_image_full_path = request.form.get('template_image_full_path')
        if template_image_full_path is None:
            raise Exception("template image not found")
        print(template_image_full_path)
    except Exception as e:
        print("failed to receive template image path")
        return jsonify("template image not found"), 400
    try:
        if int(request.form.get('is_ref_cord')) == 1:
            ref_coordinate_base_image = True
        else:
            ref_coordinate_base_image = False
    except Exception as e:
        ref_coordinate_base_image = False

    template_match_obj = TemplateMatching()
    if ref_coordinate_base_image is False:
        return_obj = template_match_obj.search_for_template(source_image_full_path, template_image_full_path)
        return jsonify(return_obj), 200
    elif ref_coordinate_base_image is True:
        try:
            ref_x = int(request.form.get('base_image_ref_cord_x'))
            ref_y = int(request.form.get('base_image_ref_cord_y'))
            if ref_x is None or ref_y is None:
                raise Exception('ref_x or ref_y is not found')
            print(ref_x, ref_y)
        except Exception as e:
            print(format_exc())
            return jsonify("wrong reference coordinates and coordinates must be in integer"), 400
        # reference coordinates(ref_x,ref_y) is pixel or point. probability of finding template image near that point or pixel is more.
        return_obj = template_match_obj.match_template_by_ref_coordinates(source_image_full_path,
                                                                          template_image_full_path, ref_x, ref_y)
        return jsonify(return_obj), 200


def run_server(port):
    app.run(port=port)

if __name__ == "__main__":
    """
    Usage :
            $ template_matching_webservice.py <port number>

            <port number> : port number for the service.
        Example :
        1.    $ python template_matching_webservice.py

        2.    $ python template_matching_webservice.py 9000
    """
    try:
        # if port number is given.
        port = sys.argv[1]
        default_port = int(port)
    except Exception as e:
        # default port number if port number is not given by user explicitly.
        default_port = 9053
    run_server(default_port)
