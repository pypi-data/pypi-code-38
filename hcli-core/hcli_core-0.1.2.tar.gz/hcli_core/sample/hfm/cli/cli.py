import json
import io
from functools import partial

class CLI:
    commands = None
    inputstream = None
    
    def __init__(self, commands, inputstream):
        self.commands = commands
        self.inputstream = inputstream

    def execute(self):

        if self.inputstream != None and self.commands[2] == '-l':
            self.upload()
            return None

        if self.inputstream == None and self.commands[2] == '-r':
            return self.download()

    def upload(self):
        unquoted = self.commands[3].replace("'", "").replace("\"", "")
        with io.open(unquoted, 'wb') as f:
            for chunk in iter(partial(self.inputstream.read, 16384), b''):
                f.write(chunk)

        return None

    def download(self):
        f = open(self.commands[3].replace("'", ""), "rb")
        return io.BytesIO(f.read())
