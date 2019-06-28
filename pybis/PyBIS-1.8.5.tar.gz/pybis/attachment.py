import base64
import os

class Attachment():
    def __init__(self, filename, title=None, description=None):
        if not os.path.exists(filename):
            raise ValueError("File not found: {}".format(filename))
        self.fileName = filename
        self.title = title
        self.description = description

    def get_data_short(self):
        return {
            "fileName": self.fileName,
            "title": self.title,
            "description": self.description,
        }

    def get_data(self):
        with open(self.fileName, 'rb') as att:
            content = att.read()
            contentb64 = base64.b64encode(content).decode()
        return {
            "fileName": self.fileName,
            "title": self.title,
            "description": self.description,
            "content": contentb64,
            "@type": "as.dto.attachment.create.AttachmentCreation",
        }
