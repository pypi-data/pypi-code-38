#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from Homevee.Helper import Logger
from Homevee.Manager.CustomVoiceCommandManager import CustomVoiceCommandManager
from Homevee.VoiceAssistant import Helper
from Homevee.VoiceAssistant.Modules.ConversationModule import VoiceConversationModule
# reload(sys)
# sys.setdefaultencoding('utf8')
from Homevee.VoiceAssistant.VoiceModules import get_voice_modules


class VoiceAssistant():
    def do_voice_command(self, username, text, user_last_location, room, db, language):
        return self.voice_command(username, text, user_last_location, room, db, language)

    def voice_command_cloud(self, username, text, user_last_location, room, db, language):
        text = text.lower()

        text = Helper.replace_voice_commands(text, username, db)

        # run custom voice_commands
        answer = CustomVoiceCommandManager().run_custom_voice_commands(text, username, db)

        if (answer is not None):
            return {'msg_speech': answer, 'msg_text': answer}

        Logger.log("Voice command: " + text)

        context = Helper.get_context(username, db)

        voice_modules = get_voice_modules()

        if context is not None:
            return self.run_context(voice_modules, context, username, text, user_last_location, room, db, language)
        else:
            MIN_CONFIDENCE = 0.95

            try:
                result = Helper.classify_voice_command(text)
            except:
                return self.do_voice_command(username, text, user_last_location, room, db, language)

            Logger.log(result)

            label = result['label']
            confidence = result['confidence']

            module_map = {}

            for module in voice_modules:
                module_map[module.get_label()] = module.run_command

            if confidence >= MIN_CONFIDENCE and label in module_map:
                answer = module_map[label](username, text, context, db)
            else:
                answer = VoiceConversationModule().run_command(username, text, context, db)

        return (answer)

    def voice_command(self, username, text, user_last_location, room, db, language):
        #return {'msg_speech': "Der Assistent ist noch nicht erreichbar.", 'msg_text': "Der Assistent ist zur Zeit noch nicht fertig, wird aber gerade implementiert."}

        #room => damit z.b. bei "mach das licht an" das licht im richtigen raum angeht

        #Logger.log "voice_command"

        text = text.lower()

        #use ai-classifier in cloud
        #try:
        #    helper.classify_voice_command(text)
        #except:
        #    Logger.log("Homevee assistant not working")

        text = Helper.replace_voice_commands(text, username, db)

        #run custom voice_commands
        answer = CustomVoiceCommandManager().run_custom_voice_commands(text, username, db)

        if(answer is not None):
            return {'msg_speech': answer, 'msg_text': answer}

        #Logger.log("Voice command: "+text)

        context = Helper.get_context(username, db)

        voice_modules = get_voice_modules()

        if context is not None:
            return self.run_context(voice_modules, context, username, text, user_last_location, room, db, language)
        else:
            for module in voice_modules:
                if(Helper.contains_pattern(module.get_pattern(db), text)):
                    answer = module.run_command(username, text, context, db)
                    break

            if answer is None:
                answer = VoiceConversationModule().run_command(username, text, context, db)

        Logger.log(answer)

        return answer

    def run_context(self, voice_modules, context, username, text, user_last_location, room, db, language):
        answer = None

        context_data = json.loads(context['CONTEXT_DATA'])

        Logger.log("Kontext: " + str(context_data))

        for module in voice_modules:
            context_key = module.get_context_key()

            if context_key is None:
                continue

            if isinstance(context_key, list):
                if context['CONTEXT_KEY'] in context_key:
                    answer = module.run_command(username, text, context_data, db)
            else:
                if context['CONTEXT_KEY'] == context_key:
                    answer = module.run_command(username, text, context_data, db)

        if answer is None or not answer:
            return self.do_voice_command(username, text, user_last_location, room, db, language)

        return (answer)