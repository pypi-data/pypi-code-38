from Homevee.VoiceAssistant import VoiceAssistant

def do_voice_command(username, text, user_last_location, location, db, language):
    return VoiceAssistant().do_voice_command(username, text, user_last_location, location, db, language)