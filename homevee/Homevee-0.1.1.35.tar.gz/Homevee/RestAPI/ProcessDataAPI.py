#!flask/bin/python
import json

from flask import Blueprint, request

from Homevee.API import API
from Homevee.Utils.Database import Database

ProcessDataAPI = Blueprint('ProcessDataAPI', __name__, template_folder='templates')

@ProcessDataAPI.route('/processdata', methods=['POST'])
def process_data():
    print("processdata")

    data = request.get_json()

    msg = API().process_data(data, Database())

    print(msg)

    return json.dumps(msg)