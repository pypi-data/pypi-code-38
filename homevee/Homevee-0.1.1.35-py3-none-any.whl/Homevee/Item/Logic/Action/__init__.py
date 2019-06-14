from Homevee.Exception import AbstractFunctionCallException
from Homevee.Item.Logic.Action.ControlDeviceAction import ControlDeviceAction
from Homevee.Item.Logic.Action.PushNotificationAction import PushNotificationAction
from Homevee.Item.Logic.Action.RunSceneAction import RunSceneAction

ACTION_PUSH_NOTIFICATION = "push_notification"
ACTION_RUN_SCENE = "run_scene"
ACTION_CONTROL_DEVICE = "control_device"

class Action():
    def __init__(self):
        return

    def run(self):
        """
        Runs this action
        :return:
        """
        raise AbstractFunctionCallException("Action.run() is abstract")

    @staticmethod
    def get_module_map():
        module_map = {
            ACTION_PUSH_NOTIFICATION: PushNotificationAction,
            ACTION_RUN_SCENE: RunSceneAction,
            ACTION_CONTROL_DEVICE: ControlDeviceAction
        }
        return module_map