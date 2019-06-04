from Homevee.Item.Logic.Action import Action


class Logic():
    def __init__(self):
        return

    @staticmethod
    def get_action_from_dict(dict):
        type = dict['action_type']

        module_map = Action.get_module_map()

        if type not in module_map:
            return None

        return module_map[type].get_from_dict(dict)

    @staticmethod
    def get_actions_from_dict(dict):
        actions = []

        for item in dict:
            action = Logic.get_action_from_dict(item)

            if action is not None:
                actions.append(action)

        return action