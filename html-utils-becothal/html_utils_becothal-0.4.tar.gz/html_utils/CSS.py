from .file_model import file_model
import re
import base64


class CSS(file_model):
    fontRegex = "src: *url\\('.*\\.ttf.*"

    def trueTypeToBase64(self):
        """
        Replaces the path to the fontfile with the BASE64 encoded file.
        """
        fonts = re.findall(self.fontRegex, self.content)
        for item in fonts:
            fileName = item[item.find("url(\'") + 5:item.find(".ttf")+4]
            with open(self.rootDir + fileName, "rb") as font_file:
                fontFileContent = font_file.read()
                encodedString = base64.b64encode(fontFileContent)
                font_file.close()
            self.content = self.content.replace("\'"+fileName+"\'", "data:font/ttf;base64,"+encodedString)