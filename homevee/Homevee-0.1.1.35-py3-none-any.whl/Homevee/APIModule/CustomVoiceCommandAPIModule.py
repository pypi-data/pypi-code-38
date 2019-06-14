from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.CustomVoiceCommandManager import CustomVoiceCommandManager

ACTION_KEY_GET_VOICE_COMMANDS = "getvoicecommands"
ACTION_KEY_ADD_EDIT_VOICE_COMMAND = "addeditvoicecommand"
ACTION_KEY_DELETE_VOICE_COMMAND = "deletevoicecommand"

class CustomVoiceCommandAPIModule(APIModule):
    def __init__(self):
        super(CustomVoiceCommandAPIModule, self).__init__()
        self.voice_command_manager = CustomVoiceCommandManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_VOICE_COMMANDS: self.get_voice_commands,
            ACTION_KEY_ADD_EDIT_VOICE_COMMAND: self.add_edit_voice_command,
            ACTION_KEY_DELETE_VOICE_COMMAND: self.delete_voice_command
        }

        return mappings

    def get_voice_commands(self, user, request, db):
        data = self.voice_command_manager.get_voice_commands(db)
        return Status(type=STATUS_OK, data={'commands': data})

    def add_edit_voice_command(self, user, request, db):
        self.voice_command_manager.add_edit_voice_command(user, request['id'], request['name'],
                                                                          request['command_data'],
                                                                          request['response_data'],
                                                                          request['action_data'], db)
        return Status(type=STATUS_OK)

    def delete_voice_command(self, user, request, db):
        self.voice_command_manager.delete_voice_command(user, request['id'], db)
        return Status(type=STATUS_OK)