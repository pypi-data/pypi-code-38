from . import logger, mydir
import json

def hello():
    with open(mydir + '/otherlist.json', 'r') as f:
        guest_list = json.load(f)
    for each in guest_list["others"]:
        logger.info('Hi from ' + each + '!')
