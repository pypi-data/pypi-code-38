#######################################################################################
#
# TextBlocks are a mapping of the tuple (textref, language) to a block of text
#
# Various widgets that display TextBlocks are given a textref reference string, and
# the language is generally derived from a browser setting. The widget then obtains
# the block of text and displays it.
# 
# To obtain the text, the framework imports this module and creates an instance
# of the AccessTextBlocks object, and uses its methods to find the text.
#
# This class reads TextBlocks from JSON files, stores them into memory and
# serves them to the framework when requested.
#
# The class also has methods for writing and saving TextBlocks to the JSON files
# which are used by skiadmin to create TextBlocks.
#
########################################################################################


import os, json, shutil


class AccessTextBlocks(object):


    def __init__(self, project, projectfiles, default_language):
        """The project imports this module and creates an instance of this class, and uses it to read the
           text of TextBlocks.
           The text is stored in JSON files beneath the directory
           projectfiles/project/data/textblocks_json
        """

        # the self.default_language attribute is expected to exist
        self.default_language = default_language
        # as is a set of available languages
        self._languages = set()
 
        # this implementation holds text in memory in this dictionary with keys
        # of the tuple (reference,language) and values being the text
        self._textblocks = {}
        # dictionary of textrefs with keys of reference and values being a list of languages for that textref
        self._textrefs = {}
        # read the json files from this directory and populate the above two dictionaries and self._languages
        self._textblocks_json_directory = os.path.join(projectfiles, project, "data", "textblocks_json")
        # for each language file in the directory, add it to the dictionary
        dir_contents = os.listdir(self._textblocks_json_directory)
        for filename in dir_contents:
            if not filename.endswith('.json'):
                continue
            filepath = os.path.join(self._textblocks_json_directory,filename)
            if not os.path.isfile(filepath):
                continue
            # filenames refer to languages, such as en.json, de.json
            language = filename[:-5].lower()
            self._languages.update([language])
            with open(filepath, 'r') as fp:
                textblocks_dict = json.load(fp)
                for textref, text in textblocks_dict.items():
                   self._textblocks[(textref,language)] = text
                   if textref in self._textrefs:
                       if language not in self._textrefs[textref]:
                           self._textrefs[textref].append(language)
                   else:
                        self._textrefs[textref] = [language]
        # sort language lists in self._textrefs
        for langlist in self._textrefs.values():
            langlist.sort()


    @property
    def languages(self):
        "Property which is a set of available languages"
        return self._languages

    def get_textrefs(self):
        "Returns a list of the textrefs"
        return list(self._textrefs.keys())

    def get_textref_languages(self):
        "Return a dictionary {textref: [languages],...}"
        return self._textrefs.copy()

    def textref_exists(self, textref):
        "Return True if the textref exists"
        return textref in self._textrefs

    def get_exact_text(self, textref, language):
        "Get text with given textref and language, gets exact value, does not seek nearest, if not found return None"
        if (textref,language) in self._textblocks:
            return self._textblocks[(textref,language)]

    def get_text(self, textref, lang):
        """Gets the text from the textblock, trying nearest language, returns None if not found
           lang is a tuple of preferred language, default_language"""
        if textref not in self._textrefs:
            return
        language, default_language = lang
        language = language.lower()
        default_language = default_language.lower()
        # try preferred language
        if (textref,language) in self._textblocks:
            return self.get_exact_text(textref,language)
        # if not preferred for example en-gb, try en
        shortlang = language.split('-')
        if (textref,shortlang[0]) in self._textblocks:
            return self.get_exact_text(textref,shortlang[0])
        # try default language
        if (textref,default_language) in self._textblocks:
            return self.get_exact_text(textref,default_language)
        shortlang = default_language.split('-')
        if (textref,shortlang[0]) in self._textblocks:
            return self.get_exact_text(textref,shortlang[0])
        # try self.default_language
        if (textref,self.default_language) in self._textblocks:
            return self.get_exact_text(textref,self.default_language)
        shortlang = self.default_language.split('-')
        if (textref,shortlang[0]) in self._textblocks:
            return self.get_exact_text(textref,shortlang[0])
        # try whatever language remains
        rlang = self.textrefs[textref][0]
        return self.get_exact_text(textref,rlang)

    def set_text(self, text, textref, language):
        """Sets the text into the textblock, with the given textref and language
           Used by skiadmin, in this implementation it is put into memory but
           not saved to the json files until the save method is called when the project
           is committed"""
        language = language.lower()
        if not text:
            self.del_text(textref, language)
            return
        self._textblocks[textref, language] = text
        self._languages.update([language])
        if textref in self._textrefs:
            langlist = self._textrefs[textref]
            if language not in langlist:
                langlist.append(language)
                langlist.sort()
        else:
            self._textrefs[textref] = [language]
        # if the language is of the format 'en-gb' then check if en is present, if not, add it
        shortlang = language.split('-')
        if shortlang[0] == language:
            return
        if (textref, shortlang) in self._textblocks:
            # A textblock with the given shortlang does exist, but check to see if it is just an empty string
            shortlangtext = self._textblocks[(textref, shortlang)]
            if (not shortlangtext) or (shortlangtext == " "):
                # add text
                self.set_text(text, textref, shortlang)
        else:
            # shortlang does not exist, so add it
            self.set_text(text, textref, shortlang)

    def del_text(self, textref, language):
        "Deletes the text from the textblock with the given language"
        language = language.lower()
        if (textref,language) not in self._textblocks:
            return
        del self._textblocks[(textref,language)]
        langlist = self._textrefs[textref]
        try:
            pos = langlist.index(language)
            del langlist[pos]
            if not langlist:
                del self._textrefs[textref]
        except Exception:
            pass
        # test if language used anywhere
        for langlist in self._textrefs.values():
            if language in langlist:
                break
        else:
            self._languages.discard(language)

    def del_textblock(self, textref):
        "Deletes the textblock, all languages"
        langlist = self._textrefs[textref].copy()
        for language in langlist:
            self.del_text(textref, language)

    def copy(self, sourceref, destinationref):
        "Copies textblock"
        langlist = self._textrefs[sourceref]
        self._textrefs[destinationref] = []
        destlanglist = self._textrefs[destinationref]
        for language in langlist:
            self._textblocks[(destinationref, language)] = self._textblocks[(sourceref, language)]
            destlanglist.append(language)

    def save(self):
        "Creates json files from the textblocks"
        if os.path.isdir(self._textblocks_json_directory):
            # remove existing json files
            shutil.rmtree(self._textblocks_json_directory)
        os.mkdir(self._textblocks_json_directory)
        for language in self._languages:
            filepath = os.path.join(self._textblocks_json_directory, language + '.json')
            lang = (language, self.default_language)
            json_dict = {}
            for textref, langlist in self._textrefs.items():
                if language not in langlist:
                    continue
                json_dict[textref] = ''
                text = self.get_text(textref, lang)
                if text is not None:
                    json_dict[textref] = text
            # save the json dictionary to file
            with open(filepath, 'w') as fp:
                json.dump(json_dict, fp, indent=2, sort_keys=True)


