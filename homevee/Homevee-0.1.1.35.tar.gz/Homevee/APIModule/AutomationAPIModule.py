from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.AutomationManager import AutomationManager

ACTION_KEY_GET_AUTOMATION_RULES = "getautomationrules"
ACTION_KEY_ADD_EDIT_AUTOMATION_RULE = "addeditautomationrule"
ACTION_KEY_DELETE_AUTOMATION_RULE = "deleteautomationrule"

class AutomationAPIModule(APIModule):
    def __init__(self):
        super(AutomationAPIModule, self).__init__()
        self.automation_manager = AutomationManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_AUTOMATION_RULES: self.get_automation_rules,
            ACTION_KEY_ADD_EDIT_AUTOMATION_RULE: self.add_edit_automation_rule,
            ACTION_KEY_DELETE_AUTOMATION_RULE: self.delete_automation_rule
        }

        return mappings

    def get_automation_rules(self, user, request, db):
        data = self.automation_manager.get_automations(user, request['location'], db)
        return Status(type=STATUS_OK, data={'rules': data})

    def add_edit_automation_rule(self, user, request, db):
        self.automation_manager.add_edit_automation_rule(user, request['location'], request['id'],
                                                                    request['name'],
                                                                    request['triggerdata'], request['conditiondata'],
                                                                    request['actiondata'],
                                                                    request['isactive'], db)
        return Status(type=STATUS_OK)

    def delete_automation_rule(self, user, request, db):
        self.automation_manager.delete_automation_rule(user, request['id'], db)
        return Status(type=STATUS_OK)