from file_model import file_model
import re
from CSS import CSS


class HTML(file_model):

    cssRegex = "(<link rel=\"stylesheet\".* href=\".*\\.css\">)"
    jsRegex = "(<script.*src=\".*\"><\/script>)"

    def __init__(self):
        file_model.__init__(self)
        print"HTML init"

    def inlineCSS(self):
        """
        Searches for linked CSS files and copies the content into the HTML file,
        so that there is only one file in the end.
        """
        tempString = ""
        if self.content == "":
            print "InlineCSS: cannot inline. File must be read first."
            return
        cssFiles = re.findall(self.cssRegex, self.content)
        if len(cssFiles) > 0:
            i = 0
            for item in cssFiles:
                if i == 0:
                    tempString = "<style>"

                cssFile = CSS()
                cssFile.readFile(self.rootDir + HTML.getFilePathFromLink(str(item)))
                cssFile.trueTypeToBase64()
                tempString += cssFile.toString()

                if i == len(cssFiles)-1:
                    tempString += "</style>"

                self.content = self.content.replace(str(item), tempString)

                tempString = ""
                i += 1

    def inlineJS(self):
        """
        Searches the HTML file for linked JavaScript files and inlines them to the HTML file.
        """
        tempString = ""
        if self.content == "":
            print "inlineJS: cannot inline. Content is Empty. File must be read first"
            return
        jsFiles = re.findall(self.jsRegex, self.content)
        if len(jsFiles) > 0:
            i = 0
            for item in jsFiles:
                if i == 0:
                    tempString = "<script>"
                jsFile = file_model()
                jsFile.readFile(self.rootDir + HTML.getFilePathFromLink(str(item)))
                tempString += jsFile.toString()
                if i == len(jsFiles)-1:
                    tempString += "</script>"

                self.content = self.content.replace(str(item), tempString)
                tempString = ""
                i += 1

    def writeFile(self, fileName):
        """
        Writes the content of the HTML-Object into a File
        :param fileName: Filename for the output file
        :type fileName: str
        """
        if fileName == "":
            print "writeFile: No FileName provided!"
            return
        else:
            fileHandler = open(fileName, "w")
            fileHandler.write(self.toString())
            fileHandler.close()

    @staticmethod
    def getFilePathFromLink(link):
        """
        Returns the filepath for a file in a <link> in HTML
        :param link: <link> from HTML
        :type link: str
        :returns: Filepath provided in the <link>
        :rtype: str
        """
        if link == "":
            print "getFilePathFromLink: No link provided"
            return
        filePath = ""
        if link.find("href=") > 0:
            filePath = link[link.find("href=\"") + 6:link.rfind("\"")]
        elif link.find("src=") > 0:
            filePath = link[link.find("src=\"") + 5:link.rfind("\"")]
        else:
            print "getFilePathFromLink: Unrecognized pattern :" + link
            return
        return filePath