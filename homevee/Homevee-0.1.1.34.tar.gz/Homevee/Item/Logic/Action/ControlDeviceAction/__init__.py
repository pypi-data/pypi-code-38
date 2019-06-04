from Homevee.Exception import AbstractFunctionCallException
from Homevee.Item.Logic.Action import Action


class ControlDeviceAction(Action):
    def __init__(self):
        super(ControlDeviceAction, self).__init__()

    def run(self):
        raise AbstractFunctionCallException("ControlDeviceAction.run() is abstract")