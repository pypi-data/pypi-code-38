import os

class CookieSessionManager:
    def __init__(self, sessionFolder, filename):
        self.session_folder = sessionFolder
        self.filename = filename


    def get_saved_cookies(self):
        try:
            f = open(self.session_folder + self.filename, 'r') 
            return f.read()
        except FileNotFoundError:
            return None

    def set_saved_cookies(self, cookie_string):
        if not os.path.exists(self.session_folder):
            os.makedirs(self.session_folder)

        f = open(self.session_folder + self.filename,"w+")
        f.write(cookie_string)
        f.close

    def empty_saved_cookies(self):
        try:
            os.remove(self.session_folder + self.filename)
        except FileNotFoundError:
            pass